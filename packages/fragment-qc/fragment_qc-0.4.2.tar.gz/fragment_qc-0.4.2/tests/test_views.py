#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from datetime import datetime
from textwrap import dedent
from uuid import UUID

from conformer.systems import Atom, System

# from fragment.db.procedures import add_view, get_view_by_id, get_view_by_order
from fragment.db.models import (
    DBSystemToView,
    DBView,
    DBViewEdge,
    DBViewNode,
    DBViewRecord,
)
from fragment.fragmenting.abstract import Fragmenter
from fragment.views import Key, KeySet, View, ViewRecord, ViewType
from tests import FragmentTestCase

PRIMARIES = [
    Key([0, 1, 4]),
    Key([1, 2, 4]),
    Key([2, 3, 4]),
    Key([3, 0, 4]),
]

PRIMARY_SET = KeySet(PRIMARIES)


class ViewTestCases(FragmentTestCase):
    def setUp(self) -> None:
        self.SYSTEM = System.from_tuples(
            (("H", float(i), float(i), float(i)) for i in range(5))
        )

    def test_constructors(self):
        p_view = View.new_primary(Fragmenter(), PRIMARY_SET, name="primary_view")
        self.assertEqual(p_view.name, "primary_view")
        self.assertTrue(p_view.tree)
        self.assertTrue(p_view.tree.primaries)
        self.assertTrue(p_view.tree.primatives)
        self.assertEqual(p_view.type, ViewType.PRIMARY)

        # Should not expose the field descriptor
        self.assertIsInstance(p_view.name, str)
        self.assertIsInstance(p_view.id, UUID)
        self.assertEqual(len(p_view), 9)

        a_view = View.new_auxiliary(Fragmenter(), p_view, 3)
        self.assertIs(a_view.parent, p_view)
        self.assertIsNot(p_view.tree, a_view.tree)
        self.assertSetEqual(p_view.tree.primaries, a_view.tree.primaries)
        self.assertEqual(a_view.type, ViewType.AUXILIARY)

        # Should not expose the field descriptor
        # Issue arising from Attr dataclass being used.
        self.assertIsInstance(a_view.name, str)
        self.assertIsInstance(a_view.id, UUID)
        self.assertEqual(len(a_view), 9)

    def test_key(self):
        view = View.new_primary(Fragmenter(), PRIMARY_SET, name="primary_view")
        view.bind_system(self.SYSTEM)

        self.assertIsInstance(view._key([1, 2, 3]), frozenset)
        self.assertSetEqual(view._key([1, 2, 3]), {1, 2, 3})
        self.assertSetEqual(view._key(Key([1, 2, 3])), {1, 2, 3})
        # Depricated!
        # self.assertSetEqual(view._key(self.SYSTEM.subsystem([1, 2, 3])), {1, 2, 3})

    def test_views(self):
        view = View.new_primary(Fragmenter(), PRIMARY_SET, name="primary_view")
        self.assertIsInstance(view.name, str)
        view.bind_system(self.SYSTEM)

        self.assertSetEqual(
            view.get_primaries(Key.union(*PRIMARIES[0:1])), set(PRIMARIES[0:1])
        )
        self.assertSetEqual(
            view.get_primatives(Key.union(*PRIMARIES[0:1])),
            set([Key([0]), Key([1]), Key([4])]),
        )

        # We technically haven't added any of our nodes yet.
        self.assertSetEqual(
            {0}, {d["coef"] for k, d in view.iter_data(include_zeros=True)}
        )

        for f in PRIMARIES:
            view.add(f)

        # Test iterators... I'm not sure how to do this...
        key_coefs = {(k, d["coef"]) for k, d in view.iter_data(include_zeros=True)}
        self.assertEqual(
            {
                (Key({0}), 0),
                (Key({1}), 0),
                (Key({2}), 0),
                (Key({3}), 0),
                (Key({4}), 1),
                (Key({0, 4}), -1),
                (Key({1, 4}), -1),
                (Key({2, 4}), -1),
                (Key({3, 4}), -1),
                (Key({0, 1, 4}), 1),
                (Key({0, 3, 4}), 1),
                (Key({1, 2, 4}), 1),
                (Key({2, 3, 4}), 1),
            },
            key_coefs,
        )

        for s, d in view.iter_systems():
            self.assertEqual(s, self.SYSTEM.subsystem(d["data"]))

        self.assertSetEqual(
            {p for p in view.get_parents(Key({0, 4}))},
            {Key({0}), Key({4})},
        )
        self.assertSetEqual(
            {p for p in view.get_ancestors(Key({0, 1, 4}))},
            {Key({0}), Key({1}), Key({4}), Key({0, 4}), Key({1, 4})},
        )

        self.assertSetEqual(
            {p for p in view.get_children(Key({0, 4}))},
            {Key({0, 1, 4}), Key({0, 3, 4})},
        )
        self.assertSetEqual(
            {p for p in view.get_descendents(Key({0}))},
            {Key({0, 4}), Key({0, 1, 4}), Key({0, 3, 4})},
        )

        self.assertSetEqual(
            {p for p in view.active_edge()},
            {Key({0, 1, 4}), Key({0, 3, 4}), Key({1, 2, 4}), Key({2, 3, 4})},
        )

        # Test get system
        self.assertEqual(view.get_system([1, 2, 3]), self.SYSTEM.subsystem([1, 2, 3]))
        A = Atom("C", [0, 0, 0])

        def test_ssm(ss, k, s: System):
            s.add_atoms(Atom("C", [0, 0, 0]))
            return s

        view.fragmenter.subsystem_mods.append(test_ssm)
        view.system_cache.clear()
        self.assertIn(A, view.get_system([1, 2, 3]))

    def test_db(self):
        p_view = View.new_primary(
            Fragmenter(name="primary"), PRIMARY_SET, name="primary_view"
        )
        a_view = View.new_auxiliary(Fragmenter(name="aux"), p_view, 3, name="aux_view")
        for f in PRIMARIES:
            a_view.add(f)

        p_view.bind_system(self.SYSTEM)
        a_view.bind_system(self.SYSTEM)

        DBView.add_views([a_view])  # Don't include the p_view. Should still save

        # Check that the DB IDs have been saved
        self.assertTrue(a_view._saved)
        self.assertTrue(p_view._saved)
        self.assertTrue(a_view.supersystem._saved) # Note, will not === self.SYSTEM which is uncanonnized
        self.assertTrue(a_view.fragmenter._saved)
        self.assertTrue(p_view.fragmenter._saved)

        # Check everything is saved
        self.assertEqual(DBView.select().count(), 2)
        self.assertEqual(DBViewNode.select().count(), 24)
        self.assertEqual(DBViewEdge.select().count(), 36)
        self.assertEqual(DBSystemToView.select().count(), 2)

        # Check retrieval
        WORLD = {}
        REGISTRY = {Fragmenter.__name__: Fragmenter}

        db_view = DBView.get_views([a_view._saved], WORLD, REGISTRY)[a_view._saved]

        self.assertEqual(a_view, db_view)
        self.assertEqual(p_view, db_view.parent)

        # Check nodes
        a = {(n, d["coef"]) for n, d in a_view}
        b = {(n, d["coef"]) for n, d in db_view}
        self.assertSetEqual(a, b)

        # Check edges
        e_a = {e for e in a_view.tree.tree.edges}
        e_b = {e for e in db_view.tree.tree.edges}
        self.assertEqual(e_a, e_b)

        self.assertDictEqual(a_view.meta, db_view.meta)

        # Test get from originator
        self.SYSTEM._saved = 0
        db_view = DBView.get_view_by_originator(
            a_view.fragmenter, self.SYSTEM, 3, WORLD, REGISTRY
        )

        self.assertEqual(a_view, db_view)

        # Should get None for none-existant order
        db_view = DBView.get_view_by_originator(
            a_view.fragmenter, self.SYSTEM, 2, WORLD, REGISTRY
        )
        self.assertEqual(None, db_view)

        # Test DB View record
        rec1 = ViewRecord(
            stage=Fragmenter(name="name"), system=self.SYSTEM, view=a_view
        )
        DBViewRecord.add_or_update_view_record([rec1])

        records = DBViewRecord.get_view_record(rec1.stage, a_view, [self.SYSTEM])
        rec1_db = records[self.SYSTEM]
        self.assertEqual(rec1.id, rec1_db.id)
        self.assertEqual(rec1._saved, rec1_db._saved)

        # Check that it will retrieve existing record
        rec1_copy = ViewRecord(stage=rec1.stage, system=self.SYSTEM, view=a_view)
        DBViewRecord.get_record_DBID([rec1_copy])
        self.assertEqual(rec1.id, rec1_copy.id)
        self.assertEqual(rec1._saved, rec1_copy._saved)

    def test_summary(self):
        p_view = View.new_primary(
            Fragmenter(name="primary"), PRIMARY_SET, name="primary_view"
        )
        a_view = View.new_auxiliary(Fragmenter(name="aux"), p_view, 3, name="aux_view")
        for f in PRIMARIES:
            a_view.add(f)

        a_view.id = UUID(int=0)
        a_view.bind_system(self.SYSTEM)
        rec = ViewRecord(stage=Fragmenter(name="name"), system=self.SYSTEM, view=a_view)
        rec.id = UUID(int=0)
        rec.start_time = datetime(2020, 1, 1)
        fixture = dedent(
            """\
        View Record 00000000-0000-0000-0000-000000000000: 
          View Name: aux_view
          Driver: name
          Fragmenter: aux
          Order: 3
          System: System(formula="H5", name="sys-83f0bc09")
          Created: 2020-01-01T00:00
          Num Fragments: 9
          Status: PENDING
        """
        )
        self.assertEqual(fixture, rec.summarize())
