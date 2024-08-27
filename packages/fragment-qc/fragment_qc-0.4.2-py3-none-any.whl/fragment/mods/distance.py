#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from enum import Enum
from itertools import combinations
from typing import Callable, DefaultDict, Dict, FrozenSet, List

import numpy as np
from conformer import spatial
from conformer_core.accessors import Accessor
from conformer_core.stages import Stage, StageOptions

from fragment.spatial import ViewDistanceMatrix, view_distance_matrix


class DistanceMethod(Enum):
    closest = "closest"
    MIC_closest = "MIC_closest"
    COM = "COM"
    MIC_COM = "MIC_COM"


def max_distance(dm: ViewDistanceMatrix, fragments: List[FrozenSet[int]]) -> bool:
    dists = [dm[i, j] for i, j in combinations(fragments, 2)]
    return np.max(dists)


def nearest_neighbor_distance(dm: ViewDistanceMatrix, fragments: List[FrozenSet[int]]) -> bool:
    r_max = 0.0
    sys_r_max = np.max(dm.dm.data)

    # Could this be more efficient?
    for i, f1 in enumerate(fragments):
        r_min = sys_r_max
        for j, f2 in enumerate(fragments):
            if i == j:
                continue
            r = dm[f1, f2]
            if r < r_min:
                r_min = r

        if r_min > r_max:
            r_max = r_min

    return r_max


class DistanceOptions(StageOptions):
    r: float | Dict[int, float]
    default_r: float | None = None
    method: DistanceMethod = DistanceMethod.MIC_closest
    use_mods: bool = False


class DistanceFilter(Stage, Accessor):
    Options = DistanceOptions
    opts: Options

    r: DefaultDict[int, float | None]

    dm_metric: Callable
    distance_fn: Callable

    def __init_stage__(self):
        super().__init_stage__()
        if isinstance(self.opts.r, dict):
            r = self.opts.r
            default_r = self.opts.default_r
        else:
            r = {}
            default_r = self.opts.r

        self.r = DefaultDict(lambda: default_r)
        self.r.update(r)

        # Load distance matrix methods
        if self.opts.method == DistanceMethod.COM:
            self.dm_metric = spatial.system_COM_distance
        elif self.opts.method == DistanceMethod.MIC_COM:
            self.dm_metric = spatial.system_MIC_COM_distance
        elif self.opts.method == DistanceMethod.closest:
            self.dm_metric = spatial.system_CA_distance
        else:
            self.dm_metric = spatial.system_MIC_CA_distance

    def churn(self):
        while not self.in_queue.empty():
            args = self.in_queue.get()
            view, primaries, order = args

            r_cut = self.r[order]
            if r_cut is None:
                self.out_queue.put((args, True))
            else:
                dm = view_distance_matrix(view, self.dm_metric, self.opts.use_mods)
                r = self.distance_fn(dm, primaries)
                self.out_queue.put((args, r < r_cut))

            self.in_queue.task_done()


class MaxDistanceFilter(DistanceFilter):
    distance_fn = staticmethod(max_distance)


class NearestNeighborDistanceFilter(DistanceFilter):
    distance_fn = staticmethod(nearest_neighbor_distance)
