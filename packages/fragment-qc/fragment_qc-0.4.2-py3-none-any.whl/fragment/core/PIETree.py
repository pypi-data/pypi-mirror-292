#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from itertools import combinations, product
from typing import Any, Dict, Iterable, Iterator, Optional, Tuple

import networkx as nx
from scipy.special import comb

from fragment.core.legacy_PIETree import UnrepresentableException
from fragment.core.PIE_common import ROOT
from fragment.core.quickPIE import (
    add_cd,
    collect_primatives,
    quickNode,
    quickNodeList,
    quickNodeSet,
    quickPlan,
    roots_overlap,
)


def get_order(data: quickNode, parents: Iterable[quickNode]) -> int:
    return sum((1 for p in parents if p.issubset(data)))


def tree_equal(t1: nx.DiGraph, t2: nx.DiGraph, check_coefs=False, debug=False) -> bool:
    def nm(d1: Dict, d2: Dict) -> bool:
        if check_coefs and d1.get("coef", -999) != d2.get("coef", -999):
            return False
        if d1.get("data", frozenset()) != d2.get("data", frozenset()):
            return False
        return True

    same = nx.is_isomorphic(t1, t2, node_match=nm)

    if not same and debug:
        # DEBUGGING CODE: Prints differences
        t1_nodes = {(n, d.get("coef", None)) for n, d in t1.nodes(data=True)}
        t2_nodes = {(n, d.get("coef", None)) for n, d in t2.nodes(data=True)}
        t1_edges = set(t1.edges)
        t2_edges = set(t2.edges)

        dn_m = set.difference(t1_nodes, t2_nodes)
        dn_e = set.difference(t2_nodes, t1_nodes)
        de_m = set.difference(t1_edges, t2_edges)
        de_e = set.difference(t2_edges, t1_edges)

        print("Missing nodes: ", dn_m)
        print("Extra nodes: ", dn_e)
        print("Missing edges: ", de_m)
        print("Extra edges: ", de_e)

    return same


