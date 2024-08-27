#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import numpy as np
from conformer.systems import System

from fragment.fragmenting.abstract import PrimaryFragmenter
from fragment.views import View


class WaterFragmenter(PrimaryFragmenter):
    def fragment(self, system: System) -> View:
        O_atoms = [
            (i, a) for i, a in enumerate(system) if a.t == "O" and a.role.is_physical
        ]
        H_atoms = [
            (i, a) for i, a in enumerate(system) if a.t == "H" and a.role.is_physical
        ]

        # TODO: Support non-OH atoms
        if 2 * len(O_atoms) != len(H_atoms):
            raise Exception("The system does not contain a 1:2 O to H ratio.")

        # This could be improved with a KDTree but it's fine for now
        primaries = set()
        for O in O_atoms:
            H_atoms.sort(key=lambda x: np.linalg.norm(O[1].r - x[1].r))
            primaries.add(frozenset((O[0], H_atoms[0][0], H_atoms[1][0])))

        return self.new_view(system, primaries)