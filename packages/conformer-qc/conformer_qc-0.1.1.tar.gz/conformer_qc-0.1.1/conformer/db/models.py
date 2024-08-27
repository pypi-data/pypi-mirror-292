#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from datetime import datetime
from enum import IntEnum
from functools import lru_cache
from itertools import chain
from typing import Dict, Generator, List, Tuple, TypeVar, Union

import numpy as np
from peewee import (
    BitField,
    CharField,
    CompositeKey,
    DateTimeField,
    Field,
    FloatField,
    ForeignKeyField,
    IntegerField,
    Model,
    chunked,
)
from playhouse.sqlite_ext import JSONField

from conformer.common import PHYSICAL_ATOM, Mask, int_to_role, role_to_int
from conformer.common import AtomMask as AM
from conformer.common import CellIndex as CI
from conformer.records import SystemRecord
from conformer.systems import (
    ORIGIN_INT,
    Atom,
    BoundAtom,
    NamedSystem,
    NPf64,
    System,
    UniqueSystemDict,
    UniqueSystemSet,
    hash_UnitCell_v2,
)
from conformer_core.db.models import (
    DBRecord,
    DBStage,
    FingerprintField,
    dedup_and_saveable,
    filter_existing,
    insert_many,
)
from conformer_core.stages import Stage

T = TypeVar("T")

CHUNK_SIZE = 100

###################################################################################
#   CUSTOM FIELDS
###################################################################################


class RoleField(BitField):
    def db_value(self, value):
        v = role_to_int(value)
        return super().db_value(v)

    def python_value(self, value):
        _v = super().python_value(value)
        return int_to_role(_v)


class UnsignedIntegerField(IntegerField):
    """Workaround This allows us to take advantage of all 64 bits"""

    def db_value(self, value: int):
        # This is a hack :(
        bytes = value.to_bytes(8, "little", signed=False)
        return int.from_bytes(bytes, "little", signed=True)

    def python_value(self, value):
        bytes = value.to_bytes(8, "little", signed=True)
        return int.from_bytes(bytes, "little", signed=False)


class MaskField(IntegerField):
    """Workaround This allows us to take advantage of all 64 bits"""

    def db_value(self, mask: Mask):
        return mask.str_digest()

    def python_value(self, mask_str: str):
        return Mask.from_str(mask_str)


class RoleBits(IntEnum):
    IS_PHYSICAL = 2**0
    HAS_BASIS_FNS = 2**1
    IS_POINT_CHARGE = 2**2
    IS_PROXY = 2**3


class RelationType(IntEnum):
    SUPERSYSTEM = 0
    PARENT_CHILD = 1
    DEPENDS_ON = 2  # Calculations that must happen first


@lru_cache(maxsize=100)
def _get_cell(data):
    # Helper function to convert cell index to ORIGIN_INT
    if data == (0, 0, 0):
        return ORIGIN_INT
    else:
        return np.array(data, dtype="int32")


###################################################################################
#   MODELS
###################################################################################


