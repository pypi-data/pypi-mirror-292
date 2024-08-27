#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from typing import Any, DefaultDict, FrozenSet, Generator, Iterator, List

from atomdriver.abstract_driver import Driver
from atomdriver.accessors import DispatcherClient
from atomdriver.project import AtomDriverProject
from conformer.systems import System
from conformer_core.records import RecordStatus

from fragment.db.models import DBViewRecord
from fragment.fragmenting.abstract import Fragmenter
from fragment.views import View, ViewRecord

FILL_LEVEL = 500

def refill(accessor: DispatcherClient, sys_iterator: Iterator, lookup: DefaultDict[System, List[FrozenSet[int]]], fill_level=FILL_LEVEL) -> True:
    try:
        while accessor.num_active < fill_level:
            sys, d = next(sys_iterator)
            lookup[sys].append(d['data']) # System-to-key
            accessor.submit(sys)
    except StopIteration:
        return False
    return True


def accumulate_view(
    accessor: DispatcherClient, view: View
) -> Generator[None, None, ViewRecord]:
    # Save view
    sys = view.supersystem  # This can be rebound later

    records = DBViewRecord.get_view_record(accessor.driver, view, [sys])
    if records:
        record = records[sys]
        if record.status == RecordStatus.COMPLETED:
            return record
        record.properties = None
        record.meta["completed_jobs"] = 0
        record.meta["total_jobs"] = view.size(include_zeros=False)
    else:
        record = ViewRecord(
            stage=accessor.driver,
            view=view,
            system=sys,
            meta={"total_jobs": view.size(include_zeros=False), "completed_jobs": 0},
        )

    # sys_iterator = self.run_hook("wrap_view_iterator", view)
    sys_iterator = view.iter_systems(include_zeros=False)
    lookup: DefaultDict[System, List[FrozenSet[int]]] = DefaultDict(list)
    has_more = refill(accessor, sys_iterator, lookup)
    failed_job = False

    # Run until complete
    while True:
        completed = accessor.get_completed()
        _pressure = (FILL_LEVEL - len(completed)) / FILL_LEVEL
        if has_more:
            has_more = refill(accessor, sys_iterator, lookup)

        record.meta["completed_jobs"] += len(completed)
        for s, r in completed:
            if r.status == RecordStatus.COMPLETED:
                for k in lookup.pop(s):
                    record.add_into(r, coef=view[k]["coef"])
            else:
                record.status = RecordStatus.FAILED
                record.meta["error"] = r.meta.get("error", "Calculation failed")
                record.meta["failed_system"] = r.system.fingerprint
                failed_job = True
                break  # Break from loop and construct records

        # print(f"PRESSURE: {_pressure:.3f}")
        if failed_job: #  Failed :(
            break
        elif not has_more and accessor.num_active == 0: #  Succesfully finishe!
            break
        elif _pressure < 0.8: # Relative to the refill level of 500
            # print("FAST FORWARD!")
            continue  #  Fast forward! We want to hit Ray as soon as possible
        else:  #  Still waiting
            yield

    # TODO: Check if the accessor uses the DB
    if (record.status == RecordStatus.PENDING) and (
        record.meta["completed_jobs"] == record.meta["total_jobs"]
    ):
        record.status = RecordStatus.COMPLETED

    # Imperfect but it gives some control
    if view.fragmenter._use_db:
        DBViewRecord.add_or_update_view_record([record])
    return record


class FragmentProject(AtomDriverProject):
    # GENERAL
    DEFAULT_CONFIG = "fragment"
    STAGE_SOURCES = ("stages", "drivers", "fragmenters", "mods")

    def get_fragmenter(self, fragmenter_name: str) -> Fragmenter:
        fragmenter = self.get_stage(fragmenter_name)
        assert isinstance(fragmenter, Fragmenter)
        return fragmenter

    def call_stage(self, in_value, stage, args) -> Generator[None, None, Any]:
        if isinstance(in_value, View) and isinstance(stage, Driver):
            """Accumulates a all systems in a view"""
            accessor = self.get_driver(stage)
            return accumulate_view(accessor, in_value)
        return super().call_stage(in_value, stage, args)
