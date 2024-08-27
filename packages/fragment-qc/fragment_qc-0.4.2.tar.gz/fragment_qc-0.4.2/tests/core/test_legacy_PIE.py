#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import unittest
from itertools import combinations
from random import randint, seed

import networkx as nx

from fragment.core import legacy_PIETree as PIETree
from fragment.core.legacy_PIE import NodeDict, PIEPlan, mk_key


class NodeDictTestCases(unittest.TestCase):
    def test_session(self):
        nd = NodeDict()
        with self.assertRaises(Exception):
            nd.add_node({1, 2}, 1)

    def test_add(self):
        nd = NodeDict()
        with nd:
            nd.add_node({1, 2}, 1)
            self.assertEqual(len(nd), 0)
            self.assertEqual(
                nd.new_nodes[
                    (
                        1,
                        2,
                    )
                ].coef,
                1,
            )

        self.assertEqual(len(nd), 1)
        self.assertEqual(
            nd[
                (
                    1,
                    2,
                )
            ].coef,
            1,
        )

        # Now check for proper cancelation
        with nd:
            nd.add_node({1, 2}, -1)
        self.assertEqual(
            nd[
                (
                    1,
                    2,
                )
            ].coef,
            0,
        )


class TestPIE(unittest.TestCase):
    def test_integration_test(self):
        order = 2
        num_primary_fragments = 12

        # Generate a consistant test set
        seed(314)
        fragments = [
            {randint(1, 20) + 0 * i for j in range(15)}
            for i in range(num_primary_fragments)
        ]
        fragment_ids = range(num_primary_fragments)

        union_total = sum(set.union(*fragments))

        aux_nodes = []
        for aux_f in combinations(zip(fragments, fragment_ids), order):
            aux_node = set.union(*(af[0] for af in aux_f))
            aux_nodes.append(aux_node)

        plan = PIEPlan(roots=aux_nodes)
        self.assertEqual(plan.size, 2271)
        self.assertEqual(plan.unconsolidated_size, 2307)
        self.assertEqual(plan.total, 210)
        self.assertEqual(plan.total, union_total)

        for n in plan.nodes.values():
            self.assertTrue(n.data)


class PIE2Tests(unittest.TestCase):
    """
    Tests added in version 2.0 of the PIE solver
    """

    def setUp(self) -> None:
        seed(314)
        num_primary_fragments = 15
        self.order = 2
        self.fragments = [
            {randint(1, 20) + 2 * i for j in range(15)}
            for i in range(num_primary_fragments)
        ]

    def benchmark_plan(self, plan, limit=7):
        aux = []
        for fs in combinations(self.fragments[0:limit], self.order):
            f = set.union(*(af for af in fs))
            aux.append(f)

        for f in aux:
            plan.add_node(f)

    @unittest.skip("Not fully implemented")
    def test_travers_deps(self):
        limit = 6
        plan2 = PIEPlan()
        self.benchmark_plan(plan2, limit=limit)
        plan2.resolve_deps()

        aux_nodes = [n for n in plan2.nodes.values() if n.coef != 0]
        index_map = {}
        for i, n in enumerate(aux_nodes):
            index_map[n.key] = i


class PIETreeTestCases(unittest.TestCase):
    def setUp(self) -> None:
        self.parents = [{i, i + 1} for i in range(6)]
        import random

        random.shuffle(self.parents)

        self.roots = []
        for aux_roots in combinations(self.parents, 2):
            self.roots.append(set.union(*(n for n in aux_roots)))

        keep = [True for _ in range(len(self.roots))]

        for (n1_i, n1), (n2_i, n2) in combinations(enumerate(self.roots), 2):
            if n1.issubset(n2):
                keep[n1_i] = False
                continue
            if n1.issuperset(n2):
                keep[n2_i] = False
                continue

        # Simplify the ROOTS. No overlaps
        from itertools import compress

        self.plan = PIEPlan(compress(self.roots, keep))

    def test_tree(self):
        _tree = PIETree.make_PIETree(self.plan, self.parents)

    def test_steps(self) -> None:
        G = nx.DiGraph()
        G.add_node(0)

        PIETree.add_aux_nodes(G, self.plan, self.parents)
        for n in self.plan.nodes.values():
            if n.coef == 0:
                continue
            self.assertEqual(G.nodes[n.key]["coef"], n.coef)

        # Check that the data field is equal to the key field
        for n, data in G.nodes(data=True):
            if n == PIETree.ROOT:
                self.assertDictEqual(data, {})
                continue
            self.assertSetEqual(set(n), data["data"])

        PIETree.add_aux_edges(G, self.plan)
        for n in nx.isolates(G):
            print(n)
        self.assertEqual(nx.number_of_isolates(G), 0)
        self.assertSetEqual(
            {n for n in nx.dfs_postorder_nodes(G, source=PIETree.ROOT)},
            {
                (1, 3),
                (0, 1, 3),
                (1, 2, 3),
                (0, 1, 2, 3),
                (1, 4),
                (0, 1, 4),
                (1, 3, 4),
                (0, 1, 3, 4),
                (1, 5),
                (0, 1, 5),
                (1, 4, 5),
                (0, 1, 4, 5),
                (1, 5, 6),
                (0, 1, 5, 6),
                (2, 4),
                (1, 2, 4),
                (2, 3, 4),
                (1, 2, 3, 4),
                (2, 5),
                (1, 2, 5),
                (2, 4, 5),
                (1, 2, 4, 5),
                (2, 5, 6),
                (1, 2, 5, 6),
                (3, 5),
                (2, 3, 5),
                (3, 4, 5),
                (2, 3, 4, 5),
                (3, 5, 6),
                (2, 3, 5, 6),
                (3, 4, 5, 6),
                0,
            },
        )


class PIETreeManipulationTestCases(unittest.TestCase):
    def setUp(self) -> None:
        self.order = 4
        self.parents = [{i} for i in range(6)]
        self.skips = [{0, 1}, {2, 3}]

        self.aux_nodes = []
        self.trimmed_aux_nodes = []
        for ns in combinations(self.parents, self.order):
            n = set.union(*ns)
            self.aux_nodes.append(n)
            if not self.skippable(n):
                self.trimmed_aux_nodes.append(n)

        self.full_plan = PIEPlan(self.aux_nodes)
        self.full_tree = PIETree.make_PIETree(self.full_plan, self.parents)

        self.trimmed_plan = PIEPlan(self.trimmed_aux_nodes)
        self.trimmed_tree = PIETree.make_PIETree(self.trimmed_plan, self.parents)

    def skippable(self, n: set):
        for s in self.skips:
            if s.issubset(n):
                return True
        return False

    def test_rm_zeros(self):
        wt = self.full_tree
        for an in self.aux_nodes:
            if self.skippable(an):
                PIETree.zero_node(wt, mk_key(an))
        PIETree.rm_zeros(wt)
        PIETree.prune_false_roots(wt)

        self.assertDictEqual(
            {n.key: n.coef for n in self.trimmed_plan.nodes.values()},
            {n: d["coef"] for n, d in wt.nodes(data=True) if n != PIETree.ROOT},
        )
