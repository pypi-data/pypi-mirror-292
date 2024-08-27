#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from datetime import datetime
from typing import Dict, List, Tuple
from uuid import uuid4

from conformer.db.models import DBSystem
from conformer.systems import System
from conformer.systems import SystemKey as Key
from conformer_core.db.models import (
    DBRecord,
    DBStage,
    KeyField,
    dedup_and_saveable,
    insert_many,
)
from conformer_core.stages import Stage
from peewee import (
    SQL,
    BooleanField,
    CharField,
    CompositeKey,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    UUIDField,
    chunked,
)
from playhouse.sqlite_ext import JSONField

from fragment.core.PIE_common import ROOT
from fragment.core.PIETree import PIETree
from fragment.views import View, ViewRecord, ViewType


class DBView(Model):
    class Meta:
        table_name = "view"

    uuid = UUIDField(default=uuid4, unique=True, index=True)
    name = CharField(max_length=255, null=True, index=True)
    created = DateTimeField(null=False, default=datetime.now)
    meta = JSONField(null=False)

    order = IntegerField(null=True)
    type = IntegerField()
    fragmenter = ForeignKeyField(DBStage, null=False)
    parent = ForeignKeyField("self", null=True)

    @classmethod
    def field_order(cls):
        return (
            cls.uuid,
            cls.name,
            cls.created,
            cls.meta,
            cls.order,
            cls.type,
            cls.fragmenter_id,
            cls.parent_id,
        )

    @classmethod
    def input_tuple(cls, view: View) -> Tuple:
        # Manage issues with parent ids
        if view.parent and view.parent._saved:
            parent_id = view.parent._saved
        else:
            parent_id = None

        return (
            view.id,
            view.name,
            view.created,
            view.meta,
            view.order,
            view.type,
            view.fragmenter._saved,
            parent_id,
        )

    @classmethod
    def reconstitute(
        cls, data: Tuple, nodes: List[Tuple], edges: List[Tuple], frame_shift=0
    ) -> View:
        ...

    @classmethod
    def add_views(cls, views: List[View]) -> None:
        """Inserts a view, its parent, and supersystem"""
        parents = [v.parent for v in views if v.parent is not None]

        to_add = dedup_and_saveable(parents + views)
        if not to_add:
            return None
        # Parents to update
        update_parents = [v for v in to_add if v.parent and not v.parent._saved]

        # Save the stage
        DBStage.add_stages([v.fragmenter for v in to_add])

        # Insert the view and update _saved
        insert_many(
            cls,
            cls.field_order(),
            [cls.input_tuple(v) for v in to_add],
        )

        view_uuid_lookup = {v.id: v for v in to_add}
        view_id_lookup = {}
        query = cls.select(cls.id, cls.uuid).where(cls.uuid << [v.id for v in to_add])

        for db_id, _uuid in query.tuples():
            view = view_uuid_lookup[_uuid]
            view._saved = db_id
            view[ROOT].update(
                coef=0
            )  # Root will be included in our tree. Give if coef of 0
            view_id_lookup[db_id] = view_uuid_lookup[_uuid]
            view_id_lookup[db_id]._saved = db_id

        with cls._meta.database.atomic():
            for v in update_parents:
                if not v.parent:
                    continue
                cls.update(parent_id=v.parent._saved).where(
                    cls.id == v._saved
                ).execute()

        # Add nodes
        nodes = []
        for view in to_add:
            for n, d in view.tree.tree.nodes(data=True):  # Iterate and include root
                nodes.append(DBViewNode.input_tuple(view, n, d))
        insert_many(DBViewNode, DBViewNode.field_order(), nodes, batch_size=500)

        # Retrieve the node ID's for saving edges
        query = (
            DBViewNode.select()
            .select(DBViewNode.id, DBViewNode.key, DBViewNode.view_id)
            .where(DBViewNode.view_id << [v._saved for v in to_add])
        )

        for db_id, k, view_id in query.tuples():
            view_id_lookup[view_id][k]["db_id"] = db_id

        # Add edges!
        edges = []
        for view in to_add:
            for u, v in view.tree.tree.edges:
                edges.append(DBViewEdge.input_tuple(view, view[u], view[v]))

        insert_many(DBViewEdge, DBViewEdge.field_order(), edges, batch_size=750)

        # Link the systems
        # Save systems
        DBSystem.add_systems([v.supersystem for v in to_add if v.supersystem])
        systems_to_views = []
        for view in to_add:
            if view.supersystem:
                systems_to_views.append((view, view.supersystem, True))
        DBSystemToView.link_views_to_systems(systems_to_views)
        return views

    @classmethod
    def get_views(cls, ids: List[int], WORLD: Dict, REGISTRY: Dict) -> Dict[int, View]:
        # This will require performing two queries instead of one. I'm ok with this.
        if not ids:
            return {}
        view_ids = set(ids)

        # Get parents and stages first
        stage_queries = cls.select(cls.fragmenter_id, cls.parent_id).where(
            cls.id << view_ids
        )
        stage_ids = set()
        parent_ids = set()
        for s_id, p_id in stage_queries.tuples():
            if s_id is not None:
                stage_ids.add(s_id)
            if p_id is not None:
                parent_ids.add(p_id)
        parent_ids.difference_update(view_ids)  # The parent could already be requested

        stages = DBStage.get_stages(list(stage_ids), WORLD=WORLD, REGISTRY=REGISTRY)
        # TODO: This could be done recursivly
        if parent_ids:
            views = cls.get_views(list(parent_ids), WORLD=WORLD, REGISTRY=REGISTRY)
        else:
            views = {}

        # Prevent double-querying
        view_ids.difference_update(set(views.keys()))

        # Get the nodes and edges!
        nodes = DBViewNode.get_nodes(view_ids)
        edges = DBViewEdge.get_edges(view_ids)

        # Perform the actual query
        query = cls.select(
            cls.id,
            cls.uuid,
            cls.name,
            cls.created,
            cls.meta,
            cls.order,
            cls.type,
            cls.fragmenter_id,
            cls.parent_id,
        ).where(cls.id << set(view_ids))

        parent_child = []
        for db_id, id, name, created, meta, order, type, s_id, p_id in query.tuples():
            # Mark parent-child relation for annotating
            if p_id is not None:
                parent_child.append((db_id, p_id))

            # Build the tree and update the graph
            primatives = {n[2] for n in nodes[db_id] if n[5]}
            primaries = {n[2] for n in nodes[db_id] if n[4]}
            tree = PIETree(
                PIETree.new_tree(), primatives, primaries, frozenset.union(*primatives)
            )

            key_lookup = {}
            for n_id, v_id, k, c, prima, prime in nodes[db_id]:
                key_lookup[n_id] = k
                tree.new_node(k, c)  # Adds order information in PIE Tree
            tree.tree.add_edges_from(
                [(key_lookup[u], key_lookup[v]) for u, v in edges[db_id]]
            )

            views[db_id] = View(
                tree=tree,
                id=id,
                _saved=db_id,
                name=name,
                type=ViewType(type),
                order=order,
                created=created,
                fragmenter=stages[s_id],
                # parent=views[p_id] if p_id else None,
                meta=meta,
            )

        # Create parent-child relationships
        for p, c in parent_child:
            views[p].parent = views[c]

        query = (
            DBSystemToView
            .select(
                DBSystemToView.view_id,
                DBSystemToView.system_id
            )
            .where(
                DBSystemToView.originator == True, # noqa: E712
                DBSystemToView.view_id << view_ids
            )
        )
        system_ids = {vid: sid for vid, sid in query.tuples()}
        systems = DBSystem.get_systems(system_ids.values())
        
        for vid, sid in system_ids.items():
            views[vid].bind_system(systems[sid])

        return views

    @classmethod
    def get_view_by_originator(
        cls, fragmenter: Stage, system: System, order: int, WORLD: Dict, REGISTRY: Dict
    ) -> View | None:
        DBSystem.get_system_DBID([system])
        if system._saved == 0:
            return None

        # Query for a matching view
        V = DBView
        StV = DBSystemToView
        S = DBSystem
        vid = (
            V.select()
            .join(StV)
            .join(S)
            .select(V.id)
            .where(
                V.order == order,
                V.fragmenter_id == fragmenter._saved,
                S.id == system._saved,
                StV.originator == True,  # noqa: E712
            )
            .tuples()
            .first()
        )
        if vid:
            vid = vid[0]
            view = cls.get_views([vid], WORLD, REGISTRY)[vid]
            view.bind_system(system)
        else:
            view = None
        return view

    # def select_view_data(view_ids: List[id]) -> None:
    #     view_ids = set(view_ids)  # Dedup

    #     # Get the view itself
    #     # TODO: Make this recursive for parents
    #     V = models.View
    #     data = V.select(V.id, *V.field_order()).where(V.id << view_ids).tuples()
    #     update_world(ctx, "view_data", {d[0]: d[1:] for d in data})

    #     # Get node data
    #     VN = models.ViewNode
    #     data = VN.select(*VN.field_order()).where(VN.view_id << view_ids).tuples()
    #     node_data = {}
    #     for v, k, c, prima, prime in data:
    #         try:
    #             node_data[v].append((k, c, prima, prime))
    #         except KeyError:
    #             node_data[v] = [(k, c, prima, prime)]
    #     update_world(ctx, "view_node_data", node_data)

    #     # Get Node edges
    #     VE = models.ViewEdge
    #     P = VN.alias()  # Parent
    #     C = VN.alias()  # Child
    #     data = (
    #         VE.select()
    #         .join(P, on=(P.id == VE.parent_id))
    #         .switch()
    #         .join(C, on=(C.id == VE.child_id))
    #         .switch()
    #         .where(VE.view_id << view_ids)
    #         .select(VE.view_id, P.key, C.key)
    #         .tuples()
    #     )
    #     edge_data = {}
    #     for v, p, c in data:
    #         try:
    #             edge_data[v].append((p, c))
    #         except KeyError:
    #             edge_data[v] = [(p, c)]
    #     update_world(ctx, "view_edge_data", edge_data)


