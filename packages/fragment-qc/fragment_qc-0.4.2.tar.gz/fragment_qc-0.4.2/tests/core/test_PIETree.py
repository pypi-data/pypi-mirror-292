#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import gc
import unittest
from itertools import combinations
from random import randint, seed
from time import process_time
from typing import List, Set

import networkx as nx
from scipy.special import comb

from fragment.core.legacy_PIE import PIEPlan, mk_key
from fragment.core.legacy_PIETree import Key, make_PIETree
from fragment.core.PIETree import ROOT, PIETree, collect_primatives, tree_equal
from fragment.core.quickPIE import compress_up, quickNode
from tests._util import QNList, QNSet

t1 = QNList({1}, {3}, {1, 2})
t2 = QNList({1}, {2}, {3}, {4}, {1, 2}, {2, 3}, {1, 3}, {1, 2, 3, 4})
t3 = QNList({1}, {2}, {1, 3}, {1, 4})
t4 = QNList({1, 2, 4}, {1}, {2}, {3}, {4})
t5 = QNList({1, 2, 3}, {1, 2, 4}, {1}, {2})
t6 = QNList({1, 2, 3}, {1}, {2})
t7 = QNList(
    {0, 1, 3, 4},
    {0, 1},
    {2},
    {0, 1, 4},
    {0, 1, 2},
    {0, 1, 3},
    {0, 1, 2, 4},
    {4},
    {1},
    {0, 2, 3, 4},
    {0, 1, 2, 3},
    {0},
    {3},
)
t8 = QNList({0, 1, 2, 3}, {0, 1, 2}, {0, 3}, {0}, {1})
t9 = QNList(
    {0, 5, 7, 9, 12, 14},
    {1, 3, 5, 6, 12, 14, 17, 18},
    {1, 3, 5, 6, 12, 14, 18},
    {0, 1, 5, 6, 7, 9, 12, 14, 18},
    {1, 3, 5, 6, 7, 12, 14, 17},
    {0, 3, 5, 7, 9, 12, 14, 17},
    {0, 1, 5, 6, 7, 9, 12, 14},
    {1, 3, 5, 6, 7, 12, 14, 20},
    {1, 3, 5, 6, 7, 12, 14, 17, 20},
    {5, 7, 12, 14},
    {1, 3, 5, 6, 12, 14},
    {3, 5, 7, 12, 14, 17, 20},
    {1, 5, 6, 7, 12, 14},
    {1, 3, 5, 6, 12, 14, 17},
    {0, 3, 5, 7, 9, 12, 14, 17, 20},
    {1, 3, 5, 6, 7, 12, 14},
    {3},
    {1, 3, 5, 6, 7, 12, 14, 18, 20},
    {3, 5, 7, 12, 14, 17},
    {0, 1, 3, 5, 6, 7, 9, 12, 14, 17},
    {1, 5, 6, 7, 12, 14, 18},
    {3},
    {5, 7, 12, 14},
    {20},
)

d1 = QNList({0}, {0, 1}, {0, 2}, {0, 1, 2})


class ConsolidateTestCases(unittest.TestCase):
    def test_primatives(self):
        primary_nodes = QNList({1, 2}, {2, 3})
        primatives = QNSet((1,), (2,), (3,))

        p1 = collect_primatives(primary_nodes)
        self.assertSetEqual(p1, primatives)

        # Case from fuzzing
        primary_nodes = QNList(
            {8, 18, 20, 13},
            {0, 6, 7},
            {1, 13, 17},
            {16, 17, 20, 1},
            {8, 17, 3},
            {0, 9, 12, 5},
            {1, 2, 12, 17},
            {8, 0, 13, 15},
            {2, 4, 6},
            {16, 1, 10, 9},
        )
        primatives = QNSet(
            (1,),
            (16,),
            (6,),
            (12,),
            (18,),
            (2,),
            (15,),
            (5,),
            (8,),
            (4,),
            (17,),
            (7,),
            (20,),
            (10,),
            (0,),
            (13,),
            (3,),
            (9,),
        )

        p2 = collect_primatives(primary_nodes)
        self.assertSetEqual(p2, primatives)

    def test_compress_up(self):
        roots = QNList({1, 2}, {2, 3}, {3})
        compressed = compress_up(roots)
        self.assertListEqual(list(compressed), QNList({1, 2}, {2, 3}))

        roots.reverse()
        compressed = compress_up(roots)
        self.assertListEqual(list(compressed), QNList({2, 3}, {1, 2}))


