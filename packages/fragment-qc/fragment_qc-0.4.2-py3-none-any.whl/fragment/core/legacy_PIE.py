#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from itertools import combinations

from scipy.special import comb

from .PIE_common import Key, NDList, NodeData, merge_data


def mk_key(data: NodeData) -> Key:
    return tuple(sorted(data))


class Node(object):
    def __init__(self, data, coef=1):
        self.data = data
        self.key = mk_key(data)
        self._coef = coef
        self._new_coef = coef

    @property
    def coef(self):
        return self._coef

    @coef.setter
    def setter(self, val):
        raise Exception("Coef must be altered by the add_to_coef ... apply cycle")

    def set_coef(self, val):
        self._new_coef = val

    def add_to_coef(self, val):
        self._new_coef += val

    def apply_coef(self):
        self._coef = self._new_coef

    @property
    def value(self):
        return sum(self.data) * self.coef

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(data={self.data}, coef={self.coef})"


class NodeDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_session = False

    def add_node(self, data: NodeData, coef: int):
        if not self.active_session:
            raise Exception("A session must be active to alter NodeDict")

        k = mk_key(data)
        try:
            self._add_existing(self, k, coef)
            return
        except KeyError:
            pass

        try:
            self._add_existing(self.new_nodes, k, coef)
            return
        except KeyError:
            pass

        self.new_nodes[k] = Node(data, coef)

    @staticmethod
    def _add_existing(d: dict, k: Key, coef: int):
        existing_node = d[k]
        existing_node.add_to_coef(coef)

    def start_session(self):
        if self.active_session:
            raise Exception("Session already in progress")
        self.new_nodes = dict()
        self.active_session = True

    def close_session(self):
        if not self.active_session:
            raise Exception("No active session")
        self.active_session = False

        # Merge in changes
        for n in self.new_nodes.values():
            self._merge_node(n)

        # Add
        for n in self.values():
            n.apply_coef()

    def _merge_node(self, node: Node):
        """
        Given a node, adds new node to self or merges existing node
        """
        # Apply and flush all changes
        node.apply_coef()

        try:
            existing_node: Node = self[node.key]
        except KeyError:
            self[node.key] = node
        else:
            existing_node.add_to_coef(node.coef)
            existing_node.apply_coef()

    def __enter__(self):
        self.start_session()

    def __exit__(self, t, v, trace):
        self.close_session()


class PIEPlan(object):
    """
    Assesses principle of inclusion/exclusion for a given sets of
    nodes and performs deduplication
    """

    nodes: NodeDict
    roots: NDList

    def __init__(
        self,
        roots: NDList = None,
    ) -> None:
        self.roots = []
        self.nodes = NodeDict()

        new_roots = roots or []

        for n in new_roots:
            self.add_node(n)

    @classmethod
    def from_MBE_primary_frags(cls, p_frags: NDList, order: int):
        # Double check that there are no overlaps
        for f1, f2 in combinations(p_frags, 2):
            if set.intersection(f1, f2):
                raise Exception("Cannot perform MBE with overlapping fragments (yet).")

        plan = cls()
        plan.add_MBE_levels(p_frags, order)
        return plan

    def add_MBE_levels(self, p_frags: NDList, order: int, m: int = 0):
        N = len(p_frags)
        coef = comb(N - order - 1 + m, m) * (-1) ** m
        # Add the proper number of coefficients to the node dict
        with self.nodes:
            for frags in combinations(enumerate(p_frags), order - m):
                frag = set.union(*(f[1] for f in frags))
                self.nodes.add_node(frag, coef)
                if m == 0:
                    self.roots.append(frag)

        if m < order - 1:
            self.add_MBE_levels(p_frags, order, m + 1)

    def add_node(self, new_node: NodeData, new_coef=1, force=False) -> None:
        # Check the primary layer.
        # If the new node is a subset of a primary node, do nothing

        if not force:
            for node in self.roots:
                if new_node.issubset(node):
                    return

        # Now add the node to our PIE plan
        with self.nodes:
            for node in self.nodes.values():
                # Empty nodes need not apply
                if node.coef == 0:
                    continue

                overlap = set.intersection(new_node, node.data)
                if not overlap:
                    continue

                coef = -node.coef * new_coef
                self.nodes.add_node(overlap, coef)

            self.nodes.add_node(new_node, new_coef)
        self.roots.append(new_node)

    @property
    def total(self):
        return sum(n.value for n in self.nodes.values())

    @property
    def size(self):
        s = 0
        for n in self.nodes.values():
            if n.coef != 0:
                s += 1
        return s

    @property
    def unconsolidated_size(self):
        return sum(abs(n.coef) for n in self.nodes.values())

    @property
    def superset(self):
        return merge_data(*self.roots)

    def check_nodes(self):
        """
        Checks for duplicates and empty nodes
        TODO: make report more accessable
        """
        dups = 0
        for n in self.nodes:
            assert n.coef != 0
            assert n.data
        for n1, n2 in combinations(self.nodes, 2):
            if n1.data == n2.data:  # and f1.coef + f2.coef == 0:
                print(
                    "  Duplicates! o{}c{} + o{}c{} = {} ({})".format(
                        n1.order,
                        n1.coef,
                        n2.order,
                        n2.coef,
                        n1.coef + n2.coef,
                        n1.value + n2.value,
                    )
                )
                dups += 1
        assert dups == 0, dups
