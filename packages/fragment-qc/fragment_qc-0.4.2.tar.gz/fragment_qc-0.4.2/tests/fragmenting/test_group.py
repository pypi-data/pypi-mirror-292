#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import unittest

from conformer.example_systems import read_example

from fragment.fragmenting.groups import GroupFragmenter
from tests._util import QNList

FRAGMENT_LENGTHS = {4, 8, 7, 9, 1, 9, 13}

class TestGroup(unittest.TestCase):
    def setUp(self) -> None:
        self.fragmenter = GroupFragmenter()

    def test_water(self):
        sys = read_example("water-6-cluster.frag")
        view = self.fragmenter(sys)

        self.assertEqual(view.size(include_zeros=True), 6)
        for s, d in view.iter_systems(include_zeros=True):
            self.assertEqual(s.chemical_formula(), "H2O")

    def test_protien(self):
        sys = read_example("small_protien.pdb")
        view = self.fragmenter(sys)
        self.assertEqual(view.size(include_zeros=True), 7)

        self.assertSetEqual(
            FRAGMENT_LENGTHS,
            {s.size for s, d in view.iter_systems(include_zeros=True)}
        )

    @unittest.skip("Not Implemented. Add Glob mod")
    def test_window(self):
        ...
        p_frags = self.fragmenter.primary_fragments(self.sys)

        self.assertEqual(len(p_frags.fragments), 6)

        frag_atom_ids = [f.key for f in p_frags.fragments]
        # print(frag_atom_ids)
        self.assertListEqual(
            frag_atom_ids,
            QNList(
                (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12),
                (5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19),
                (13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28),
                (20, 21, 22, 23, 24, 25, 26, 27, 28, 29),
                (29, 30, 31, 32, 33, 34, 35, 36, 37, 38),
                (
                    30,
                    31,
                    32,
                    33,
                    34,
                    35,
                    36,
                    37,
                    38,
                    39,
                    40,
                    41,
                    42,
                    43,
                    44,
                    45,
                    46,
                    47,
                    48,
                    49,
                    50,
                    51,
                ),
            ),
        )