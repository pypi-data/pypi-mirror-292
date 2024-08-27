#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from itertools import combinations
from typing import FrozenSet, Iterable, Optional

from conformer.systems import System
from conformer_core.stages import FilterStack, ModStack, Stack, Stage, StageOptions

from fragment.core.quickPIE import compress_up
from fragment.db.models import DBView
from fragment.views import Key, KeySet, View


class FragmenterOptions(StageOptions):
    clean_zeros: bool = False  # NOTE: Only implemented for aux framenters


class Fragmenter(Stage):
    Options = FragmenterOptions

    subsystem_mods = Stack()
    pre_mods = ModStack()
    post_mods = ModStack()


class PrimaryFragmenter(Fragmenter):
    def new_view(self, sys: System, primaries: Iterable[FrozenSet[int]]) -> View:
        sys_name = f"{self.name}({sys.name})"
        view = View.new_primary(self, primaries, name=sys_name)
        view.bind_system(sys)
        return view

    def view_from_db(self, sys: System) -> View | None:
        if not self._use_db:
            return
        if self._saved:  # Only query if this Fragmenter has been saved
            return DBView.get_view_by_originator(
                self,
                sys,
                0,  # Primary Views have order == 0
                WORLD=self._world,  # Share the Fragmenter World
                REGISTRY={
                    self.__class__.__name__: self.__class__
                },  # This shouldn't need to be accessed
            )
        return None

    def view_to_db(self, view: View) -> View:
        if not self._use_db:
            return
        DBView.add_views([view])

    def __call__(self, sys: System) -> View:
        if not sys.is_canonized:
            sys = sys.canonize()
        # Check if we have a copy in the database
        view = self.view_from_db(sys)
        if view is not None:  # Add force flag
            return view

        # sys = self.pre_mods(sys)
        view = self.fragment(sys)
        # view = self.post_mods(view)

        self.view_to_db(view)
        return view

    def fragment(self, sys: System) -> View:
        ...


class AuxFragmenter(Fragmenter):
    filters = FilterStack()

    def view_name(self, view: View, order: int) -> View:
        return f"{view.name}--{self.name}({order})"

    def view_from_db(self, p_view: View, order: int) -> View | None:
        if not self._use_db:
            return
        if self._saved:  # Only query if this Fragmenter has been saved
            return DBView.get_view_by_originator(
                self,
                p_view.supersystem,
                order,  # Primary Views have order == 0
                WORLD=self._world,  # Share the Fragmenter World
                REGISTRY={
                    self.__class__.__name__: self.__class__
                },  # This shouldn't need to be accessed
            )
        return None

    def view_to_db(self, view: View) -> str:
        if not self._use_db:
            return
        DBView.add_views([view])

    def combinate(self, p_view: View, order: int) -> View:
        ...

    def __call__(self, p_view: View, order: int) -> View:
        if p_view.supersystem is not None:
            assert p_view.supersystem.is_canonized
        view = self.view_from_db(p_view, order)
        if view:
            return view

        # p_view, order = self.pre_mods(p_view, order)
        view = self.combinate(p_view, order)
        # view = self.post_mods(view)

        if self.opts.clean_zeros:
            view.tree.clean_zeros()
        if not view.tree.is_complete():
            raise ValueError("Fragmentation scheme does not reproduce the supersystem.")
        
        self.view_to_db(view)
        return view


class FullFragmenter(AuxFragmenter):
    filters = None  # There is no filtering allowed for this puppy

    def combinate(self, p_view: View, order: int) -> View:
        # Quicklky do non-overlapping fragments
        if p_view.primaries == p_view.primatives:
            view = View.new_MBE_auxiliary(
                self, p_view, order, name=self.view_name(p_view, order)
            )

        # Spend more time brute-forcing overlapping fragments :(
        else:
            view = View.new_auxiliary(
                self, p_view, order, name=self.view_name(p_view, order)
            )
            for comb in combinations(view.primaries, order):
                view.add(Key.union(*comb))

        return view


class TopDownFragmenter(AuxFragmenter):
    def combinate(self, p_view: View, order: int) -> View:
        # TODO: Implement without complete combos.
        # May be simpler and cheaper to check if fragment is in tree
        # Do the old reliable way :)
        view = View.new_auxiliary(
            self, p_view, order, name=self.view_name(p_view, order)
        )

        root_fragments = self.complete_combos(view.primaries, view, order)
        for k in compress_up(root_fragments):
            view.add(k)

        return view

    def complete_combos(
        self,
        to_add: KeySet,
        view: View,
        order: int,
        fragments: Optional[KeySet] = None,
        checked: Optional[KeySet] = None,
    ) -> KeySet:
        if fragments is None:
            fragments = KeySet()
        if checked is None:
            checked = KeySet()  # Maybe just build the view?

        # TODO: Parallelize with accessors
        for frags in combinations(to_add, order):
            key = Key.union(*frags)
            if key in checked:
                continue  # Skip. It's already there
            else:
                checked.add(key)  # Skip next time

            if order == 1:  # All first order fragments get added
                fragments.add(key)  # TODO: Why not just add it to the view?
            elif self.filters(view, frags, order)[1]:  # Filtering
                fragments.add(key)
            else:
                self.complete_combos(frags, view, order - 1, fragments, checked)

        return fragments

    # def add_fragments(self, view: View, *frags: Key) -> KeySet:
    #     order = len(frags)
    #     key = frozenset.union(*frags)

    #     if order == 1:
    #         return set(frags)

    #     # TODO: Parallelize this with accessors
    #     if filter(view, frags):  # Keep if True
    #         return set((key,))

    #     return self.complete_combos(fags, order - 1, filter)


