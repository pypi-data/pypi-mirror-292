#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from typing import Dict, FrozenSet

from conformer.db.models import DBSystem
from conformer.stages import get_system
from conformer.systems import System

from fragment.core.PIETree import PIETree
from fragment.db.models import DBSystemToView, DBView
from fragment.views import View, ViewType

from .abstract import Fragmenter


def dict_add(d: Dict, k: FrozenSet, v: int):
    try:
        d[k] += v
    except KeyError:
        d[k] = v


class InteractionEnergy(Fragmenter):
    """Transforms a complete view to calculate the interaction energy between two
    subsystems A and B
    """

    def new_view(self, parent: View, A_sys: System, B_sys: System) -> View:
        graph = parent.tree.tree.copy()
        tree = PIETree(
            graph,
            parent.tree.primatives,
            parent.tree.primaries,
            parent.tree.target
        )

        return View(
            name=f"{parent.name}--{self.name}({A_sys.name}, {B_sys.name})",
            tree=tree,
            parent=parent,
            order=parent.order,
            type=ViewType.AUXILIARY,
            fragmenter=self,
            supersystem=parent.supersystem,
        )

    def view_from_db(self, p_view: View, A_sys: System, B_sys: System) -> View | None:
        if not self._use_db:
            return
        if self._saved:  # Only query if this Fragmenter has been saved


            # Update system ids
            DBSystem.get_system_DBID([p_view.supersystem, A_sys, B_sys])

            if not A_sys._saved or not B_sys._saved or not p_view._saved:
                return None

            AB = DBSystemToView.alias()
            A = DBSystemToView.alias()
            B = DBSystemToView.alias()

            # Get the view id
            view_id = (DBView
                .select(DBView.id)
                .join(AB).switch()
                .join(A).switch()
                .join(B).switch()
                .where(
                    DBView.fragmenter_id == self._saved,
                    DBView.parent_id == p_view._saved,
                    AB.system_id == p_view.supersystem._saved,
                    A.system_id == A_sys._saved,
                    B.system_id == B_sys._saved,
                )
            ).first()
            if view_id:
                view_id = view_id.id
                view = DBView.get_views([view_id], self._world, {})[view_id]
                view.bind_system(p_view.supersystem)
                return view
        return None

    def view_to_db(self, view: View, A_sys: System, B_sys: System) -> None:
        if not self._use_db:
            return
        DBView.add_views([view])
        DBSystem.add_systems([A_sys, B_sys])
        DBSystemToView.link_views_to_systems([
            (view, view.supersystem, True),
            (view, A_sys, True),
            (view, B_sys, True),
        ])

    def __call__(self, AB_view: View, A_sys: System | str, B_sys: System | str) -> View:
        AB_sys = AB_view.supersystem
        A_sys = get_system(A_sys)
        B_sys = get_system(B_sys)

        # TODO: Check that this works with periodic systems
        A_idxs = frozenset((i[0] for i in AB_sys.join_map(A_sys)))
        B_idxs = frozenset((i[0] for i in AB_sys.join_map(B_sys)))

        # Check that the sub-systems don't overlap
        assert not A_idxs.intersection(B_idxs)
        assert len(A_idxs.union(B_idxs)) == len(AB_sys)

        # Check if we have an existing system
        view = self.view_from_db(AB_view, A_sys, B_sys)
        if view:
            return view

        to_sub: Dict[FrozenSet, int] = {}
        IE_view = self.new_view(AB_view, A_sys, B_sys)

        for n, d in IE_view.iter_data():
            c = -d['coef']

            A_n = A_idxs.intersection(n)
            if A_n:
                dict_add(to_sub, A_n, c)

            B_n = B_idxs.intersection(n)
            if B_n:
                dict_add(to_sub, B_n, c)

        # Subtract everything
        for k, c in to_sub.items():
            try:
                IE_view[k]['coef'] += c
            except KeyError:
                # Add to the tree WITHOUT accounting for overlaps
                IE_view.tree.update_or_add(k, coef=c)
        
        # Should be net zero for interaction energy
        for o in IE_view.tree.count_members().values():
            assert o == 0

        self.view_to_db(IE_view, A_sys, B_sys)
        return IE_view