##### ATOM MODEL ##################################################################
class DBAtom(Model):
    class Meta:
        table_name = "atom"

    fingerprint = FingerprintField(index=True, unique=True)
    t = CharField(8)
    x = FloatField()
    y = FloatField()
    z = FloatField()
    charge = IntegerField(default=0)
    meta = JSONField(null=False, default=lambda: {})

    @classmethod
    def field_list(cls) -> Tuple[Field, ...]:
        return (cls.fingerprint, cls.t, cls.x, cls.y, cls.z, cls.charge, cls.meta)

    @staticmethod
    def to_tuple(atom: Atom) -> Tuple:
        return (
            atom.fingerprint,
            atom.t,
            atom.r[0],
            atom.r[1],
            atom.r[2],
            atom.charge,
            atom.meta,
        )

    @classmethod
    def add_atoms(cls, atoms: List[Atom]) -> List[Atom]:
        """Adds all atoms in a system (and it's copies in other roles)

        .. NOTE:
            For adding Adding 50000 Atoms

            - Using dict of object identifiers takes 3.9 s
            - Using dict of strings takes 4.4 s
            - Using tuples and specifying fields 3.2 s
            - Using DBAtom objects gave similar to above results

            We are taking a performance hit by serilizing a json object for each atom meta
        """
        to_add = filter_existing(dedup_and_saveable(atoms), cls)

        if not to_add:
            return atoms

        # Serialize the atom data
        atom_data = [cls.to_tuple(a) for a in to_add]
        insert_many(
            cls, cls.field_list(), atom_data, batch_size=1500, ignore_conflicts=True
        )

        # Now Query the database and get the udpate PKs
        just_added = filter_existing(to_add, cls, check_collisions=True)
        assert len(just_added) == 0  # They should have ALL been added :)

        # Return the finished atom list
        return atoms

    @classmethod
    def get_atoms(cls, atom_ids: List[int]) -> Dict[int, Atom]:
        to_get = set(atom_ids)
        atoms = {}

        # Get related atoms and varients
        base_query = cls.select(
            cls.id,
            cls.t,
            cls.x,
            cls.y,
            cls.z,
            cls.charge,
            cls.meta,
        )
        for batch in chunked(to_get, 500):
            atom_data = base_query.where(cls.id << batch)
            for a_id, t, x, y, z, c, _meta in atom_data.tuples():
                atom = Atom(
                    t=t,
                    r=np.array((x, y, z)),
                    charge=c,
                    meta=_meta,
                    _saved=a_id,
                )
                atoms[a_id] = atom
        return atoms


##### UNITE CELLMODEL ##############################################################
class DBUnitCell(Model):
    class Meta:
        table_name = "unit_cell"

    fingerprint = FingerprintField(index=True, unique=True)
    a = FloatField(null=False)
    b = FloatField(null=False)
    c = FloatField(null=False)

    @staticmethod
    def _cell_fingerprint(r: NPf64) -> str:
        return hash_UnitCell_v2(r).hexdigest()

    @classmethod
    def add_cells(cls, cells: List[Union[NPf64, None]]) -> Dict[int, int]:
        # Remove None and duplicates
        to_add = []
        added_fingerprints = set()
        for c in cells:
            if c is None:
                continue
            # Calculate the hashes (TODO: can we pre-compute this?)
            h = cls._cell_fingerprint(c)
            if h in added_fingerprints:
                continue
            added_fingerprints.add(h)
            to_add.append((h, c[0], c[1], c[2]))

        if to_add:
            insert_many(
                cls,
                (cls.fingerprint, cls.a, cls.b, cls.c),
                to_add,
                ignore_conflicts=True,
            )

        query = cls.select(cls.fingerprint, cls.id).where(
            cls.fingerprint << added_fingerprints
        )
        ret = {h: id for h, id in query.tuples()}
        ret[None] = None
        return ret

    @classmethod
    def iter_cell_ids(cls, systems: List[System]) -> Generator[int, None, None]:
        """For each system return the database id of unit it's unit cell.

        If one does not exist, a new cell is created.
        """
        cells = [s.unit_cell for s in systems]
        fingerprints = [
            cls._cell_fingerprint(c) if c is not None else None for c in cells
        ]
        cell_table = cls.add_cells(cells)
        for h in fingerprints:
            yield cell_table[h]

    @classmethod
    def get_cells(cls, ids: List[int]) -> Dict[Union[None, int], NPf64]:
        cell_ids = set(ids)
        query = DBUnitCell.select(cls.id, cls.a, cls.b, cls.c).where(cls.id << cell_ids)
        return {d[0]: np.array(d[1:], dtype=np.float64) for d in query.tuples()}


