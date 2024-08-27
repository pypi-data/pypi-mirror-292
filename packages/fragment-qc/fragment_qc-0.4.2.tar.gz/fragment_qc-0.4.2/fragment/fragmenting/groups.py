#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import logging

from conformer.systems import System

from fragment.fragmenting.abstract import PrimaryFragmenter
from fragment.views import View

log = logging.getLogger(__name__)

# TODO: Add GlobMod

class GroupFragmenter(PrimaryFragmenter):
    """
    TODO: Add hetero-atom fragmentation scheme
    """

    def fragment(self, system: System) -> View:
        primaries = {}

        for i, a in enumerate(system):
            try:
                fg = a.meta['frag_group']
            except KeyError:
                raise Exception("Atoms in system lack residue information")
            
            # Add to the groups
            try:
                primaries[fg].append(i)
            except KeyError:
                primaries[fg] = [i]

        # TODO: Add a distance-based glob modifier (Globbing)

        # Combine into windowed fragments
        # TODO: Perform distance based globbing
        # windowed_frags = [[] for _ in range((num_residues - self.window + 1))]
        # for w in range(0, (num_residues - self.window + 1)):
        #     for x in range(self.window):
        #         windowed_frags[w] += residues[w + x]
        return self.new_view(
            system,
            [frozenset(p) for p in primaries.values()]
        )

PDBFragmenter = GroupFragmenter
