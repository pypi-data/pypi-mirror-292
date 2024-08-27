#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from itertools import combinations, compress
from typing import Dict, FrozenSet, Iterable, List, Set

quickNode = FrozenSet[int]
quickNodeList = List[quickNode]
quickNodeSet = Set[quickNode]
quickPlan = Dict[quickNode, int]


def mk_quickNode(k: Iterable[int]) -> quickNode:
    return frozenset(k)


def merge_coefs(d: quickPlan, n: quickNode, c: int) -> None:
    """Add coef or create node in Plan"""
    try:
        d[n] += c
    except KeyError:
        d[n] = c


def compress_up(roots: quickNodeList) -> Iterable[quickNode]:
    """If any set in `roots` is a subset of another, it is eliminated"""
    keep = [True for _ in range(len(roots))]

    for (i1, r1), (i2, r2) in combinations(enumerate(roots), 2):
        if r1.issuperset(r2):
            keep[i2] = False
            continue
        if r1.issubset(r2):
            keep[i1] = False

    return compress(roots, keep)


def compress_down(roots: quickNodeList) -> Iterable[quickNode]:
    """If any set in `roots` is a superset of another, it is eliminated"""
    keep = [True for _ in range(len(roots))]

    for (i1, r1), (i2, r2) in combinations(enumerate(roots), 2):
        if r1.issuperset(r2):
            keep[i1] = False
            continue
        if r1.issubset(r2):
            keep[i2] = False

    return compress(roots, keep)


def add_cd(s: quickNodeSet, n: quickNode) -> None:
    """Add and compress down"""
    remove: quickNodeSet = set()
    for _n in s:
        if _n.issubset(n):
            return  # Don't add it. Something better exists
        if _n.issuperset(n):
            remove.add(_n)
    s.difference_update(remove)
    s.add(n)


def add_cu(s: quickNodeSet, n: quickNode) -> None:
    """Add and compress up"""
    remove: quickNodeSet = set()
    for _n in s:
        if _n.issuperset(n):
            return  # Don't add it. Something better exists
        if _n.issubset(n):
            remove.add(_n)
    s.difference_update(remove)
    s.add(n)


def collect_primatives(primary_nodes: quickNodeList) -> quickNodeSet:
    if not primary_nodes:
        return set()

    keep = [True for _ in primary_nodes]
    overlaps: quickNodeSet = set()  # Stored compressed to reduce memory reqs.

    for (i1, p1), (i2, p2) in combinations(enumerate(primary_nodes), 2):
        inter = frozenset.intersection(p1, p2)
        if inter:
            d1 = p1.difference(inter)
            if d1:
                keep[i1] = False
                overlaps.add(d1)

            d2 = p2.difference(inter)
            if d2:
                keep[i2] = False
                overlaps.add(d2)

            # If there was an overlap on both sides, we'd better keep it
            if (not keep[i1]) and (not keep[i2]):
                overlaps.add(inter)

    return set.union(
        {i for i in compress(primary_nodes, keep)},
        collect_primatives(list(overlaps)),
    )


def roots_overlap(roots: quickNodeList) -> bool:
    for f1, f2 in combinations(roots, 2):
        if frozenset.intersection(f1, f2):
            return True
    return False


def add(d: quickPlan, new: quickNode) -> None:
    """Add a root node to a quickPlan"""
    if new in d:
        return

    new_nodes: quickPlan = {}

    for _n, _c in d.items():
        if _c == 0:
            continue

        i = frozenset.intersection(new, _n)

        # Don't add empty sets
        if not i:
            continue
        merge_coefs(new_nodes, i, -_c)

    # Merge in new nodes
    for _n, _c in new_nodes.items():
        merge_coefs(d, _n, _c)
    merge_coefs(d, new, 1)


def mk_quickPlan(roots: Iterable[quickNode]) -> quickPlan:
    """Add iterable of quick nodes"""
    d: quickPlan = {}
    for r in compress_up(list(roots)):
        add(d, r)
    return d


def mk_quickPlan_dirty(roots: Iterable[quickNode]) -> quickPlan:
    """Add iterable of quick nodes with no checks that it exists.
    This can be faster for smaller sets of nodes
    """
    d: quickPlan = {}
    for r in roots:
        add(d, r)
    return d


def check_plan(plan: quickPlan) -> None:
    """
    Checks for duplicates and empty nodes
    TODO: make report more accessable
    """
    counts = {}
    for n, c in plan.items():
        assert n  # Should not be an empty set!
        for k in n:
            try:
                counts[k] += c
            except KeyError:
                counts[k] = c
    print(counts)
    for c in counts.values():
        assert c == 1
