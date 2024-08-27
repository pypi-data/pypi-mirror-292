#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import conformer.spatial as spatial
import networkx as nx
from conformer.systems import System, is_join

from fragment.fragmenting.abstract import FragmenterOptions, PrimaryFragmenter
from fragment.views import View


class CovalentComponentsFragmenter(PrimaryFragmenter):
    class Options(FragmenterOptions):
        scale: float = 1.1

    def fragment(self, system: System) -> View:
        bonding_graph = spatial.bonding_graph(system, self.opts.scale)
        primaries = []
        for comp in nx.connected_components(bonding_graph):
            primary_key = frozenset((i for i, _ in system.join_map(comp, is_join)))
            primaries.append(primary_key)
        return self.new_view(system, primaries)
