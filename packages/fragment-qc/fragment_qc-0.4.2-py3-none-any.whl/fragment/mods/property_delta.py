#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from itertools import combinations
from typing import (
    Any,
    Callable,
    DefaultDict,
    Dict,
    FrozenSet,
    Iterable,
    List,
    Optional,
    Tuple,
)
from uuid import UUID, uuid4

from atomdriver.abstract_driver import Driver
from atomdriver.accessors import DriverAccessor, get_accessor
from conformer.elements import KCAL_MOL_TO_HARTREE
from conformer.records import SystemRecord
from conformer.systems import System
from conformer_core.accessors import Accessor
from conformer_core.records import RecordStatus
from conformer_core.stages import Link, Stage, StageOptions

from fragment.core.quickPIE import mk_quickPlan_dirty
from fragment.views import View


class AccessorTask:
    args: Tuple
    result: Optional[Any]
    uuid: UUID

    def get_args(self) -> Tuple:
        return self.args

    def set_args(self, *args) -> None:
        self.result = None
        self.args = args

    def get_result(self) -> Any:
        if not self.done():
            raise Exception("Task was not completed!")
        return self.result

    def set_result(self, res: Any) -> None:
        self.result = res

    def done(self) -> bool:
        return self.result is not None

    def __init__(self, *args) -> None:
        self.uuid = uuid4()
        self.set_args(*args)

    def __hash__(self) -> int:
        self.uuid.__hash__()

    def __eq__(self, __value: "AccessorTask") -> bool:
        self.uuid == __value.uuid


class DeltaPropertyTask(AccessorTask):
    supersystem: System
    result: SystemRecord
    coefs: Dict[System, int]

    def __init__(
        self,
        components: List[FrozenSet[int]],
        subsys_fn: Callable[[FrozenSet[int]], System],
        *args: Any,
    ) -> None:
        super().__init__(components, subsys_fn, *args)
        supersystem_key = frozenset.union(*components)
        supersystem = subsys_fn(supersystem_key)

        plan = mk_quickPlan_dirty(components)
        self.coefs = {supersystem: 1}
        for k, v in plan.items():
            self.coefs[subsys_fn(k)] = -v

        self.result = SystemRecord(
            stage=Stage(),
            system=supersystem,
        )

    def update(self, record: SystemRecord) -> None:
        # Handle errors gracefully
        coef = self.coefs.pop(record.system)

        if record.status == RecordStatus.FAILED:
            self.result.status = RecordStatus.FAILED
            self.result.meta['error'] = record.meta.get('error')
            self.result.meta['failed_system'] = record.system.fingerprint
            # Cancel other jobs? How?
            return

        self.result.add_into(record, coef=coef)
        if not self.coefs:
            self.result.status = RecordStatus.COMPLETED

    def done(self) -> bool:
        if self.result.status is RecordStatus.FAILED:
            return True
        return not self.coefs
        # There is currently no go way to prempt this kind of job
        return self.result.status != RecordStatus.PENDING


class DeltaPropertyAccessor(Stage, Accessor):
    driver: Driver = Link()
    accessor: DriverAccessor
    running: Dict[System, List[DeltaPropertyTask]]

    def __init_stage__(self):
        self.accessor = get_accessor(self.driver)
        self.running = {}

    def submit(self, components, subsys_fn, *args) -> None:
        self.num_submitted += 1
        task = DeltaPropertyTask(components, subsys_fn, *args)

        for s in task.coefs.keys():
            try:
                self.running[s].append(task)
            except KeyError:
                self.running[s] = [task]
                self.accessor.submit(s)

    def process_result(self, t: DeltaPropertyTask) -> Any:
        return t.get_args(), t.get_result()

    def churn(self) -> None:
        for s, r in self.accessor.get_completed():
            for t in self.running.pop(s):
                if t.done():
                    continue # It's already been returned!
                    # This happens when there is a failed calculation.
                    # I cannot think of a clean way to clear this out/cancel

                t.update(r)
                if t.done():
                    self.out_queue.put(self.process_result(t))

class DeltaProperyFilter(DeltaPropertyAccessor):

    class Options(StageOptions):
        T: Dict[int, float]
        default_T: int | None = None
        property: str = "total_energy"
    opts: Options

    args_lookup: Dict[int, Tuple]
    T: Dict[int, float]

    def __init_stage__(self):
        super().__init_stage__()
        self.args_lookup = {}

        if self.opts.default_T is not None:
            default = self.opts.default_T * KCAL_MOL_TO_HARTREE
        else:
            default = None
        
        self.T = DefaultDict(lambda: default)
        for o, t in self.opts.T.items():
            self.T[o] = t * KCAL_MOL_TO_HARTREE

    def process_result(self, t: DeltaPropertyTask) -> bool:
        _, __, arg_i, T = t.get_args()
        result = t.get_result().properties[self.opts.property]
        return self.args_lookup.pop(arg_i), abs(result) > T

    def submit(
        self, view: View, primaries: Iterable[FrozenSet[int]], order: int
    ) -> None:
        arg_i = self.num_submitted
        args = (view, primaries, order)
        T = self.T[order]
        if T is None:
            self.num_submitted += 1
            self.out_queue.put((args, True)) # It always passes
        else:
            self.args_lookup[arg_i] = args
            aux = [frozenset.union(*c) for c in combinations(primaries, order - 1)]
            super().submit(aux, view.get_system, arg_i, T)