##### SYSTEM MODEL #################################################################
class DBSystem(Model):
    class Meta:
        table_name = "system"

    fingerprint = FingerprintField(index=True, unique=True)
    digest = MaskField(index=True)  # Not unique. unit_cell + digest is unique
    unit_cell = ForeignKeyField(DBUnitCell, null=True)

    @classmethod
    def field_list(cls) -> Tuple[Field, ...]:
        return (cls.fingerprint, cls.digest, cls.unit_cell)

    @classmethod
    def to_tuple(cls, sys: System, cell_id: int) -> Tuple:
        return (sys.fingerprint, cls.create_digest(sys), cell_id)

    @staticmethod
    def create_digest(sys: System) -> Mask:
        data = {}
        for a in sys:
            c = tuple(a.cell)
            am = AM(a._saved, a.role)
            try:
                data[c].append(am)
            except KeyError:
                data[c] = [am]

        return Mask({CI(c): frozenset(d) for c, d in data.items()})

    @classmethod
    def get_system_DBID(cls, systems: List[System]) -> None:
        """Attaches the database ID to the system if it exists"""
        filter_existing([s for s in systems if not s._saved], cls)

    @classmethod
    def add_systems(cls, systems: List[System]) -> List[System]:
        """Insert statement for system row

        Systems are saved with atoms in canonical order. SystemLabels will
        allow alternative ordering schemes

        .. NOTE:
            This presupposes that all atoms have already been saved
        """
        _systems = dedup_and_saveable(systems)
        new_sys = filter_existing(_systems, cls)

        if new_sys:
            # TODO: Look for related systems?

            # Step 1: Save the atoms!
            atoms = [a._atom for a in chain(*new_sys)]
            DBAtom.add_atoms(atoms)

            # Step 2: Save the system (fingerprint, digest, unit cell)
            to_add = UniqueSystemSet(new_sys)
            system_data = [
                cls.to_tuple(s, i)
                for i, s in zip(DBUnitCell.iter_cell_ids(to_add), to_add)
            ]

            insert_many(
                cls,
                cls.field_list(),
                system_data,
                ignore_conflicts=True,
            )

            # Update _saved on all models and conferm everything was saved
            just_added = filter_existing(new_sys, cls, check_collisions=True)
            assert len(just_added) == 0  # They should have ALL been added :)

            # Add the BoundSystem/AtomToSystem data
            canonical_atoms = [sys._canonical_atoms for sys in to_add]
            insert_many(
                DBAtomToSystem,
                DBAtomToSystem.field_list(),
                [
                    DBAtomToSystem.to_tuple(a, i)
                    for i, a in enumerate(chain(*canonical_atoms))
                ],
            )

        # Handle named systems using ALL systems
        named_systems = [s for s in _systems if isinstance(s, NamedSystem)]
        if named_systems:
            DBSystemLabel.add_system_labels(named_systems)
        return systems

    @classmethod
    def get_systems(cls, ids: List[int]) -> Dict[int, System]:
        # TODO: Look for related systems?
        system_ids = set(ids)

        binding_data = DBAtomToSystem.get_binding_data(system_ids)

        # GET ATOMS
        atom_ids = set((bd[1]) for bd in chain(*binding_data.values()))
        atoms = DBAtom.get_atoms(list(atom_ids))

        # GET AND ASSEMBLE THE SYSTEM
        system_query = cls.select(
            cls.id, cls.fingerprint, cls.digest, cls.unit_cell
        ).where(cls.id << system_ids)

        # Get the unit cell data
        raw_data = [d for d in system_query.tuples()]
        cells = DBUnitCell.get_cells((d[3] for d in raw_data))

        # TODO: Handle unit cells
        system_data = {}

        for sid, s_fingerprint, digest, cell_id in raw_data:
            sys = System(
                (
                    BoundAtom(atoms[bd[1]], role=bd[2], cell=_get_cell(bd[3:6]))
                    for bd in binding_data[sid]
                ),
                unit_cell=cells.get(cell_id, None),
                is_canonized=True,
                _saved=sid,
            )

            # Debugging
            # Should come out of the database as canonized!
            # TODO: Remove for performance
            # for a1, a2 in zip(sys, sys.canonize()):
            #     assert a1 == a2
            # assert s_fingerprint == sys.fingerprint().hexdigest()
            # assert digest == cls.create_digest(sys)

            system_data[sid] = sys
        return system_data

    @classmethod
    def get_systems_by_fingerprint(cls, fingerprints: List[str]) -> Dict[str, System]:
        if not fingerprints:
            return {}

        query = cls.select(cls.id, cls.fingerprint).where(
            cls.fingerprint << fingerprints
        )
        fp_lookup = {id: fp for id, fp in query.tuples()}
        systems = cls.get_systems(fp_lookup.keys())

        return {fp_lookup[i]: s for i, s in systems.items()}


