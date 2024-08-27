#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from conformer.systems import System
from conformer_core.stages import Stage

from fragment.fragmenting.abstract import FullFragmenter
from fragment.fragmenting.interaction_energy import InteractionEnergy
from fragment.views import View
from tests import FragmentTestCase

fs = frozenset


class TestInteractionEnergies(FragmentTestCase):
    def test_interaction_energie_fragmenter(self):
        AB_sys = System.from_tuples(
            [
                ("He", 0, 0, 0),
                ("He", 1, 0, 0),
                ("He", 2, 0, 0), 
                ("He", 3, 0, 0),
            ]
        )

        # Split into 50:50 system
        A_sys = AB_sys.subsystem([0, 1])
        B_sys = AB_sys.subsystem([2, 3])

        # Split into 25:75 system
        I_sys = AB_sys.subsystem([0])
        J_sys = AB_sys.subsystem([1, 2, 3])

        p_view = View.new_primary(
            fragmenter=Stage(),
            primaries={fs([i]) for i in range(4)},
            supersystem=AB_sys,
        )

        full_mbe = FullFragmenter(_use_db=True)
        mbe2 = full_mbe(p_view, 2)
        mbe3 = full_mbe(p_view, 3)

        ie_mbe = InteractionEnergy(_use_db=True)

        # This causes and error
        with self.assertRaises(AssertionError):
            ie_mbe(mbe2, A_sys, I_sys)

        v = ie_mbe(mbe2, A_sys, B_sys)
        v2 = ie_mbe(mbe2, A_sys, B_sys)
        self.assertSetEqual(
            {(n, d["coef"]) for n, d in v},
            {
                (fs({0}), -2),
                (fs({1}), -2),
                (fs({2}), -2),
                (fs({3}), -2),
                (fs({0, 2}), 1),
                (fs({0, 3}), 1),
                (fs({1, 2}), 1),
                (fs({1, 3}), 1),
            },
        )

        v = ie_mbe(mbe3, A_sys, B_sys)
        v2 = ie_mbe(mbe3, A_sys, B_sys)
        self.assertEqual(v._saved, v2._saved)
        self.assertSetEqual(
            {(n, d["coef"]) for n, d in v},
            {
                (fs({0}), 1),
                (fs({1}), 1),
                (fs({2}), 1),
                (fs({3}), 1),
                (fs({0, 1}), -2),
                (fs({0, 2}), -1),
                (fs({0, 3}), -1),
                (fs({1, 2}), -1),
                (fs({1, 3}), -1),
                (fs({2, 3}), -2),
                (fs({0, 1, 2}), 1),
                (fs({0, 1, 3}), 1),
                (fs({0, 2, 3}), 1),
                (fs({1, 2, 3}), 1),
            },
        )

        v = ie_mbe(mbe2, I_sys, J_sys)
        v2 = ie_mbe(mbe2, I_sys, J_sys)
        self.assertEqual(v._saved, v2._saved)
        self.assertSetEqual(
            {(n, d["coef"]) for n, d in v},
            {
                (fs({0}), -3),
                (fs({1}), -1),
                (fs({2}), -1),
                (fs({3}), -1),
                (fs({0, 1}), 1),
                (fs({0, 2}), 1),
                (fs({0, 3}), 1),
            },
        )


        v = ie_mbe(mbe3, I_sys, J_sys)
        v2 = ie_mbe(mbe3, I_sys, J_sys)
        self.assertEqual(v._saved, v2._saved)
        self.assertSetEqual(
            {(n, d["coef"]) for n, d in v},
            {
                (fs({1}), 1),
                (fs({2}), 1),
                (fs({3}), 1),
                (fs({0, 1}), -1),
                (fs({0, 2}), -1),
                (fs({0, 3}), -1),
                (fs({1, 2}), -1),
                (fs({1, 3}), -1),
                (fs({2, 3}), -1),
                (fs({0, 1, 2}), 1),
                (fs({0, 1, 3}), 1),
                (fs({0, 2, 3}), 1),
            },
        )