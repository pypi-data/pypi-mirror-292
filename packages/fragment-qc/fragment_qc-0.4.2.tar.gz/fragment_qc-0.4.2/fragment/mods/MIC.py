#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from conformer.mods.MIC import valid_MIC_system
from conformer.systems import System
from conformer_core.accessors import Accessor
from conformer_core.stages import Stage, StageOptions


class ValidMICSystemFilter(Stage, Accessor):

    class Options(StageOptions):
        scale: float = 1.2
    opts: Options

    def churn(self) -> System:
        while not self.in_queue.empty():
            view, primaries, order = self.in_queue.get()
            subsys = view.get_system(frozenset.union(*primaries))

            # TODO: Handle capping and ghost atom edge cases?
            assert all((a.is_physical for a in subsys)), "All atoms must be physical"

            # Return filter values 
            self.out_queue.put((
                (view, primaries, order),
                valid_MIC_system(subsys)
            ))
