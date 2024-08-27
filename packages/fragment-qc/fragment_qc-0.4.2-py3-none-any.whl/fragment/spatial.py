#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from functools import lru_cache
from itertools import combinations
from typing import Callable, Dict, FrozenSet, Iterator, Mapping, Tuple

from conformer import spatial
from conformer.systems import System

from fragment.views import View

Key = FrozenSet[int]


class ViewDistanceMatrix(Mapping):
    """
    View wrapper for system matrix.
    """

    dm: spatial.SystemDistanceMatrix
    primary_to_idx: Dict[Key, int]

    def __init__(
        self,
        view: View,
        metric: Callable[[System, System], float],
        use_mods: bool = None,
    ) -> None:
        systems_to_key = {view.get_system(k, use_mods): k for k in view.primaries}
        self.dm = spatial.system_distance_matrix(
            systems_to_key.keys(), metric, view.supersystem
        )
        self.primary_to_idx = {
            k: self.dm.system_to_idx[s] for s, k in systems_to_key.items()
        }

    def __getitem__(self, key: Tuple[System | Key | int, System | Key | int]) -> float:
        return self.dm[self.idx(*key)]

    def __iter__(self) -> Iterator:
        # What make sense? The keys are not ideal
        for s1, s2 in combinations(self.systems, 2):
            yield s1, s2, self[s1, s2]

    def __len__(self) -> int:
        return self.dm.__len__()

    def idx(self, s1: System | Key | int, s2: System | Key | int) -> int:
        """Convert keys to ints"""
        if isinstance(s1, frozenset):  # Is a frozoneset
            i1 = self.primary_to_idx[s1]
        else:
            i1 = s1

        if isinstance(s2, frozenset):
            i2 = self.primary_to_idx[s2]
        else:
            i2 = s2

        return i1, i2


@lru_cache()
def view_distance_matrix(
    view: View, metric: Callable, use_mods=False
) -> ViewDistanceMatrix:
    """Returns distance matrix for a view"""
    return ViewDistanceMatrix(view, metric, use_mods)