class BottomUpFragmenter(AuxFragmenter):
    class Options(FragmenterOptions):
        M: int = 1

    def combinate(self, p_view: View, order: int) -> View:
        """Adds nodes layer by layer.

        Only fragments with N - M parents in the tree are allowed to be added.
        For example ab + ac + bc -> abc is allowed but ab + ac -!> abc for M = 0
        """
        view = View.new_auxiliary(
            self, p_view, order=order, name=self.view_name(p_view, order)
        )
        # Congratulations! We have level one completed!
        for f in p_view.primaries:
            view.add(f)

        if order != 1:
            # Add remaining levels
            self.add_bottom_up_level(view, order, 2)
        return view

    def add_bottom_up_level(
        self,
        view: View,
        o: int,  # Target order
        m: int,  # The current level
    ) -> None:
        # TODO: Find a more efficient way to do this
        _new_hl: KeySet = set()
        new_ll_nodes = 1  # New low-level nodes
        new_hl_nodes = 1  # New high-level nodes
        MAX_ITER = 1
        # _M = max(m - 2, 0)
        _M = self.opts.M
        # print(f"{m} -> {_M}")
        itr = 1

        while new_ll_nodes and new_hl_nodes and MAX_ITER >= itr:
            to_add: KeySet = set()
            to_add_missing: KeySet = set()

            # This is a brute force check. We can probably do this much more
            # efficiently with the Tree (finally, a use!)
            for com in combinations(view.primaries, m):
                # Check that all parents exist in the tree. They don't have to have
                # non-zero coefs (?) but should be there
                mc = 0
                missing = set()
                hl_key = frozenset.union(*(com))
                if hl_key in _new_hl:
                    continue  # Don't duplicate work

                skip = False
                for children in combinations(com, m - 1):
                    pk = frozenset.union(*(children))
                    if pk not in view:
                        mc += 1
                        missing.add(pk)
                        if mc > _M:
                            skip = True
                            # break

                if not skip and self.filters(view, com, m)[1]:
                    to_add_missing.update(missing)
                    to_add.add(hl_key)

            # Add the missing high-level terms and new keys
            prev_nodes = len(view)

            for k in to_add:
                view.add(k)

            new_hl_nodes = len(to_add)
            new_ll_nodes = len(view) - prev_nodes - new_hl_nodes
            _new_hl.update(to_add)  # Keep track of which HL nodes exist
            # print(
            #     f"itr={itr}\tm={m}\tnhl={new_hl_nodes}\tnll={new_ll_nodes}\tmll={len(to_add_missing)}"
            # )
            itr += 1

        # Just keep going until we have nothing left to add
        if m == o or len(_new_hl) == 0:
            return view
        else:
            return self.add_bottom_up_level(view, o, m + 1)


# class AbstractFragmenter:

#     def generate_aux_fragments(
#         self,
#         primary_view: View,
#         order: int,
#         app: FilterApplicator = None,
#     ) -> View:
#         """Workhorse function which groups for generating aux fragments

#         Args:
#             primary_view (:class:`.View`): Primary view on which to base the
#                 primary fragments
#             order (int): Fragment generation order
#             app (FilterApplicator, optional): Filter function for aux fragment
#                 creation. Defaults to None.

#         Raises:
#             Exception: Raised when order is insuffiencet to create aux fragments
#             Exception: Raised when atoms do not have a DB id.

#         Returns:
#             View: View containing auxiliary fragments with properly weighted
#                 view coeficients.
#         """

#         # Validate the inputs and make sure we can do this
#         if len(primary_view.fragments) < order:
#             raise Exception("The number of primary fragments is less than the order.")

#         for f in primary_view.fragments:
#             if f.key is None:
#                 raise Exception("Cannot perform fragmentation on un-instantiated atoms")

#         if self.combinator is None:
#             tree = self._auto_aux_fragments(primary_view, order, app)
#         elif self.combinator == "top_down":
#             tree = self._overlapping_aux_fragments(primary_view, order, app)
#         elif self.combinator == "bottom_up":
#             tree = self._bottom_up_aux_fragments(primary_view, order, app)
#         elif self.combinator == "mbe":
#             tree = self._quick_aux_fragments(primary_view, order)
#         else:
#             raise ValueError(f"Unknow fragmentation combinator '{self.combinator}'")

#         # Validate
#         if not tree.is_complete():
#             raise ValueError("Fragmentation scheme does not reproduce the supersystem.")

#         return self.aux_frags_from_tree(primary_view, tree, order)