class TreeCreateTestCases(unittest.TestCase):
    def assertAdd(self, d: Set[int], t_ref: List[Set[int]]):
        _d = frozenset(d)
        _t_ref = QNList(*t_ref)
        t = PIETree.brute_force(_t_ref)

        children = t.find_children(_d)
        parents = t.find_parents(_d, children)

        # print(children)
        # print(parents)
        # nx.nx_pydot.write_dot(t.tree, "t1.dot")

        t.new_node(_d, 0)
        t.link_node(_d)
        # nx.nx_pydot.write_dot(t.tree, "t2.dot")

        ref = t.brute_force(_t_ref + [_d])
        # nx.nx_pydot.write_dot(ref.tree, "t3.dot")

        self.assertTrue(PIETree.is_equal(t, ref))
        return parents, children

    def assertRemove(self, d, t_ref: Set[Key]):
        _d = frozenset(d)
        _t_ref = QNList(*t_ref)

        t = PIETree.brute_force(_t_ref)
        # nx.nx_pydot.write_dot(t.tree, "t1.dot")

        t.remove_node(_d)
        # nx.nx_pydot.write_dot(t.tree, "t2.dot")

        ref = PIETree.brute_force([i for i in _t_ref if i != _d])
        # nx.nx_pydot.write_dot(ref.tree, "t3.dot")

        self.assertTrue(PIETree.is_equal(t, ref))

    def test_t1(self):
        parents, children = self.assertAdd({1, 2, 3}, t1)
        self.assertSetEqual(
            QNSet((1, 2), (3,)),
            children,
        )
        self.assertSetEqual(set(), parents)

    def test_t2(self):
        parents, children = self.assertAdd({1, 2, 3}, t2)
        self.assertSetEqual(
            QNSet((1, 2), (2, 3), (1, 3)),
            children,
        )
        self.assertSetEqual(
            QNSet((1, 2, 3, 4)),
            parents,
        )

    def test_t3(self):
        parents, children = self.assertAdd({1, 2}, t3)
        self.assertSetEqual(QNSet((1,), (2,)), children)
        self.assertSetEqual(set(), parents)

    def test_t4(self):
        parents, children = self.assertAdd({1, 2, 3}, t4)
        self.assertSetEqual(QNSet((1,), (2,), (3,)), children)
        self.assertSetEqual(set(), parents)

    def test_t5(self):
        parents, children = self.assertAdd({1, 2}, t5)
        self.assertSetEqual(QNSet((1,), (2,)), children)
        self.assertSetEqual(QNSet((1, 2, 3), (1, 2, 4)), parents)

    def test_t6(self):
        parents, children = self.assertAdd({1, 2}, t6)
        self.assertSetEqual(QNSet((1,), (2,)), children)
        self.assertSetEqual(QNSet((1, 2, 3)), parents)

    def test_t7(self):
        parents, children = self.assertAdd({0, 2}, t7)
        self.assertSetEqual(QNSet((0,), (2,)), children)
        self.assertSetEqual(QNSet((0, 1, 2), (0, 2, 3, 4)), parents)

    def test_t8(self):
        parents, children = self.assertAdd({0, 1}, t8)
        self.assertSetEqual(QNSet((0,), (1,)), children)
        self.assertSetEqual(QNSet((0, 1, 2)), parents)

    def test_t9(self):
        parents, children = self.assertAdd({3, 5, 7, 12, 14, 20}, t9)
        self.assertSetEqual(QNSet((3,), (20,), (5, 7, 12, 14)), children)
        self.assertSetEqual(
            QNSet((1, 3, 5, 6, 7, 12, 14, 20), (3, 5, 7, 12, 14, 17, 20)), parents
        )

    def test_d1(self):
        self.assertRemove({0, 1}, d1)

    def test_from_roots(self):
        """Check that from_roots works.

        Does not check coefficients
        """
        t = PIETree.from_roots(t1)
        self.assertTrue(t.is_complete)

        t = PIETree.from_roots(t2)
        self.assertTrue(t.is_complete)

        t = PIETree.from_roots(t3)
        self.assertTrue(t.is_complete)

    def test_MBE(self):
        order = 4
        for n in range(5, 8):
            frags = QNSet(*((i,) for i in range(n)))
            MBETree = PIETree.from_MBE_primary_frags(frags, order)
            nodes_in_graph = int(
                comb(len(frags), 4)
                + comb(len(frags), 3)
                + comb(len(frags), 2)
                + comb(len(frags), 1)
            )
            self.assertEqual(nodes_in_graph + 1, len(MBETree.tree))
            self.assertTrue(MBETree.is_complete())

            GMBETree = PIETree.from_primatives(set(frags))
            for f in combinations(frags, order):
                GMBETree.expand(frozenset.union(*f))

            # Check that all nodes are accessable and have right number of children
            node_counter = 0
            for n in nx.descendants(MBETree.tree, ROOT):
                node_counter += 1
            self.assertEqual(node_counter, nodes_in_graph)

            self.assertTrue(PIETree.is_equal(MBETree, GMBETree, check_coef=True))

    def test_idempotence(self):
        SIZE = 6
        prims = QNSet(*((i,) for i in range(SIZE)))
        big_to_small = (
            [frozenset(i) for i in combinations(range(SIZE), 4)]
            + [frozenset(i) for i in combinations(range(SIZE), 3)]
            + [frozenset(i) for i in combinations(range(SIZE), 2)]
            + [frozenset(i) for i in combinations(range(SIZE), 1)]
        )

        bs_tree = PIETree.from_primatives(prims)
        for i in big_to_small:
            bs_tree.expand(i)
        self.assertTrue(bs_tree.is_complete())

        sb_tree = PIETree.from_primatives(prims)
        for i in reversed(big_to_small):
            sb_tree.expand(i)
        self.assertTrue(sb_tree.is_complete())

        self.assertTrue(PIETree.is_equal(bs_tree, sb_tree, check_coef=True))

        # Let's try to re-add a node to the tree
        bs_tree.expand(frozenset({0, 1, 2, 3}))

        self.assertTrue(PIETree.is_equal(bs_tree, sb_tree, check_coef=True))