class DBViewNode(Model):
    class Meta:
        table_name = "view_node"

    view = ForeignKeyField(DBView, backref="coefs")
    key = KeyField()
    coef = IntegerField()
    is_primative = BooleanField(default=False)
    is_primary = BooleanField(default=False)

    @classmethod
    def field_order(cls):
        return (
            cls.view_id,
            cls.key,
            cls.coef,
            cls.is_primative,
            cls.is_primary,
        )

    @classmethod
    def input_tuple(cls, view: View, n: Key, d: Dict) -> Tuple:
        return (
            view._saved,
            n,
            d["coef"],
            n in view.tree.primatives,
            n in view.tree.primaries,
        )

    @classmethod
    def get_nodes(cls, view_ids: List[int]) -> Dict[int, List[Tuple]]:
        query = cls.select(
            cls.id, cls.view_id, cls.key, cls.coef, cls.is_primative, cls.is_primary
        ).where(cls.view_id << view_ids)
        nodes = {}
        for d in query.tuples():
            try:
                nodes[d[1]].append(d)
            except KeyError:
                nodes[d[1]] = [d]
        return nodes


class DBViewEdge(Model):
    class Meta:
        table_name = "view_edge"
        primary_key = CompositeKey("view", "parent", "child")

    view = ForeignKeyField(DBView, null=False, index=True)
    parent = ForeignKeyField(DBViewNode, null=False)
    child = ForeignKeyField(DBViewNode, null=False)

    @classmethod
    def field_order(cls):
        return (
            cls.view_id,
            cls.parent_id,
            cls.child_id,
        )

    @classmethod
    def input_tuple(cls, view: View, n1: Dict, n2: Dict) -> Tuple:
        return (
            view._saved,
            n1["db_id"],
            n2["db_id"],
        )

    @classmethod
    def get_edges(cls, view_ids: List[int]) -> Dict[int, List[Tuple]]:
        query = cls.select(*cls.field_order()).where(cls.view_id << view_ids)
        edges = {}
        for v_id, p_id, c_id in query.tuples():
            try:
                edges[v_id].append((p_id, c_id))
            except KeyError:
                edges[v_id] = [(p_id, c_id)]
        return edges


