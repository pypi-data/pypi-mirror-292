#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import gc
import unittest
from itertools import combinations
from random import randint, seed
from time import process_time
from typing import Tuple

from fragment.core.legacy_PIE import PIEPlan, mk_key
from fragment.core.quickPIE import (
    mk_quickNode,
    mk_quickPlan,
    mk_quickPlan_dirty,
    quickPlan,
)


class QuickPIETestCases(unittest.TestCase):
    def assert_plans_equal(self, p1: quickPlan, p2: PIEPlan):
        p1_keys = {mk_key(p) for p, c in p1.items() if c != 0}
        p2_keys = {p for p, c in p2.nodes.items() if c.coef != 0}

        # p1_keys = {mk_key(p) for p, c in p1.items()}
        # p2_keys = {p for p, c in p2.nodes.items()}

        if p1_keys != p2_keys:
            for n, c in p1.items():
                if c == 0:
                    continue
                print(n, c, sep=": ")
            for n, c in p2.nodes.items():
                if c.coef == 0:
                    continue
                print(n, c.coef, sep=": ")
            raise AssertionError(
                f"Plans have different keys: {set.difference(p1_keys, p2_keys)}"
            )

        for k1, c1 in p1.items():
            if c1 == 0:
                continue
            assert c1 == p2.nodes[mk_key(k1)].coef

    def compair_methods(self, aux, primaries, n, o):
        gc.collect()
        s = process_time()
        plan = PIEPlan(aux)
        _t_trad = process_time() - s

        gc.collect()
        s = process_time()
        quick_plan = mk_quickPlan((mk_quickNode(a) for a in aux))
        _t_quick = process_time() - s

        gc.collect()
        s = process_time()
        quick_dirty_plan = mk_quickPlan_dirty((mk_quickNode(a) for a in aux))
        _t_quick_dirty = process_time() - s

        # print(
        #     f"{n}\t{o}\t{len(quick_plan)}\t{_t_trad:.6f}"
        #     + f"\t{_t_quick:.6f}"
        #     + f"\t{_t_quick_dirty:.6f}"
        # )

        self.assert_plans_equal(quick_plan, plan)
        self.assert_plans_equal(quick_dirty_plan, plan)

    def assert_MBE_methods(self, n: int, o: int, r=0):
        primary = [{i} for i in range(n)]

        if r:

            def keeper(i: Tuple[int, ...], r=7) -> bool:
                i_s = set.union(*i)
                return (max(i_s) - min(i_s)) <= r

            aux = [set.union(*i) for i in combinations(primary, o) if keeper(i, r)]
        else:
            aux = [set.union(*i) for i in combinations(primary, o)]

        self.compair_methods(aux, primary, n, o)

    def assert_GMBE_methods(
        self,
        n: int,
        o: int,
    ):
        seed(314)
        primary = [{randint(0, 20) for i in range(4)} for i in range(n)]

        aux = [set.union(*i) for i in combinations(primary, o)]

        self.compair_methods(aux, primary, n, o)

    def test_MBE_aux_nodes(self):
        for i in range(4, 9):
            self.assert_MBE_methods(i, 3)
        for i in range(5, 8):
            self.assert_MBE_methods(i, 4)

        # MBE PERFORMANCE TESTING
        return
        print("RUNNING MBE PERFORMANCE TEST")
        for i in range(4, 21, 2):
            self.assert_MBE_methods(i, 3)
        for i in range(6, 23, 2):
            self.assert_MBE_methods(i, 4)

        print("RUNNING SCREENED MBE PERFORMANCE TEST")
        for i in range(5, 151, 5):
            self.assert_MBE_methods(i, 3, r=7)
        for i in range(5, 151, 5):
            self.assert_MBE_methods(i, 4, r=7)

    def test_GMBE_aux_nodes(self):
        for i in range(4, 8):
            self.assert_GMBE_methods(i, 3)
        for i in range(5, 9):
            self.assert_GMBE_methods(i, 4)
        return

        print("DOING STRESS GMBE TEST")
        for i in range(50):
            self.assert_GMBE_methods(randint(6, 10), randint(3, 5))