class TestChildEquivalence(unittest.TestCase):
    def test_child_eq(self):
        _1234 = frozenset((0, 1, 2, 3))
        _1234_children = {
            (frozenset((0, 1)), -1),
            (frozenset((0,)), 1),
            (frozenset((0, 2, 3)), 1),
            (frozenset((0, 2)), -1),
            (frozenset((0, 1, 2)), 1),
            (frozenset((0, 3)), -1),
            (frozenset((0, 1, 3)), 1),
        }
        t_new = {
            (frozenset((0, 1, 2, 4)), 1),
            (frozenset((0, 1, 4)), -1),
            (frozenset((0, 2, 3, 4)), 1),
            (frozenset((0, 1, 3, 4)), 1),
            (frozenset((0, 4)), 1),
            (frozenset((0, 3, 4)), -1),
            (frozenset((0, 2, 4)), -1),
        }

        t = PIETree.from_roots(t7)

        children = t.child_equivalent(_1234)
        children.clean_zeros()
        self.assertSetEqual({(n, d["coef"]) for n, d in children}, _1234_children)

        self.assertDictEqual({0: 1, 1: 1, 2: 1, 3: 1}, children.count_members())

        old_counts = t.count_members()

        t.replace_with_children(_1234)
        self.assertDictEqual(old_counts, t.count_members())
        t.clean_zeros()
        self.assertSetEqual({(n, d["coef"]) for n, d in t}, t_new)