class DBSystemToView(Model):
    class Meta:
        table_name = "system_to_view"
        constraints = [
            SQL("UNIQUE (system_id, view_id)"),
        ]

    system = ForeignKeyField(DBSystem, null=False)
    view = ForeignKeyField(DBView, null=False)
    originator = BooleanField(default=False)

    @classmethod
    def field_order(cls):
        return (
            cls.system,
            cls.view,
            cls.originator,
        )

    @classmethod
    def input_tuple(cls, view: View, system: System, is_originator: bool) -> Tuple:
        return (system._saved, view._saved, is_originator)

    @classmethod
    def link_views_to_systems(cls, view_data: List[Tuple[View, System, bool]]) -> None:
        insert_many(
            cls,
            cls.field_order(),
            [cls.input_tuple(v, s, o) for v, s, o in view_data],
            batch_size=750,
            ignore_conflicts=True,
        )

    @classmethod
    def get_link_ids(
        cls, view_data: List[Tuple[View, System]]
    ) -> Dict[Tuple[int, int], Tuple[int, bool]]:
        lookup = {}
        for chunk in chunked(view_data, 100):
            query = cls.select(
                cls.view_id, cls.system_id, cls.id, cls.originator
            ).orwhere(
                *(
                    (cls.view_id == v._saved) & (cls.system_id == s._saved)
                    for v, s in chunk 
                )
            )
            lookup.update((((v, s), (i, o)) for v, s, i, o in query.tuples()))
        return lookup