##### ATOM TO SYSTEM RELATION ######################################################
class DBAtomToSystem(Model):
    class Meta:
        table_name = "atom_to_system"
        # primary_key = CompositeKey("atom", "system", "role")

    atom = ForeignKeyField(DBAtom, backref="_systems")
    system = ForeignKeyField(DBSystem, backref="_atoms")
    _order = IntegerField()

    # ATOM ROLE
    role = RoleField(default=PHYSICAL_ATOM)

    # Defined to simplify queries
    is_physical = role.flag(RoleBits.IS_PHYSICAL)
    has_basis_fns = role.flag(RoleBits.HAS_BASIS_FNS)
    is_point_charge = role.flag(RoleBits.IS_POINT_CHARGE)
    is_proxy = role.flag(RoleBits.IS_PROXY)

    # CELL INDEX
    # NOTE: Store as null to save space for (0,0,0)
    a = IntegerField(null=True)
    b = IntegerField(null=True)
    c = IntegerField(null=True)

    @classmethod
    def field_list(cls) -> Tuple[Field, ...]:
        return (
            cls.atom_id,
            cls.system_id,
            cls._order,
            cls.role,
            cls.a,
            cls.b,
            cls.c,
        )

    @staticmethod
    def to_tuple(atom: BoundAtom, order: int) -> Tuple:
        return (
            atom._saved,
            atom.system._saved,
            order,
            atom.role,
            atom.cell[0],
            atom.cell[1],
            atom.cell[2],
        )

    @classmethod
    def get_binding_data(cls, system_ids: List[int]) -> Dict[int, List[Tuple]]:
        # GET THE BOUND ATOMS
        binding_data_query = (
            cls.select(
                cls.system_id,
                cls.atom_id,
                cls.role,
                cls.a,
                cls.b,
                cls.c,
            )
            .where(cls.system_id << system_ids)
            .order_by(cls._order)
        )
        binding_data = {}
        for bd in binding_data_query.tuples():
            try:
                binding_data[bd[0]].append(bd)
            except KeyError:
                binding_data[bd[0]] = [bd]
        return binding_data


##### SYSTEM TO SYSTEM RELATION ####################################################
class DBSystemToSystem(Model):
    class Meta:
        table_name = "system_to_system"
        primary_key = CompositeKey("left", "right", "rel_type")

    left = ForeignKeyField(DBSystem, backref="related_on_left")
    right = ForeignKeyField(DBSystem, backref="related_on_right")
    rel_type = IntegerField()


