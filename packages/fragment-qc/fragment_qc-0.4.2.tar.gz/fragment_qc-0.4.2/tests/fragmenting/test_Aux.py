#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from unittest.mock import patch

from conformer.systems import System
from conformer_core.accessors import Accessor
from conformer_core.stages import Stage

from fragment.core.PIETree import PIETree
from fragment.fragmenting.abstract import (
    BottomUpFragmenter,
    FullFragmenter,
    TopDownFragmenter,
)
from fragment.views import Key, View
from tests import FragmentTestCase

NUM_ATOMS = 5


class No123Filter(Stage, Accessor):
    """Dummy mod to get rid of fragment with key (1,2,3)"""

    def churn(self) -> None:
        while not self.in_queue.empty():
            args = self.in_queue.get()
            view, primaries, order = args

            k = frozenset.union(*primaries)
            if k in {frozenset({0, 1, 2, 3}), frozenset({0, 1, 3, 4})}:
                ret = False
            else: 
                ret = True

            self.out_queue.put((args, ret))
            self.in_queue.task_done()


class TestAuxFragmenters(FragmentTestCase):

    """Testing these two fragmenters is easier with both present"""

    def setUp(self):
        self.sys = System.from_tuples([("H", i, i, i) for i in range(NUM_ATOMS)])

        self.p_frags = View.new_primary(
            Stage(),
            set([Key([i, i + 1]) for i in range(NUM_ATOMS - 1)]),
            supersystem=self.sys,
        )

    def test_primary_fragments(self):
        self.assertEqual(len(self.p_frags.primaries), 4)
        self.assertSetEqual(
            set(self.p_frags.iter_keys(include_zeros=True)),
            {
                Key([0, 1]),
                Key([1, 2]),
                Key([2, 3]),
                Key([3, 4]),
                Key([0]),
                Key([1]),
                Key([2]),
                Key([3]),
                Key([4]),
            },
        )

    def test_aux_fragments(self):
        # Key: (coef, order)
        fragments = {
            frozenset({0, 1, 2, 3}): (1, 3),
            frozenset({0, 1, 3, 4}): (1, 2),
            frozenset({1, 2, 3, 4}): (1, 3),
            frozenset({0, 1, 3}): (-1, 1),
            frozenset({1, 2, 3}): (-1, 2),
            frozenset({1, 3, 4}): (-1, 1),
            frozenset({1, 3}): (1, 0),
        }
        full_fragmenter = FullFragmenter()
        aux_frags = full_fragmenter(self.p_frags, 2)

        self.assertSetEqual(set(aux_frags.iter_keys()), {k for k in fragments.keys()})
        for k, d in aux_frags:
            self.assertEqual(fragments[k][0], d["coef"])
            self.assertEqual(fragments[k][1], d["primary_order"])

    @patch.object(PIETree, "from_MBE_primary_frags")
    def test_aux_MBE(self, mock):
        fragmenter = FullFragmenter()
        view = View.new_primary(Stage(), set([Key([1]), Key([2]), Key([3])]))
        # NOTE: Most testing done in PIETree package :)
        fragmenter(view, 2)
        self.assertTrue(mock.called)

    def test_TD_v_BU(self):
        no_123 = No123Filter.from_options("n124")

        # Make fragmenters
        FULL = FullFragmenter.from_options("full", clean_zeros=True)

        TD = TopDownFragmenter.from_options("top_down", clean_zeros=True)
        TD_mod = TopDownFragmenter.from_options(
            "top_down_moded",
            links=dict(filters=[no_123]),
            clean_zeros=True,
        )

        BU = BottomUpFragmenter.from_options("bottom_up", clean_zeros=True, M=0)
        BU_mod = BottomUpFragmenter.from_options(
            "bottom_up_moded", links=dict(filters=[no_123]), clean_zeros=True, M=0
        )
        BU_mod_M1 = BottomUpFragmenter.from_options(
            "bottom_up_moded_missing_children",
            links=dict(filters=[no_123]),
            clean_zeros=True,
            M=1,
        )

        # Two appraoches should give the same results w/o filters
        view_FULL = FULL(self.p_frags, 3)
        view_TD = TD(self.p_frags, 3)
        view_BU = BU(self.p_frags, 3)

        self.assertEqual(view_FULL, view_TD)
        self.assertEqual(view_TD, view_BU)

        # Results will be different for modded approach
        view_TD_mod = TD_mod(self.p_frags, 3)
        view_BU_mod = BU_mod(self.p_frags, 3)
        view_BU_mod_M1 = BU_mod_M1(self.p_frags, 3)

        self.assertNotEqual(view_TD_mod, view_BU_mod)
        self.assertEqual(view_TD_mod, view_BU_mod_M1)

        fragments = {
            frozenset({1, 2, 3, 4}): (1, 3),
            frozenset({0, 1, 2}): (1, 2),
            frozenset({1, 2}): (-1, 1),
        }

        for k, d in view_BU_mod.iter_data():
            self.assertEqual(fragments[k][0], d["coef"])
            self.assertEqual(fragments[k][1], d["primary_order"])