class DBViewRecord(Model):
    class Meta:
        table_name = "view_record"
        primary_key = CompositeKey("bound_view", "record")

    bound_view = ForeignKeyField(DBSystemToView)
    record = ForeignKeyField(DBRecord)

    @classmethod
    def get_record_DBID(cls, records: List[ViewRecord]) -> None:
        """Allows SystemRecords to have a one-to-one relationship
        between DBSystems and Records.

        This assumes each record in `records` will overwrite the existing
        value.
        """
        # Pull existing DBIDs for records
        unsaved_records = dedup_and_saveable(records)
        DBSystem.get_system_DBID([r.system for r in unsaved_records])

        # If the view is not saved, don't update
        ids = [
            (r.stage._saved, r.view._saved, r.system._saved)
            for r in unsaved_records
            if r.stage._saved and r.view._saved and r.system._saved
        ]

        lookup = {}
        for chunk in chunked(ids, 100):
            query = (
                DBRecord.select()
                .join(cls)
                .join(DBSystemToView)
                .select(
                    DBRecord.stage_id,
                    DBSystemToView.view_id,
                    DBSystemToView.system_id,
                    cls.record_id,
                    DBRecord.uuid,
                )
                .orwhere(
                    *(
                        (
                            (DBRecord.stage_id == d)
                            & (DBSystemToView.view_id == v)
                            & (DBSystemToView.system_id == s)
                        )
                        for d, v, s in chunk
                    )
                )
            )
            lookup.update((((d, v, s), (r, u)) for d, v, s, r, u in query.tuples()))

        for record in records:
            # DEBUGGING: Sanity check
            r_id, r_uuid = lookup.get(
                (record.stage._saved, record.view._saved, record.system._saved), (0, 0)
            )

            if r_id:
                record._saved = r_id
                record.id = r_uuid

    @classmethod
    def add_or_update_view_record(
        cls, records: List[ViewRecord], add_only=False
    ) -> List[ViewRecord]:
        """This can add duplicate records if we are not carful. Make sure to
        check for existing records before adding a new one
        """
        # All views must be saved!
        if not all((r.view._saved for r in records)):
            raise Exception("Cannot add records for unsaved views")

        # Check if records already exist
        cls.get_record_DBID(records)

        # Create links for un-saved records
        to_link = [r for r in records if not r._saved]

        # TODO: Check that the system -- record.backend are unique in the database
        DBSystem.add_systems((r.system for r in records))
        DBRecord.add_or_update_records(records, add_only=add_only)

        # Add system-veiw relation
        DBSystemToView.link_views_to_systems(
            [
                (r.view, r.system, False)  # Will ignore origin-view links
                for r in to_link
            ]
        )
        stv_ids = DBSystemToView.get_link_ids([(r.view, r.system) for r in to_link])

        insert_many(
            cls,
            (
                cls.bound_view_id,
                cls.record_id,
            ),
            ((stv_ids[(r.view._saved, r.system._saved)][0], r._saved) for r in to_link),
            ignore_conflicts=True,
        )
        return records

    @classmethod
    def get_view_record(
        cls, stage: Stage, view: View, systems: List[System]
    ) -> Dict[System, ViewRecord]:
        # Stage must be saved for this to work
        if not stage._saved or not view._saved:
            return {}

        # Update any systems which are in the DB but don't have ids yet
        DBSystem.get_system_DBID(systems)
        system_lookup = {s._saved: s for s in systems if s._saved}

        # Get link data
        query = (
            DBRecord.select()
            .join(cls)
            .join(DBSystemToView)
            .select(DBSystemToView.system_id, *DBRecord.select_fields())
            .where(
                (DBSystemToView.system_id << list(system_lookup.keys()))
                & (DBRecord.stage_id == stage._saved)
                & (DBSystemToView.view_id == view._saved)
            )
        )

        record = {
            system_lookup[rec_data[0]]: DBRecord.tuple_to_record(
                stage,
                *rec_data[2:],
                system=system_lookup[rec_data[0]],
                view=view,
                RecordBase=ViewRecord,
            )
            for rec_data in query.tuples()
        }
        return record


