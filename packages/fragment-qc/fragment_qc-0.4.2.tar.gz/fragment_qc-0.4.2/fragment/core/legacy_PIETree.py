#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#

# Converts PIE Solver result to a handy-dandy tree!
# Conventient for all you fragment-calculation needs

from itertools import permutations
from typing import List, Set, Tuple

import networkx as nx

from fragment.core.legacy_PIE import PIEPlan, mk_key
from fragment.core.PIE_common import NDList, get_order

# EDGE TYPES
PARENT_CHILD = 1
DEPENDS_ON = 2

ROOT = 0

Key = Tuple[int, ...]


class PIETreeException(Exception):
    pass


class UnrepresentableException(PIETreeException):
    pass


class TreeIncomplete(PIETreeException):
    pass


def make_PIETree(plan: PIEPlan, parents: NDList, remove_zeros=True) -> nx.DiGraph:
    G = nx.DiGraph()
    G.add_node(0)
    add_aux_nodes(G, plan, parents, remove_zeros)
    add_aux_edges(G, plan)

    # This does not work as expected
    if nx.number_of_isolates(G) != 0:
        raise TreeIncomplete("Graph contains isolated nodes")
    return G


def add_aux_nodes(G: nx.DiGraph, plan: PIEPlan, parents: NDList, remove_zeros=True):
    # Add aux nodes
    for node in plan.nodes.values():
        if remove_zeros and node.coef == 0:
            continue

        G.add_node(
            node.key,
            data=node.data,
            order=get_order(node.data, parents),
            coef=node.coef,
        )


def add_aux_edges(G: nx.DiGraph, plan: PIEPlan):
    root_nodes = []
    for root_set in plan.roots:
        root_node = plan.nodes[mk_key(root_set)]
        if root_node.coef == 0:
            continue
        root_nodes.append((root_node.key, root_node.data, []))

    for node, d in G.nodes(data=True):
        if node == ROOT:
            continue
        for rkey, rdata, candidates in root_nodes:
            if node != rkey and d["data"].issubset(rdata):
                candidates.append(node)

    for rkey, rdata, candidates in root_nodes:
        gather_children(G, rkey, candidates)
        if G.in_degree(rkey) == 0:
            G.add_edge(ROOT, rkey, type=DEPENDS_ON)


def gather_children(G: nx.DiGraph, key: Key, candidates: List[Key]) -> List[bool]:
    data = set(key)

    # Extract all children of this node
    children: Tuple[List[int], int] = []
    for c in candidates:
        if key == c:
            continue
        c_data = G.nodes[c]["data"]
        if c_data.issubset(data):
            children.append([c, True])  # Mark the child as indirect

    # Separate children which are subsets of other children
    # and ones which are independent
    for c, o in permutations(children, 2):
        if (not c[1]) or (not o[1]):  # c has been claimed by someone else
            continue  # or other has already been maked

        c_data = G.nodes[c[0]]
        o_data = G.nodes[o[0]]
        if c_data["data"].issubset(o_data["data"]):
            c[1] = False

    for n, is_direct in children:
        if not is_direct:
            continue
        G.add_edge(key, n, type=DEPENDS_ON)
        gather_children(G, n, (c for c, _is_d in children if not _is_d))


def zero_node(G: nx.DiGraph, n: Key):
    """Set the coefficient for node `n` to zero without changing the over-all
    representation of the tree

    Args:
        G (nx.DiGraph): The PIETree to trim node
        n (Key): The node to zero out
    """
    equ = child_eq_coefs(G, n)
    parent_coef = G.nodes[n]["coef"]
    _reduce(G, n, parent_coef)
    for c, coef in equ:
        _reduce(G, c, -coef * parent_coef)


def substitute_node(G: nx.DiGraph, n: Key):
    equ = child_eq_coefs(G, n)
    parent_coef = G.nodes[n]["coef"]
    for c, coef in equ:
        _reduce(G, c, -coef * parent_coef)
        for p, _ in G.in_edges(n):
            G.add_edge(p, c)

    # Finally remove that node
    G.remove_node(n)


def _reduce(G: nx.DiGraph, n, coef):
    G.nodes[n]["coef"] -= coef


def child_eq_coefs(G: nx.DiGraph, n: Key) -> List[Tuple[Key, int]]:
    child_roots = [set(e[1]) for e in G.out_edges(n)]
    plan = PIEPlan(child_roots)  # Get the equivalent of this node
    if plan.superset != set(n):
        raise UnrepresentableException(
            f"Node {n} does not have a complete set of children."
        )
    return [(n.key, n.coef) for n in plan.nodes.values() if n.coef != 0]


def child_eq(G: nx.DiGraph, n: Key) -> nx.DiGraph:
    """Get an equivalent node in terms of the child nodes

    Args:
        G (nx.DiGraph): PIETree
        n (Key): Node to be replaces

    Returns:
        DiGraph: subgraph of equivalent to `n`
    """
    ce = child_eq_coefs(G, n)
    tree = G.subgraph((n for n, _ in ce)).copy()

    # Update the copy's coef
    for n, coef in ce:
        if n.coef == 0:
            continue
        tree.nodes[n]["coef"] = coef
    return tree


def rm_zeros(G: nx.DiGraph):
    """Removes node with coef==0

    .. warning:: This does not reconcile the tree to use children
    """
    _rm = [n for n, d in G.nodes(data=True) if n != ROOT and d["coef"] == 0]
    G.remove_nodes_from(_rm)


def prune_false_roots(G: nx.DiGraph):
    parentless = (n for n, d in G.in_degree if n != ROOT and d == 0)
    count = 0
    for n in parentless:
        count += 1
        zero_node(G, n)
    if count == 0:
        return  # End recursion
    rm_zeros(G)
    prune_false_roots(G)


def superset(G: nx.DiGraph) -> Set[int]:
    ss = set()
    for n in G.neighbors(ROOT):
        ss.update(G.nodes[n]["data"])
    return ss