class PIETestCases(unittest.TestCase):
    def assert_MBE_methods(self, n: int, o: int, r=0):
        primary_legacy = [{i} for i in range(n)]

        if r:

            def keeper(i: quickNode, r=7) -> bool:
                i_s = set.union(*i)
                return (max(i_s) - min(i_s)) <= r

            aux_legacy = [
                set.union(*i) for i in combinations(primary_legacy, o) if keeper(i, r)
            ]
        else:
            aux_legacy = [set.union(*i) for i in combinations(primary_legacy, o)]

        primary = [frozenset(i) for i in primary_legacy]
        aux = [frozenset(i) for i in aux_legacy]

        self.compair_methods(aux, primary, n, o)

    def assert_tree_equal(self, t1: nx.tree, t2: nx.tree):
        self._node_equal(ROOT, t1, t2)

    def _node_equal(self, n, t1: nx.DiGraph, t2: nx.DiGraph):
        if n != ROOT:
            self.assertEqual(t1.nodes[n]["data"], t2.nodes[n]["data"])
            self.assertEqual(t1.nodes[n]["coef"], t2.nodes[n]["coef"])

        c1 = {s for s in t1.successors(n)}
        c2 = {s for s in t1.successors(n)}
        self.assertSetEqual(c1, c2)
        t1.pred
        for c in c1:
            self._node_equal(c, t1, t2)

    def compair_methods(self, aux, primaries, n, o):
        aux_legacy = [set(i) for i in aux]
        primary_legacy = [set(i) for i in primaries]

        # print(f"{n}\t{o}", end="\t")

        gc.collect()
        s = process_time()
        plan = PIEPlan(aux_legacy)
        pie_tree = make_PIETree(plan, primary_legacy)
        _t_trad = process_time() - s

        # print(f"{len(pie_tree)}\t{_t_trad:.6f}", end="\t")

        gc.collect()
        s = process_time()
        tree = PIETree.from_primaries(primaries)
        for a in aux:
            tree.expand(a)
        tree.clean_zeros()
        _t_tree = process_time() - s

        self.assertSetEqual(tree.primaries, set(primaries))
        self.assertEqual(tree.primatives, collect_primatives(primaries))

        # print(f"{_t_tree:.6f}")

        try:
            self.assertTrue(tree_equal(pie_tree, tree.tree, check_coefs=True))
        except AssertionError:
            print("These trees do not match.")
            print(f"Reference Implementation has: {len(pie_tree) - 1} nodes")
            print(f"Target Implementation has: {len(tree.tree) - 1} nodes")
            print("Primary: ", primaries)
            print("Aux: ", aux)
            nx.nx_agraph.write_dot(tree.tree, "tree.dot")
            nx.nx_agraph.write_dot(pie_tree, "pie.dot")
            raise

    def assert_GMBE_methods(self, n: int, o: int):
        primary = [frozenset({randint(0, 20) for i in range(4)}) for i in range(n)]

        aux = [frozenset.union(*i) for i in combinations(primary, o)]
        aux = list(compress_up(aux))

        self.compair_methods(aux, primary, n, o)

    def test_MBE_higher_order(self):
        """
        Tests the case where the number of primary fragment is less
        than the requested order.

        The chosen behavior is to merge all all nodes into a single supernode instead
        of throwing an error. For example, if there are two primary nodes and the order
        is three, these two nerds will be merged
        """
        tree = PIETree.from_MBE_primary_frags(QNList({0}, {1}), 3)
        self.assertSetEqual(
            {(mk_key(n), d["coef"]) for n, d in tree},
            {((0,), 0), ((1,), 0), ((0, 1), 1)},
        )

        tree = PIETree.from_MBE_primary_frags(QNList({0}, {1}, {2}), 3)
        self.assertSetEqual(
            {(mk_key(n), d["coef"]) for n, d in tree},
            {((0,), 0), ((1,), 0), ((2,), 0), ((0, 1, 2), 1)},
        )

    def test_MBE_aux_nodes(self):
        for i in range(4, 9):
            self.assert_MBE_methods(i, 3)
        for i in range(5, 8):
            self.assert_MBE_methods(i, 4)

        # MBE PERFORMANCE TESTING
        return
        print("RUNNING MBE PERFORMANCE TEST")
        for i in range(4, 17, 2):
            self.assert_MBE_methods(i, 3)
        for i in range(6, 19, 2):
            self.assert_MBE_methods(i, 4)
        return
        print("RUNNING SCREENED MBE PERFORMANCE TEST")
        for i in range(5, 151, 5):
            self.assert_MBE_methods(i, 3, r=7)
        for i in range(5, 151, 5):
            self.assert_MBE_methods(i, 4, r=7)

    def test_GMBE_aux_nodes(self):
        seed(314)
        for i in range(4, 7):
            self.assert_GMBE_methods(i, 3)
        for i in range(5, 8):
            self.assert_GMBE_methods(i, 4)

        # GMBE PERFORMANCE TESTING
        return
        print("DOING STRESS GMBE TEST")
        for i in range(50):
            self.assert_GMBE_methods(randint(4, 8), randint(3, 5))