#     def aux_frags_from_tree(
#         self, primary_view: View, tree: PIETree, order: int
#     ) -> View:
#         aux_frags = self.new_aux_view(primary_view, order)
#         prim_frags = primary_view.fragments.sets
#         coefs = []
#         systems = []

#         for node, data in tree:
#             # Annotate with primary fragment information
#             primaries = [p for p in prim_frags if data["data"].issuperset(p)]
#             data["primaries"] = primaries
#             data["order"] = len(primaries)

#             # Extract that information to to build View
#             systems.append(System(aux_frags.supersystem.atoms.filter(ids=node)))
#             coefs.append(data["coef"])

#         aux_frags.fragments.add(*systems, coefs=coefs)
#         for f in aux_frags.fragments:
#             f.viewcoef.order = tree[f.key]["order"]
#         aux_frags.dep_tree = tree  # This needs to change

#         return aux_frags

#     def _auto_aux_fragments(
#         self, p_view: View, order: int, app: FilterApplicator
#     ) -> PIETree:
#         if app.is_empty() and not roots_overlap(p_view.fragments.keys):
#             tree = self._quick_aux_fragments(p_view, order)
#         else:
#             tree = self._overlapping_aux_fragments(p_view, order, app)
#         return tree

#     def _quick_aux_fragments(
#         self,
#         p_view: View,
#         order: int,
#     ) -> PIETree:
#         return PIETree.from_MBE_primary_frags(p_view.fragments.sets, order)

#     def _bottom_up_aux_fragments(
#         self,
#         p_view: View,
#         order: int,
#         app: FilterApplicator,
#     ) -> PIETree:
#         """Adds nodes layer by layer.

#         Only fragments with all parents in the tree are allowed to be added.
#         For example ab + ac + bc -> abc is allowed but ab + ac -!> abc
#         """
#         tree = PIETree.from_primaries(p_view.fragments.sets, add=True)
#         # Congratulations! We have level one completed!

#         if order != 1:
#             # Add remaining levels
#             self._add_bottom_up_level(p_view.fragments, tree, app, order, 2)
#         return tree

#     def _add_bottom_up_level(
#         self,
#         p_frags: List[System],
#         tree: PIETree,
#         filter: FilterApplicator,
#         o: int,  # Target order
#         m: int,  # The current level
#     ) -> PIETree:
#         # TODO: Find a more efficient way to do this
#         _new_hl: quickNodeSet = set()
#         new_ll_nodes = 1  # New low-level nodes
#         new_hl_nodes = 1  # New high-level nodes
#         MAX_ITER = 1
#         # _M = max(m - 2, 0)
#         _M = self.bu_missing
#         # print(f"{m} -> {_M}")
#         itr = 1

#         while new_ll_nodes and new_hl_nodes and MAX_ITER >= itr:
#             to_add: quickNodeSet = set()
#             to_add_missing: quickNodeSet = set()

#             # This is a brute force check. We can probably do this much more
#             # efficiently with the Tree (finally, a use!)
#             for com in combinations(p_frags, m):
#                 # Check that all parents exist in the tree. They don't have to have
#                 # non-zero coefs (?) but should be there
#                 mc = 0
#                 missing = set()
#                 hl_key = frozenset.union(*(c.key for c in com))
#                 if hl_key in _new_hl:
#                     continue  # Don't duplicate work

#                 skip = False
#                 for children in combinations(com, m - 1):
#                     pk = frozenset.union(*(c.key for c in children))
#                     if not pk in tree:
#                         mc += 1
#                         missing.add(pk)
#                         if mc > _M:
#                             skip = True
#                             # break

#                 if not skip and filter(*com):
#                     to_add_missing.update(missing)
#                     to_add.add(frozenset.union(*(c.key for c in com)))

#             # Add the missing high-level terms and new keys
#             prev_nodes = len(tree.tree)

#             for k in to_add:
#                 tree.expand(k)

#             new_hl_nodes = len(to_add)
#             new_ll_nodes = len(tree.tree) - prev_nodes - new_hl_nodes
#             _new_hl.update(to_add)  # Keep track of which HL nodes exist
#             # print(
#             #     f"itr={itr}\tm={m}\tnhl={new_hl_nodes}\tnll={new_ll_nodes}\tmll={len(to_add_missing)}"
#             # )
#             itr += 1

#         # Just keep going until we have nothing left to add
#         if m == o or len(_new_hl) == 0:
#             return tree
#         else:
#             return self._add_bottom_up_level(p_frags, tree, filter, o, m + 1)

#     def _overlapping_aux_fragments(
#         self, p_view: View, order: int, app: FilterApplicator
#     ) -> PIETree:
#         # TODO: Implement without complete combos.
#         # May be simpler and cheaper to check if fragment is in tree
#         # Do the old reliable way :)
#         tree = PIETree.from_primaries(p_view.fragments.sets)

#         root_fragments = complete_combos(p_view.fragments, order, app)
#         for k in compress_up(root_fragments):
#             tree.expand(k)
#         tree.clean_zeros()

#         return tree