##### SYSTEM LABEL MODEL ##########################################################
class DBSystemLabel(Model):
    class Meta:
        table_name = "system_label"

    system = ForeignKeyField(DBSystem, backref="labels")
    name = CharField(max_length=255, null=False, index=True, unique=True)
    created = DateTimeField(null=False, default=datetime.now)
    meta = JSONField(null=False)

    @classmethod
    def add_system_labels(cls, systems: List[NamedSystem]) -> List[NamedSystem]:
        """Adds the label for a system. This information will not be retrieved
        when the system is loaded with `get_systems`. Use `get_systems_by_name` instead
        """
        # Check that this system hasn't been added before
        existing = set(
            (
                existing_s
                for existing_s in cls.select(cls.system.id, cls.name)
                .where(cls.name << [s.name for s in systems])
                .join(DBSystem)
                .tuples()
            )
        )
        systems = [s for s in systems if (s._saved, s.name) not in existing]

        # Add offset to the metadata such that we get the *exact* system back on retrieval
        DB_systems = DBSystem.get_systems([s._saved for s in systems])
        for s1 in systems:
            s2 = DB_systems[s1._saved]
            s1.meta["offset"] = list(s1.COM - s2.COM)

        insert_many(
            cls,
            (cls.system_id, cls.name, cls.created, cls.meta),
            [(s._saved, s.name, s.created, s.meta) for s in systems],
            batch_size=500,
        )

        return systems

    @classmethod
    def all_system_names(cls) -> List[str]:
        query = cls.select(cls.name)
        return [n[0] for n in query.tuples()]

    @classmethod
    def get_systems_by_name(cls, names: List[str]) -> Dict[str, NamedSystem]:
        label_data = {}
        for batch in chunked(names, 500):
            sl_data = cls.select(
                cls.system_id,
                cls.name,
                cls.created,
                cls.meta,
            ).where(cls.name << batch)

            for s in sl_data.tuples():
                label_data[s[1]] = s

        # We will be double allocating this which I don't love
        # Optimize later I guess
        systems = DBSystem.get_systems([s[0] for s in label_data.values()])
        labeled_systems = {}
        for n, (id, name, create, meta) in label_data.items():
            _sys = systems[id]
            labeled_systems[n] = NamedSystem(
                _sys._atoms,
                name=name,
                unit_cell=_sys.unit_cell,
                supersystem=_sys.supersystem,
                created=create,
                meta=meta,
                _saved=id,
            )

        return labeled_systems


