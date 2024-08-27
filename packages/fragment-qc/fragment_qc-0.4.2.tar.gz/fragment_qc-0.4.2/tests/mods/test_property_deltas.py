#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import unittest
from copy import deepcopy
from itertools import combinations

from atomdriver.accessors import clear_accessor_cache
from atomdriver.drivers.libxtb import LibxTB
from conformer.records import SystemRecord
from conformer.systems import System
from conformer_core.properties.core import PropertySet
from conformer_core.records import RecordStatus
from conformer_core.stages import Stage

from fragment.mods.property_delta import (
    DeltaPropertyAccessor,
    DeltaPropertyTask,
    DeltaProperyFilter,
)
from fragment.views import View

fs = frozenset
PRIMARIES = [fs({1}), fs({2}), fs({3})]


def new_record(sys: System, total_energy: float) -> SystemRecord:
    return SystemRecord(
        stage=Stage(),
        system=sys,
        properties=PropertySet.from_dict({"total_energy": total_energy}),
    )


class DeltaTestCases(unittest.TestCase):
    def setUp(self) -> None:
        self.sys = System.from_tuples(
            [
                ("He", 0, 0, 0),
                ("He", 1, 0, 0),
                ("He", 2, 0, 0),
                ("He", 3, 0, 0),  # Not included
            ]
        ).canonize()

    def tearDown(self) -> None:
        clear_accessor_cache()

    def test_DeltaPropertyTask(self):
        sys = self.sys
        task = DeltaPropertyTask(
            [fs.union(*c) for c in combinations(PRIMARIES, 2)], sys.subsystem
        )

        self.assertFalse(task.done())
        self.maxDiff = None
        self.assertDictEqual(
            {
                sys.subsystem([1, 2, 3]): 1,
                sys.subsystem([1, 2]): -1,
                sys.subsystem([1, 3]): -1,
                sys.subsystem([2, 3]): -1,
                sys.subsystem([1]): 1,
                sys.subsystem([2]): 1,
                sys.subsystem([3]): 1,
            },
            task.coefs,
        )

        # Test failure
        failed_task = deepcopy(task)
        failed_record = new_record(sys.subsystem([1, 2, 3]), 3.3)
        failed_record.status = RecordStatus.FAILED
        failed_record.meta['error'] = 'bad'
        failed_task.update(failed_record)
        self.assertTrue(failed_task.done())
        self.assertEqual(failed_task.result.status, RecordStatus.FAILED)
        self.assertEqual(failed_task.result.meta['error'], 'bad')
        self.assertEqual(failed_task.result.meta['failed_system'], sys.subsystem([1, 2, 3]).fingerprint)

        # Finish testing the working task
        task.update(new_record(sys.subsystem([1, 2, 3]), 3.3))
        self.assertFalse(task.done())

        task.update(new_record(sys.subsystem([1, 2]), 2.05))
        task.update(new_record(sys.subsystem([1, 3]), 2.0))
        task.update(new_record(sys.subsystem([2, 3]), 2.05))
        task.update(new_record(sys.subsystem([1]), 1.0))
        task.update(new_record(sys.subsystem([2]), 1.0))
        task.update(new_record(sys.subsystem([3]), 1.0))
        self.assertTrue(task.done())

        self.assertAlmostEqual(task.result.properties["total_energy"], 0.2)

    def test_DeltaPropertyAccessor(self):
        driver = LibxTB.from_options(use_database=False)
        accessor = DeltaPropertyAccessor.from_options(links={"driver": driver})
        accessor.submit(
            [fs.union(*c) for c in combinations(PRIMARIES, 2)], self.sys.subsystem
        )

        args, result = list(accessor.as_completed())[0]
        self.assertAlmostEqual(result.properties["total_energy"], 0.068836)
        self.assertEqual(result.status, RecordStatus.COMPLETED)

    def test_DeltaProperyFilter(self):
        driver = LibxTB.from_options(use_database=False)
        sys = self.sys
        primaries = [fs([i]) for i in range(sys.size)]

        # Just need this for subsystem
        stage = Stage()
        stage.subsystem_mods = []  # Mock a fragmenter
        view = View.new_primary(stage, primaries, supersystem=sys)

        # Test None for thresholds
        accessor = DeltaProperyFilter.from_options(links={"driver": driver}, T={})
        for aux in combinations(primaries, 2):
            accessor.submit(view, aux, 2)

        # for (view, _aux, order), (result) in accessor.as_completed():
        for (view, _aux, order), (result) in accessor.as_completed():
            self.assertTrue(result)

        # Test with actual threshold
        FILTER_FIXTURE = {
            sys.subsystem([0, 1]): True,
            sys.subsystem([1, 2]): True,
            sys.subsystem([2, 3]): True,
            sys.subsystem([0, 2]): False,
            sys.subsystem([0, 3]): False,
            sys.subsystem([1, 3]): False,
        }

        # Test specific value
        accessor = DeltaProperyFilter.from_options(links={"driver": driver}, T={2: 10})
        for aux in combinations(primaries, 2):
            accessor.submit(view, aux, 2)
        for (view, _aux, order), (result) in accessor.as_completed():
            k = frozenset.union(*_aux)
            self.assertEqual(FILTER_FIXTURE[sys.subsystem(k)], result)

        # Test default value
        accessor = DeltaProperyFilter.from_options(
            links={"driver": driver}, T={}, default_T=10
        )
        for aux in combinations(primaries, 2):
            accessor.submit(view, aux, 2)
        for (view, _aux, order), (result) in accessor.as_completed():
            k = frozenset.union(*_aux)
            self.assertEqual(FILTER_FIXTURE[sys.subsystem(k)], result)