###########################################################
#                   RELATION MODELS                       #
###########################################################


# class Bond(BaseModel):
#     a1: Atom = ForeignKeyField(Atom)
#     a2: Atom = ForeignKeyField(Atom)
#     system: System = ForeignKeyField(System)
#     length: float = FloatField()
#     order: int = IntegerField(default=0)

#     @classmethod
#     def save_graph(cls, sys: System, G: nx.Graph, save_zero=True) -> None:
#         sys_id = sys.id
#         bonds = [
#             Bond(
#                 a1_id=G.nodes[a1]["db_id"],
#                 a2_id=G.nodes[a2]["db_id"],
#                 system_id=sys_id,
#                 length=d["length"],
#                 order=d["order"],
#             )
#             for a1, a2, d in G.edges(data=True)
#         ]
#         cls.bulk_create(bonds)

#     @classmethod
#     def get_bond_graph(cls, sys_id: int) -> nx.Graph:
#         bond_query = cls.select(
#             Bond.a1_id,
#             Bond.a2_id,
#             Bond.length,
#             Bond.order,
#         ).where(Bond.system_id == sys_id)
#         G = nx.Graph()

#         for a1, a2, l, o in bond_query.tuples():
#             G.add_edge(a1, a2, length=l, order=o)
#         return G

#     @classmethod
#     def mk_bond_graph(cls, sys: System, save=True) -> nx.Graph:
#         tolerance = 1.2
#         cutoff = 3.0
#         k = 8

#         G = nx.Graph()
#         kd = sys.KDTree
#         bonds: List["Bond"] = []

