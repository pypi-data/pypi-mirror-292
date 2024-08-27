#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import unittest

import numpy as np
from conformer import spatial
from conformer.systems import System

from fragment.fragmenting.covalent_components import CovalentComponentsFragmenter
from fragment.mods.distance import (
    MaxDistanceFilter,
    NearestNeighborDistanceFilter,
    max_distance,
    nearest_neighbor_distance,
)
from fragment.mods.MIC import ValidMICSystemFilter
from fragment.spatial import view_distance_matrix

fs = frozenset


class DistanceTestCases(unittest.TestCase):
    def setUp(self) -> None:
        self.sys = System.from_tuples(
            [
                ("He", 0, 0, 0),
                ("He", 1, 0, 0),
                ("He", 2, 0, 0),
                ("He", 3, 0, 0),
            ],
        )
        cc = CovalentComponentsFragmenter()
        self.view = cc(self.sys)

    def test_max_distance(self):
        dm = view_distance_matrix(self.view, spatial.system_COM_distance)
        self.assertAlmostEqual(2, max_distance(dm, [fs({0}), fs({1}), fs({2})]))
        self.assertAlmostEqual(3, max_distance(dm, [fs({0}), fs({1}), fs({3})]))

        md = MaxDistanceFilter.from_options(r={2: 2.0})
        self.assertEqual(md(self.view, [fs({0}), fs({1})], 2)[1], True)
        self.assertEqual(md(self.view, [fs({0}), fs({1})], 3)[1], True)
        self.assertEqual(md(self.view, [fs({0}), fs({3})], 2)[1], False)

        md = MaxDistanceFilter.from_options(r=2.0)
        self.assertIs(md.dm_metric, spatial.system_MIC_CA_distance)
        self.assertEqual(md(self.view, [fs({0}), fs({1})], 2)[1], True)
        self.assertEqual(md(self.view, [fs({0}), fs({1})], 3)[1], True)

        # Test changing the distance method
        md = MaxDistanceFilter.from_options(r=2.0, method="closest")
        self.assertIs(md.dm_metric, spatial.system_CA_distance)
        self.assertEqual(md(self.view, [fs({0}), fs({1})], 2)[1], True)

    def test_nearest_neighbors_distance(self):
        dm = view_distance_matrix(self.view, spatial.system_COM_distance)
        self.assertAlmostEqual(
            1, nearest_neighbor_distance(dm, [fs({0}), fs({1}), fs({2})])
        )
        self.assertAlmostEqual(
            2, nearest_neighbor_distance(dm, [fs({0}), fs({1}), fs({3})])
        )

        md = NearestNeighborDistanceFilter.from_options(r={2: 2.0})
        self.assertEqual(md(self.view, [fs({0}), fs({1})], 2)[1], True)
        self.assertEqual(md(self.view, [fs({0}), fs({1}), fs({2})], 3)[1], True)
        self.assertEqual(md(self.view, [fs({0}), fs({2})], 3)[1], True)
        self.assertEqual(md(self.view, [fs({0}), fs({3})], 2)[1], False)

        md = NearestNeighborDistanceFilter.from_options(r=2.0)
        self.assertEqual(md(self.view, [fs({0}), fs({1})], 2)[1], True)
        self.assertEqual(md(self.view, [fs({0}), fs({1}), fs({2})], 3)[1], True)
        self.assertEqual(md(self.view, [fs({0}), fs({2})], 3)[1], False)

    def test_view_distance_matrix(self):
        dm = view_distance_matrix(self.view, spatial.system_COM_distance)
        self.assertIs(dm, view_distance_matrix(self.view, spatial.system_COM_distance))

        dm = view_distance_matrix(self.view, spatial.system_CA_distance)
        self.assertIs(dm, view_distance_matrix(self.view, spatial.system_CA_distance))

    def test_MIC_filter(self):
        # Test for non-periodic systesm
        mf = ValidMICSystemFilter()
        self.assertEqual(mf(self.view, [fs({0}), fs({1})], 2)[1], True)
        self.assertEqual(mf(self.view, [fs({0}), fs({3})], 2)[1], True)

        # Make the system periodic
        self.sys.unit_cell = np.array([4, 4, 4])
        self.view.bind_system(self.sys)

        self.assertEqual(mf(self.view, [fs({0}), fs({1})], 2)[1], True)
        self.assertEqual(mf(self.view, [fs({0}), fs({3})], 2)[1], False)


# class TestDistance(DBTestCase):
#     def setUp(self) -> None:
#         systems = [System([Atom("H", r=(i, 0, 0))]) for i in range(4)]
#         systems.append(System([Atom("H", r=(-4, 0, 0))]))
#         self.s1, self.s2, self.s3, self.s4, self.s5 = systems

#         for s in systems:
#             s.save()

#         self.supersystem = System.merge(*systems)
#         self.view = View(systems, [0 for _ in systems])

#     def test_max_distance(self):
#         dfilter = DistanceMod(
#             "df",
#             "note",
#             # Pydantic returns this with string mapping keys
#             max_distance={"2": 2.5, "3": 2.5},
#         )
#         dfilter.setUp(self.supersystem, self.view, 3, 0)

#         # Test two-body thresholds
#         self.assertTrue(dfilter.run(self.s1, self.s2))
#         self.assertTrue(dfilter.run(self.s1, self.s3))
#         self.assertFalse(dfilter.run(self.s1, self.s4))

#         # Test three-body thresholds
#         self.assertFalse(dfilter.run(self.s1, self.s2, self.s4))  # Outside max
#         self.assertTrue(dfilter.run(self.s1, self.s2, self.s3))  # Outside min

#     def test_min_distance(self):
#         dfilter = DistanceMod(
#             "df",
#             "note",
#             min_distance={"2": 2.5, "3": 2.5},
#         )
#         dfilter.setUp(self.supersystem, self.view, 3, 0)

#         # Test two-body thresholds
#         self.assertTrue(dfilter.run(self.s1, self.s2))
#         self.assertTrue(dfilter.run(self.s1, self.s3))
#         self.assertFalse(dfilter.run(self.s1, self.s4))

#         # Test three-body thresholds
#         self.assertTrue(dfilter.run(self.s1, self.s2, self.s4))
#         self.assertTrue(dfilter.run(self.s1, self.s2, self.s3))
#         self.assertFalse(dfilter.run(self.s1, self.s4, self.s5))  # outisde min