##### SYSTEM RECORD MODEL #########################################################
class DBSystemRecord(Model):
    class Meta:
        table_name = "system_record"
        primary_key = CompositeKey("system", "record")

    system = ForeignKeyField(DBSystem)
    record = ForeignKeyField(DBRecord)

    @classmethod
    def get_record_DBID(cls, records: List[SystemRecord]) -> None:
        """Allows SystemRecords to have a one-to-one relationship
        between DBSystems and Records.

        This assumes each record in `records` will overwrite the existing
        value.
        """

        # Perform unions?
        DBSystem.get_system_DBID([r.system for r in records if not r._saved])
        ids = set(
            (r.stage._saved, r.system._saved)
            for r in records
            if r.system._saved and r.stage._saved
        )

        # TODO: Batch
        if not ids:
            return

        lookup = {}
        # TODO: Benchmark both approaches
        for chunk in chunked(ids, 50):
            query = (
                cls.select()
                .join(DBRecord)
                .select(DBRecord.stage_id, cls.system_id, cls.record_id, DBRecord.uuid)
                .orwhere(
                    *(
                        ((DBRecord.stage_id == d) & (cls.system_id == s))
                        for d, s in chunk
                    )
                )
            )

            lookup.update((((d, s), (r, u)) for d, s, r, u in query.tuples()))

        # # Chain by driver_id
        # query = None
        # for driver_id in {i[0] for i in ids}:
        #     system_ids = {i[1] for i in ids}

        #     # TODO: Batch
        #     sub_query = cls.select().join(DBRecord).select(
        #         cls.system_id,
        #         DBRecord.id,
        #         cls.record_id,
        #         DBRecord.uuid
        #     ).where(
        #         cls.system_id << system_ids, DBRecord.id == driver_id
        #     )

        #     # Append it to the next query
        #     if query is None:
        #         query = sub_query
        #     else:
        #         query = query.union(sub_query)

        # Guard againts unsaved queries
        # if query is None:
        #     return
        # lookup = {(s, d): (r, u) for s, d, r, u in query.tuples()}

        for record in records:
            # DEBUGGING: Sanity check
            r_id, r_uuid = lookup.get(
                (record.stage._saved, record.system._saved), (0, 0)
            )

            if r_id:
                record._saved = r_id
                record.id = r_uuid

    @classmethod
    def add_or_update_system_record(
        cls, records: List[SystemRecord], add_only=False
    ) -> List[SystemRecord]:
        """This can add duplicate records if we are not carful. Make sure to
        check for existing records before adding a new one
        """
        # Check if records already exist
        cls.get_record_DBID(records)

        # Prevent double-checking if system is saved and record is changed
        to_link = [r for r in records if not r._saved]

        # TODO: Check that the system -- record.backend are unique in the database
        DBSystem.add_systems((r.system for r in records))
        DBRecord.add_or_update_records(records, add_only=add_only)

        # Link the systems and records
        insert_many(
            cls,
            (
                cls.system_id,
                cls.record_id,
            ),
            ((r.system._saved, r._saved) for r in to_link),
            ignore_conflicts=True,
        )
        return records

    @classmethod
    def get_system_records(
        cls, stage: Stage, systems: List[System]
    ) -> Dict[System, SystemRecord]:
        # Stage must be saved for this to work
        if not stage._saved:
            return {}

        # Update any systems which are in the DB but don't have ids yet
        DBSystem.get_system_DBID(systems)
        system_lookup = {s._saved: s for s in systems if s._saved}

        # Get link data
        query = (
            DBRecord.select()
            .join(cls)
            .select(cls.system_id, *DBRecord.select_fields())
            .where(
                (cls.system_id << list(system_lookup.keys()))
                & (DBRecord.stage_id == stage._saved)
            )
        )

        # I don't like this signature. We already have stage...
        # Passing empty registry since we won't be rebuilding stage....
        records = UniqueSystemDict()
        for rec_data in query.tuples():
            sys = system_lookup[rec_data[0]]
            record = DBRecord.tuple_to_record(
                stage,
                *rec_data[2:],
                system=system_lookup[rec_data[0]],
                RecordBase=SystemRecord,
            )
            records[sys] = record
        return records

    @classmethod
    def get_record_by_uuid(
        cls, uuids: List[str], WORLD: Dict, REGISTRY: Dict
    ) -> SystemRecord:
        conditions = [DBRecord.uuid.startswith(u.replace("-", "")) for u in uuids]

        # TODO: Add batching
        query = (
            DBRecord.select()
            .join(cls)
            .select(cls.system_id, *DBRecord.select_fields())
            .orwhere(*conditions)
        )
        record_data = list(query.tuples())
        system_ids = set((r[0] for r in record_data))
        stage_ids = set((r[1] for r in record_data))

        systems = DBSystem.get_systems(system_ids)
        stages = DBStage.get_stages(stage_ids, WORLD, REGISTRY)

        records = {
            str(r[3]): DBRecord.tuple_to_record(
                stages[r[1]],
                *r[2:],
                system=systems[r[0]],
                RecordBase=SystemRecord,
            )
            for r in record_data
        }

        return records

    @classmethod
    def get_or_create_system_records(
        cls,
        stage: Stage,
        systems: List[System],
    ) -> Dict[System, SystemRecord]:
        """Creates saved records for a given calculation"""

        if not stage._saved:
            raise ValueError(
                "`get_or_create_system_records` must be called with a saved Stage"
            )

        # Save all systems first
        _systems = UniqueSystemSet(DBSystem.add_systems(systems))

        # Get what records we can
        existing_records = cls.get_system_records(stage, systems)

        # Create new records
        new_records = [
            SystemRecord(stage, system=s) for s in _systems if s not in existing_records
        ]
        cls.add_or_update_system_record(new_records)

        # Update existing records
        for r in new_records:
            existing_records[r.system] = r
        return existing_records