#         # ADD ATOMS AS NODES
#         for idx, a in enumerate(sys.atoms):
#             a: Atom
#             G.add_node(
#                 idx,
#                 db_id=a.id,
#                 atom=a,
#                 charge=a.charge,
#                 valence=a.valence_e,
#                 bonds_needed=min(a.valence_e, a.max_valence - a.valence_e),
#                 column=ptable.to_group(a.t),
#             )

#         # ADD BONDS TO GRAPH
#         for a1_idx, a1 in enumerate(sys.atoms):
#             a2_d_list, a2_idx_list = kd.query(a1.r, k=k, distance_upper_bound=cutoff)
#             for a2_d, a2_idx in zip(a2_d_list, a2_idx_list):
#                 if a1_idx <= a2_idx:
#                     continue
#                 a2 = sys.atoms[a2_idx]
#                 expected = a1.covalent_radius + a2.covalent_radius
#                 if a2_d < expected * tolerance:
#                     # A very broad definition of a bond :)
#                     G.add_edge(
#                         a1_idx,
#                         a2_idx,
#                         order=0,
#                         length=a2_d,
#                         score=cls.get_score(
#                             a2_d,
#                             0,
#                             abs(ptable.to_period(a1.t) - ptable.to_period(a2.t)),
#                         ),
#                     )

#         # INCREASE BOND ORDER UNTIL DONE
#         bm = 1
#         while bm > 0:
#             bonds = []
#             for a1, a2, d in G.edges(data=True):
#                 if G.nodes[a1]["bonds_needed"] == 0 or G.nodes[a2]["bonds_needed"] == 0:
#                     continue
#                 bonds.append((a1, a2, d["score"]))
#             if not bonds:
#                 break

#             bonds.sort(key=lambda x: x[2])
#             bm = cls.start(G, bonds[0][0])

#         if save:
#             cls.save_graph(sys, G)
#         return G

#     @classmethod
#     def get_score(cls, length: float, order: int, period_delta: int) -> float:
#         return length + 0.15 * length * (order + period_delta)

#     @classmethod
#     def score_from_edge(cls, G: nx.Graph, a1_idx, a2_idx):
#         e = G[a1_idx][a2_idx]
#         a1 = G.nodes[a1_idx]["atom"]
#         a2 = G.nodes[a2_idx]["atom"]
#         return cls.get_score(
#             e["length"],
#             e["order"],
#             abs(ptable.to_period(a1.t) - ptable.to_period(a2.t)),
#         )

#     @classmethod
#     def start(cls, G: nx.Graph, a_idx: int) -> int:
#         bonds_made = 0
#         a = G.nodes[a_idx]
#         while a["bonds_needed"] > 0:
#             bonds = cls.get_bonds(G, a_idx)  # Get newly scored bonds
#             if not bonds:  # Prevent infinite loops
#                 break
#             a1_idx, a2_idx, _score = bonds[0]

#             # Make the bond
#             bonds_made += 1
#             cls.make_bond(G, a1_idx, a2_idx)

#             # Make bonds on linked atom
#             a_next = a_idx if a_idx != a1_idx else a2_idx
#             bonds_made += cls.start(G, a_next)
#         return bonds_made

#     @classmethod
#     def get_bonds(cls, G: nx.Graph, a1_idx: int):
#         bonds = []
#         for a2_idx in G[a1_idx]:
#             a2 = G.nodes[a2_idx]
#             if a2["bonds_needed"] > 0:
#                 bonds.append((a1_idx, a2_idx, G[a1_idx][a2_idx]["score"]))
#         bonds.sort(key=lambda x: x[2])
#         return bonds

#     @classmethod
#     def make_bond(cls, G: nx.Graph, a1_idx: int, a2_idx: int):
#         G.nodes[a1_idx]["bonds_needed"] -= 1
#         G.nodes[a2_idx]["bonds_needed"] -= 1
#         G[a1_idx][a2_idx]["order"] += 1
#         G[a1_idx][a2_idx]["score"] = cls.score_from_edge(G, a1_idx, a2_idx)