class PIETree:
    tree: nx.DiGraph  # Keys are quickNodes
    primaries: quickNodeSet  # Smallest blocks which may overlap
    primatives: quickNodeSet  # Smallest blocks of the fragmentation
    target: quickNode  # Target this tree should reproduce

    def __init__(
        self,
        tree: nx.DiGraph,
        primatives: quickNodeSet,
        primaries: quickNodeSet,
        target: quickNode,
    ) -> None:
        self.tree = tree
        self.primatives = primatives
        self.primaries = primaries
        self.target = target

    def __iter__(self) -> Iterator[Tuple[quickNode, Dict]]:
        return (i for i in self.tree.nodes(data=True) if i[0] != ROOT)

    def __getitem__(self, k: quickNode) -> Dict:
        return self.tree.nodes[k]

    def __contains__(self, item: Any) -> bool:
        return self.tree.__contains__(item)

    @classmethod
    def empty_tree(cls) -> "PIETree":
        return cls(cls.new_tree(), set(), set(), frozenset())

    @classmethod
    def from_primatives(
        cls, primatives: quickNodeSet, primaries: Optional[quickNodeList] = None
    ) -> "PIETree":
        tree = cls(
            cls.new_tree(),
            primatives,
            set(primaries) if primaries else primatives,
            frozenset.union(*primatives),
        )

        for p in primatives:
            k_p = tree.new_node(p, 0)
            tree.tree.add_edge(ROOT, k_p)

        return tree

    @classmethod
    def from_primaries(
        cls, primaries: quickNodeList, add=False, add_coef=1
    ) -> "PIETree":
        primatives = collect_primatives(primaries)
        tree = cls.from_primatives(primatives, primaries)

        if add:
            for p in primaries:
                try:
                    tree.expand(p, add_coef)
                except AttributeError:
                    pass
        return tree

    @classmethod
    def from_roots(
        cls, roots: quickNodeList, primatives: Optional[quickNodeSet] = None
    ) -> "PIETree":
        _primatives = collect_primatives(roots) if primatives is None else primatives
        tree = cls.from_primatives(_primatives)
        for r in roots:
            tree.expand(r)
        return tree

    @classmethod
    def from_MBE_primary_frags(cls, primaries: quickNodeList, order: int) -> "PIETree":
        if not primaries:
            raise ValueError("Primaries cannot be empty")

        target = frozenset.union(*primaries)
        if not target:
            raise ValueError(f"View cannot be created for empty system:\n{primaries}")

        if roots_overlap(primaries):
            raise Exception("Cannot perform MBE with overlapping fragments (yet).")

        tree = cls.from_primaries(primaries)

        if len(primaries) <= order:
            k = tree.new_node(target, 1)
            tree.link_node(k)
        else:
            tree.add_MBE_levels(primaries, order)
            # Modify the tree edges reflect reality
            for p in primaries:
                tree.tree.remove_edge(ROOT, p)

        for prims in combinations(primaries, order):
            tree.tree.add_edge(ROOT, frozenset.union(*prims))

        return tree

    def add_MBE_levels(self, primaries: quickNodeList, order: int, m: int = 0):
        N = len(primaries)
        coef = comb(N - order - 1 + m, m) * (-1) ** m
        make_links = m < order - 1

        # Add lower levels first so we can efficiently link to them
        if make_links:
            self.add_MBE_levels(primaries, order, m + 1)

        # Add the proper number of coefficients to the node dict
        for prims in combinations(primaries, order - m):
            frag = frozenset.union(*prims)
            k = self.new_node(frag, int(coef))

            if make_links:
                for children in combinations(prims, len(prims) - 1):
                    ck = frozenset.union(*children)
                    self.tree.add_edge(k, ck)

    @classmethod
    def from_quickPlan(
        cls, plan: quickPlan, primaries: Optional[quickNodeList] = None
    ) -> "PIETree":
        _primaries: quickNodeSet

        if primaries:
            primatives = collect_primatives(list(primaries))
        else:
            # Much more expensive!
            primatives = collect_primatives(list(plan.keys()))
        tree = cls.from_primatives(primatives, primaries)
        for n, c in plan.items():
            tree.new_node(n, c)
            tree.link_node(n)
        return tree

    @classmethod
    def brute_force(cls, nodes: quickNodeList) -> "PIETree":
        primatives = collect_primatives(nodes)
        tree = cls(cls.new_tree(), primatives, primatives, frozenset.union(*nodes))

        for n in nodes + [frozenset(p) for p in primatives]:
            # Quick and dirty node addition
            tree.new_node(n, 0)

        # Add cross linkages to ALL nodes (SLOW)
        for a, b in combinations(tree.tree, 2):
            if a == ROOT or b == ROOT:
                continue
            a_d = tree.tree.nodes[a]
            b_d = tree.tree.nodes[b]

            if a_d["data"].issuperset(b_d["data"]):
                tree.tree.add_edge(a, b)
                continue
            elif a_d["data"].issubset(b_d["data"]):
                tree.tree.add_edge(b, a)

        # Link to root
        for k in tree.tree:
            if k == ROOT:
                continue
            if not tree.tree.in_degree(k):
                tree.tree.add_edge(ROOT, k)

        for k in tree.tree.successors(ROOT):
            tree._brute_force_remove_edges(k)

        return tree

    def _brute_force_remove_edges(self, k: quickNode) -> None:
        for a, b in combinations(self.tree.successors(k), 2):
            a_d = self[a]
            b_d = self[b]

            if a_d["data"].issuperset(b_d["data"]):
                try:
                    self.tree.remove_edge(k, b)
                except nx.NetworkXError:
                    pass
                continue
            elif a_d["data"].issubset(b_d["data"]):
                try:
                    self.tree.remove_edge(k, a)
                except nx.NetworkXError:
                    pass

        for n in self.tree.successors(k):
            self._brute_force_remove_edges(n)

    # CONSTRUCTION METHODS
    @staticmethod
    def new_tree() -> nx.DiGraph:
        tree = nx.DiGraph()
        tree.add_node(ROOT)
        return tree

    def new_node(self, data: quickNode, coef: int) -> quickNode:
        """Optimized type-stable new node"""
        self.tree.add_node(
            data,
            data=data,
            coef=coef,
            primative_order=get_order(data, self.primatives),
            primary_order=get_order(data, self.primaries),
        )
        return data

    def new_annotated_node(self, data: quickNode, coef: int, **kwargs) -> quickNode:
        self.tree.add_node(
            data,
            data=data,
            coef=coef,
            primative_order=get_order(data, self.primatives),
            primary_order=get_order(data, self.primaries),
            **kwargs,
        )
        return data

    def update_or_add(self, n: quickNode, coef: int) -> None:
        try:
            self[n]["coef"] += coef
        except KeyError:
            self.new_node(n, coef)
            self.link_node(n)

    # QUERY METHODS

    ################# FIND CHILDREN #################
    def find_children(self, key: quickNode) -> quickNodeSet:
        """FOR USE WITH KEY NOT IN TREE

        Returns a list of nodes which *should* be the parents of `key`
        """
        children: quickNodeSet = set()
        visited: quickNodeSet = set()

        for n in self.primatives:
            self._find_children(n, key, children, visited)

        return children

    def _find_children(
        self, n: quickNode, d: quickNode, children: quickNodeSet, visited: quickNodeSet
    ) -> bool:
        """Adds child node keys to children

        Args:
            tree (nx.DiGraph): PIETree to parse
            n (quickNode): starting node in tree
            d (quickNode): data to compair all nodes againse
            children (quickNodeSet): Set in which to populate with all child nodes
            visited (quickNodeSet): All visited subsets of d

        Returns:
            bool: True if `n` is is subset of d
        """
        if n == ROOT:
            # ROOT is never a child of d
            return False

        if not n.issubset(d):
            # If this node isn't a subset of d, just move on
            return False

        if n in visited:
            # We've calculated all the decendents for this node
            # It is a subset
            return True
        visited.add(n)

        is_child = True
        for parent in self.tree.predecessors(n):
            if self._find_children(parent, d, children, visited):
                is_child = False

        if is_child:
            children.add(n)
        return True  # This is a subset of d

    ################# FIND PARENTS #################
    def find_parents(self, key: quickNode, start: quickNodeSet) -> quickNodeSet:
        parents: quickNodeSet = set()
        visited: quickNodeSet = set()

        # Assumes start are all children of `key`
        for k in start:
            self._find_parents(k, key, visited, parents)

        return parents

    def _find_parents(
        self, n: quickNode, d: quickNode, visited: quickNodeSet, parents: quickNodeSet
    ) -> None:
        if n in visited:
            return
        visited.add(n)

        for p in self.tree.predecessors(n):
            if p == ROOT:
                return  # If it hits root, it's definitly TL
            if p.issuperset(d):
                add_cd(parents, p)
                self._visit_all_pred(p, visited)
                continue
            self._find_parents(p, d, visited, parents)

    def _visit_all_pred(self, n: quickNode, visited: quickNodeSet):
        if n in visited:
            return
        visited.add(n)

        for p in self.tree.predecessors(n):
            self._visit_all_pred(p, visited)

    def accessable_from(
        self, n: quickNode, accessable: Optional[quickNodeSet] = None
    ) -> quickNodeSet:
        _accessable = set() if accessable is None else accessable

        for c in self.tree.successors(n):
            # We don't visit it or it's already visited
            if c in _accessable:
                continue
            _accessable.add(c)
            self.accessable_from(c, accessable=_accessable)
        return _accessable

    # BUILDING METHODS
    def remove_node(self, n: quickNode):
        # Get a list of accessable children
        children = set(self.tree.successors(n))
        parents = set(self.tree.predecessors(n))
        self.tree.remove_node(n)
        for p in parents:
            accessable_children = self.accessable_from(p)
            for c in children:
                if c in accessable_children:
                    continue
                self.tree.add_edge(p, c)

    def link_node(self, key: quickNode) -> None:
        if self.tree.degree(key):
            raise AttributeError(f"Node {key} is already linked")

        children = self.find_children(key)
        parents = self.find_parents(key, children)

        self._link_node(key, parents, children)

    def _link_node(
        self, key: quickNode, parents: quickNodeSet, children: quickNodeSet
    ) -> None:
        if not parents:  # If there are not parents,
            parents = {ROOT}  # TODO: Change root to full set

        self.tree.remove_edges_from(((p, c) for p, c in product(parents, children)))
        self.tree.add_edges_from(((p, key) for p in parents))
        self.tree.add_edges_from(((key, c) for c in children))

    def expand(self, n: quickNode, coef: int = 1):
        changes: Dict[quickNode, int] = {n: coef}
        visited: quickNodeSet = set()
        addable: bool = False

        for p in self.primatives:
            if not p.issubset(n):
                continue
            addable = True
            self._overlap_node(n, p, visited, changes)

        if not addable:
            raise AttributeError(f"Node {n} is not a superset of any primatives")

        # DEBUGGING: This snippet brute forces the overlap between the new
        # node and the tree-optimized overlap to make sure we are not
        # missing any nodes
        # should_visit: quickNodeSet = set()
        # should_add: quickPlan = dict()
        # for _n, _n_d in self.tree.nodes(data=True):
        #     if _n == ROOT:
        #         continue
        #     inter = n.intersection(_n)
        #     if inter:
        #         should_visit.add(_n)
        #         try:
        #             should_add[inter] += -_n_d["coef"]
        #         except KeyError:
        #             should_add[inter] = -_n_d["coef"]
        # print("SHOULD VISIT:", should_visit.difference(visited))

        # for v in visited:
        #     self.tree.nodes[v]["style"] = "filled"
        # for sv in should_visit:
        #     self.tree.nodes[sv]["color"] = "green"

        # if should_visit.difference(visited):
        #     raise Exception("Not all nodes were visited!")

        # Always add the expanding node
        self.update_or_add(n, changes[n])
        del changes[n]

        # Update all other nodes
        for c_k, _c_coef in changes.items():
            c_coef = _c_coef * coef
            if not self.skip_add(c_k, c_coef):
                self.update_or_add(c_k, c_coef)

            # DEBUGGING: See that each addition is being done correctly
            # ref_tree = brute_force_tree((k for k in tree if k != ROOT))
            # if not nx.is_isomorphic(tree, ref_tree):
            #     print(f"There was an error adding {c_k}")
            #     print({k for k in tree if k != ROOT})
            #     nx.nx_pydot.write_dot(tree, "ta.dot")
            #     nx.nx_pydot.write_dot(ref_tree, "tr.dot")
            #     exit()

        # DEBUGGING: Ensures that the final tree represents the target
        # valid_atoms = frozenset.union(
        #     *(k for k in self.tree.successors(ROOT) if k not in self.primatives)
        # )
        # for a, c in self.count_members().items():
        #     if a not in valid_atoms:
        #         continue
        #     if c != 1:
        #         print("Adding", n, "fucked shit up")
        #         print(self.count_members())
        #         print({k for k in self.tree if k != ROOT})
        #         exit()

    def skip_add(self, k: quickNode, coef: int) -> bool:
        """Determines if a given node should be added to the tree

        ..note::
            Misuse of this function may cause trees to be unballance. The intened use for this feature is to prevent the creation of fragments consisting only
            of ghost atoms and other non-physical atoms which are often used to
            augment fragments.
        """
        return coef == 0

    def _overlap_node(
        self,
        new: quickNode,
        existing: quickNode,
        visited: quickNodeSet,
        changes: Dict[quickNode, int],
    ):
        if existing == ROOT:
            return
        if existing in visited:
            return
        visited.add(existing)

        n_coef = -self[existing]["coef"]
        if n_coef:
            child_key = frozenset.intersection(new, existing)
            try:
                changes[child_key] += n_coef
            except KeyError:
                changes[child_key] = n_coef

        for pred in self.tree.predecessors(existing):
            self._overlap_node(new, pred, visited, changes)

    def clean_zeros(self):
        """Remove nodes where the coef == 0"""
        zeros: quickNodeSet = set()

        for n, d in self:
            if d["coef"] == 0:
                zeros.add(n)

        for z in zeros:
            self.remove_node(z)

    def update_target(self):
        self.target = {k for k in self.count_members().keys()}

    # General Usage Methods

    def child_equivalent(self, k: quickNode) -> "PIETree":
        """
        Returns a PIETree tree that is equivalent to one instance of k
        """

        successors = list(self.tree.successors(k))
        successor_data = (
            frozenset.union(*successors) if len(successors) else frozenset()
        )

        if successor_data != k:
            raise UnrepresentableException(
                f"Node {k} connot be represented by children"
            )

        return self.__class__.from_roots(successors)

    def replace_with_children(
        self, k: quickNode, children: Optional["PIETree"] = None
    ) -> None:
        """
        Replaces node `k` with it's equivalent child representation

        If children is not provided, this will be generated using
        `child_equivalent`. There is no checking on the value of `children`.
        """

        if children is None:
            children = self.child_equivalent(k)

        pd = self[k]
        parent_coef = pd["coef"]

        if parent_coef == 0:
            return

        pd["coef"] = 0

        for ck, cd in children:
            # TODO: Automatically add non-existant nodes to tree
            self[ck]["coef"] += cd["coef"] * parent_coef

    # VALIDATION METHODS

    def count_members(self) -> Dict[int, int]:
        counts: Dict[int, int] = {}
        coef_key = "coef"
        for _, d in self:
            for i in d["data"]:
                try:
                    counts[i] += d[coef_key]
                except KeyError:
                    counts[i] = d[coef_key]
        return counts

    def is_complete(self) -> bool:
        counts = self.count_members()
        for c in counts.values():
            if c != 1:
                return False

        if self.target != {s for s in counts.keys()}:
            return False

        return True

    @staticmethod
    def is_equal(t1: "PIETree", t2: "PIETree", check_coef=False, debug=False) -> bool:
        return tree_equal(t1.tree, t2.tree, check_coefs=check_coef, debug=debug)
