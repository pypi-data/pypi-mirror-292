#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import hashlib
from datetime import datetime
from typing import Dict, FrozenSet, Iterable, List, Optional, Set, Tuple, TypeVar, Union
from uuid import UUID, uuid4

from peewee import (
    SQL,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
    UUIDField,
    chunked,
)
from playhouse.sqlite_ext import JSONField

import conformer_core.properties.core as props
import conformer_core.records as records
from conformer.systems import SystemKey
from conformer_core.calculation import CalculationRecord
from conformer_core.records import Record, RecordStatus
from conformer_core.stages import Stage, StoredStage, reconstitute

quickNode = FrozenSet[int]
T = TypeVar("T")


class ValidationError(Exception):
    pass


###################################################################################
#   CUSTOM FIELDS
###################################################################################
# TODO: Add this to settings!
ALLOWED_CHARS = set("-_./()")


def validate_slug(value):
    for c in value:
        c: str
        if c.isalnum():
            continue
        if c in ALLOWED_CHARS:
            continue
        raise ValidationError(
            f'Name {value} is not a valid slug. Should contain only letters, numbers, and the special character "{ALLOWED_CHARS}"'
        )


class SlugField(CharField):
    def db_value(self, value):
        validate_slug(value)
        return super().db_value(value)


class FingerprintField(CharField):
    def db_value(self, value: Union["hashlib._Hash", str]):
        if isinstance(value, str):
            return value
        return value.hexdigest()


class KeyField(CharField):
    """Field for storing System Keys and similar"""

    def db_value(self, value):
        if isinstance(value, Iterable):
            store_str = ",".join((str(v) for v in sorted(value)))
        else:
            store_str = str(value)
        return super().db_value(store_str)

    def python_value(self, value) -> quickNode:
        if value:
            ids_str = value.split(",")
            return SystemKey((int(id) for id in ids_str))
        else:
            return SystemKey([])


class PropertiesField(JSONField):
    def db_value(self, value: props.PropertySet):
        if value is None:
            if self.null:
                _value = None
            else:
                _value = {}
        elif not value.values and self.null:
            _value = None
        else:
            _value = value.to_dict()
        return super().db_value(_value)

    def python_value(self, value) -> props.PropertySet:
        _value = super().python_value(value)
        if _value is None:
            return None
        else:
            return props.PropertySet.from_dict(_value)


###################################################################################
#   HELPER FUNCTIONS
###################################################################################
def insert_many(
    model: Model,
    fields: Tuple,
    data: List,
    batch_size=500,
    ignore_conflicts=False,
    replace_conflicts=False,
) -> None:
    for batch in chunked(data, batch_size):
        # with model._meta.database.transaction():
        query = model.insert_many(batch, fields=fields)
        if ignore_conflicts:
            query = query.on_conflict_ignore()
        if replace_conflicts:
            query = query.on_conflict_replace()
        query.execute()


def dedup(obj_list: List[T]) -> List[T]:
    # Deduplicate the objects
    mem_addresses: Set[int] = set()
    to_add: List[T] = []  # The unique objects to add
    for o in obj_list:
        if id(o) not in mem_addresses:
            mem_addresses.add(id(o))
            to_add.append(o)
    return to_add


def dedup_and_saveable(obj_list: List[T]) -> List[T]:
    """Same a dedup but also filters out objects which have already been saved"""
    # Deduplicate the objects
    mem_addresses: Set[int] = set()
    to_add: List[T] = []  # The unique objects to add
    for o in obj_list:
        if not o._saved and id(o) not in mem_addresses:
            mem_addresses.add(id(o))
            to_add.append(o)

    return to_add


def filter_existing(
    items: List[T], model: Model, check_collisions=False, CHUNK_SIZE=500
) -> List[T]:
    if not items:
        return []
    prints = set(h.fingerprint for h in items)
    lookup = {}
    for b in chunked(prints, CHUNK_SIZE):
        query = model.select(model.fingerprint, model.id).where(model.fingerprint << b)
        lookup.update({h: i for h, i in query.tuples()})

    # This check assumes that `items` contains unique elements
    if check_collisions:
        assert len(lookup) == len(prints)

    missing = []
    for i in items:
        try:
            i._saved = lookup[i.fingerprint]
        except KeyError:
            missing.append(i)
    return missing


###################################################################################
#   MODELS
###################################################################################


##### MIGRATION MODEL #############################################################
class DBMigration(Model):
    """Allows migrations to track versions of the code"""
    class Meta:
        table_name = "migration"

    name: str = CharField(unique=True)
    applied: datetime = DateTimeField(default=datetime.now())


##### STAGE MODEL #################################################################
class DBStage(Model):
    """
    This class is used to store and regenerate config objects
    for future use.

    """

    class Meta:
        table_name = "stage"

    name: str = CharField(
        max_length=255, null=False, index=True, unique=True
    )  # A reference
    created: datetime = DateTimeField(default=datetime.now)

    class_name: str = CharField(max_length=255)  # What object will it will construct
    uuid: UUID = UUIDField(unique=True, default=uuid4)
    meta: Dict = JSONField(default=lambda: {})  # Can we query created/datetimes?
    opts: Dict = JSONField(default=lambda: {})  # Will be loaded into config

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(name='{self.name}', class='{self.class_name}')"
        )

    @classmethod
    def _get_stage_dependents(cls, stage: Stage, deps=None) -> Set[Stage]:
        if deps is None:
            deps = set()

        deps.add(stage)
        for _, link in stage.get_links():
            if isinstance(link, (List, Iterable)):
                for i in link:
                    if i is None or i in deps:
                        continue
                    cls._get_stage_dependents(i, deps)
            else:
                if link is None or link in deps:
                    continue
                cls._get_stage_dependents(link, deps)

        return deps

    @classmethod
    def all_stage_names(cls) -> List[Tuple[str, str, str]]:
        query = cls.select(
            cls.name,
            cls.meta["note"],
            cls.class_name,
            cls.meta["anonymous"],
        )
        return list(query.tuples())

    @classmethod
    def add_stages(cls, stages: List[Stage]) -> List[Stage]:
        """Adds a Stage as the root for a workflow"""
        # TODO: REFACTOR
        all_stages = set()
        for s in stages:
            cls._get_stage_dependents(s, all_stages)

        # Insert the the Stages
        to_add = dedup_and_saveable(all_stages)
        if not to_add:
            return stages

        for stage in to_add:
            stage._use_db = True

        stage_data = [
            (s.__class__.__name__, s.id, s.name, s.meta, s.opts.model_dump(mode="json"))
            for s in to_add
        ]

        insert_many(
            cls,
            (
                cls.class_name,
                cls.uuid,
                cls.name,
                cls.meta,
                cls.opts,
            ),
            stage_data,
        )

        # Now Query the database and get the udpate PKs
        uuids = [s.id for s in to_add]
        db_ids = cls.select(cls.id, cls.uuid).where(cls.uuid << uuids).tuples()

        id_lookup = {uuid: db_id for db_id, uuid in db_ids}
        for s in to_add:
            s._saved = id_lookup[s.id]

        # Link the Stages together
        links = []
        for stage in all_stages:
            for fieldname, linked in stage.get_links():
                if isinstance(linked, Iterable):
                    for i, l in enumerate(linked):
                        if l is None:
                            continue
                        links.append((stage._saved, fieldname, l._saved, True, i))
                else:
                    if linked is None:
                        continue
                    links.append((stage._saved, fieldname, linked._saved, False, 0))

        # Insert Stage Links
        SL = DBStageLink
        insert_many(
            SL,
            (SL.from_stage_id, SL.from_field, SL.to_stage_id, SL.isstack, SL._order),
            links,
            ignore_conflicts=True,
        )

        return stages

    @classmethod
    def get_stages(
        cls, ids: List[int], WORLD: Dict, REGISTRY: Dict
    ) -> Dict[int, Stage]:
        # Load all links into the world
        links = DBStageLink.select_stage_links(ids)

        for stage_data in links.values():
            if stage_data.name not in WORLD:
                reconstitute(stage_data, REGISTRY, WORLD)

        return {i: WORLD[links[i].name] for i in ids}

    @classmethod
    def get_stages_by_name(
        cls, names: List[str], WORLD: Dict, REGISTRY: Dict
    ) -> Dict[str, Stage]:
        # Less efficient than a join but less code to maintain
        query = cls.select(cls.name, cls.id).where(cls.name << names)
        to_id = {n: id for n, id in query.tuples()}
        stages = cls.get_stages(list(to_id.values()), WORLD, REGISTRY)
        return {n: stages[id] for n, id in to_id.items()}

    @classmethod
    def update_options(cls, stage: Stage) -> None:
        if not stage._saved:
            raise ValueError("Only saved stages can be updated")
        cls.update(opts=stage.opts.model_dump(mode="json")).where(
            cls.id == stage._saved
        ).execute()
        print(
            "A stage has been update. Restart the application and reload stages to prevent unintended consiquences!"
        )


##### STAGE-STAGE RELATION #########################################################
class DBStageLink(Model):
    """Stored link between two stages"""

    class Meta:
        table_name = "stage_link"
        constraints = [
            SQL("UNIQUE (from_stage_id, from_field, to_stage_id)"),
        ]

    from_stage = ForeignKeyField(DBStage, field="id", null=False, index=True)
    from_field = CharField(max_length=255)  # Where on the 'from' stage to link to
    to_stage = ForeignKeyField(DBStage, field="id", null=False, index=True)
    isstack = BooleanField(default=False)
    _order = IntegerField(default=0)

    @classmethod
    def select_stage_links(cls, root_ids: List[int]) -> Dict[int, StoredStage]:
        # Do this as a recursive query
        # See https://docs.peewee-orm.com/en/latest/peewee/querying.html#recursive-ctes
        Base = DBStageLink.alias()
        base_case = (
            Base.select(
                Base.from_stage_id,
                Base.from_field,
                Base.to_stage_id,
                Base.isstack,
                Base._order,
            )
            .where(Base.from_stage_id << root_ids)
            .cte("base", recursive=True)
        )

        RTerm = DBStageLink.alias()
        recursive = RTerm.select(
            RTerm.from_stage_id,
            RTerm.from_field,
            RTerm.to_stage_id,
            RTerm.isstack,
            RTerm._order,
        ).join(base_case, on=(RTerm.from_stage_id == base_case.c.to_stage_id))

        cte = base_case.union(recursive)
        query = cte.select_from(
            cte.c.from_stage_id,
            cte.c.from_field,
            cte.c.to_stage_id,
            cte.c.isstack,
            cte.c._order,
        ).order_by(cte.c._order)  # This way we don't have to sort :)

        stage_links = {}
        stage_ids = set(root_ids)
        for _from, _field, _to, _isstack, _order in query.tuples():
            stage_ids.add(_from)
            stage_ids.add(_to)
            # Get the correct stage (as db_id)
            try:
                from_stage = stage_links[_from]
            except KeyError:
                from_stage = {}
                stage_links[_from] = from_stage

            # Update the links dict
            if not _isstack:
                from_stage[_field] = _to
            else:
                try:
                    from_stage[_field].append(_to)
                except KeyError:
                    from_stage[_field] = [_to]

        SM = DBStage
        stage_query = SM.select(
            SM.id, SM.class_name, SM.uuid, SM.name, SM.created, SM.meta, SM.opts
        ).where(SM.id << stage_ids)

        new_stages: Dict[int, StoredStage] = {}
        stage_lookup: Dict[int, str] = {}  # Convert id to name

        # Get data into structured form
        for db_id, class_name, uuid, name, created, meta, opts in stage_query.tuples():
            stage_lookup[db_id] = name
            # meta.update(from_db=True)  # Indicate that this was from a database
            new_stages[db_id] = StoredStage(
                name=name,
                id=uuid,
                links={},  # Populate this in a second loop
                type=class_name,
                created=created,
                meta=meta,
                options=opts,
                db_id=db_id,
            )

        # Now go through stage_links and convert ints to strings
        for stage_data in new_stages.values():
            if stage_data.db_id not in stage_links:
                continue

            links = stage_data.links
            for field, v in stage_links[stage_data.db_id].items():
                if isinstance(v, List):
                    links[field] = [new_stages[i] for i in v]
                    # links[field] = [stage_lookup[i] for i in v]
                else:
                    links[field] = new_stages[v]
                    # links[field] = stage_lookup[v]

        # Put it in the world. Callers can create the final objects
        return new_stages


##### RECORD MODEL ################################################################
class DBRecord(Model):
    class Meta:
        table_name = "record"

    stage = ForeignKeyField(DBStage)
    uuid = UUIDField(unique=True, default=uuid4)

    status: int = IntegerField(default=RecordStatus.PENDING)
    start_time: datetime = DateTimeField(null=True)
    end_time: datetime = DateTimeField(null=True)
    properties: Dict = PropertiesField(null=True)
    meta: Dict = JSONField(null=True)

    @classmethod
    def select_fields(cls):
        return (
            cls.stage_id,
            cls.id,
            cls.uuid,
            cls.status,
            cls.start_time,
            cls.end_time,
            cls.properties,
            cls.meta,
        )

    @classmethod
    def tuple_to_record(
        cls,
        stage: Stage,
        id: int,
        uuid: UUID,
        status: RecordStatus,
        start_time: datetime,
        end_time: datetime,
        properties: props.PropertySet,
        meta: Dict,
        RecordBase: records.Record = records.Record,
        **kwargs,
    ) -> records.Record:
        return RecordBase(
            stage=stage,
            _saved=id,
            id=uuid,
            status=RecordStatus(status),
            start_time=start_time,
            end_time=end_time,
            properties=properties,
            meta={} if meta is None else meta,
            **kwargs,
        )

    @classmethod
    def upsert_records(cls, records: List[Record], add_only=False) -> None:
        if add_only:  # Will only add unsaved records
            to_add = dedup_and_saveable(records)
        else:
            to_add = dedup(records)
        if not to_add:
            return

        record_data = [
            (
                r._saved if r._saved else None,
                r.stage._saved,
                r.id,  # Unsaved will be equal to None
                r.status,
                r.start_time,
                r.end_time,
                # Don't store empty properties or metadata
                r.properties,
                r.meta if r.meta else None,
            )
            for r in to_add
        ]

        insert_many(
            cls,
            (
                cls.id,  # None if this isn't saved
                cls.stage_id,
                cls.uuid,
                cls.status,
                cls.start_time,
                cls.end_time,
                cls.properties,
                cls.meta,
            ),
            record_data,
            replace_conflicts=True,
        )

        # Now Query the database and get the udpate PKs
        uuids = [s.id for s in to_add]
        db_ids = cls.select(cls.id, cls.uuid).where(cls.uuid << uuids).tuples()
        id_lookup = {uuid: db_id for db_id, uuid in db_ids}
        for r in to_add:
            r._saved = id_lookup[r.id]

    @classmethod
    def add_or_update_records(
        cls, records: List[Record], add_only=False
    ) -> List[Record]:
        """Adds a Stage as the root for a workflow"""
        DBStage.add_stages([r.stage for r in records])
        cls.upsert_records(records, add_only=add_only)
        return records

    @classmethod
    def get_records(
        cls, ids: List[int], WORLD: Dict, REGISTRY: Dict, record_kwargs=None
    ) -> Dict[int, T]:
        query = cls.select(*cls.select_fields()).where(cls.id << ids)
        raw_data = [r for r in query.tuples()]

        stages = DBStage.get_stages([d[0] for d in raw_data], WORLD, REGISTRY)

        return {rd[1]: cls.tuple_to_record(stages[rd[0]], *rd[1:]) for rd in raw_data}


class DBCalculationRecord(Model):
    class Meta:
        table_name = "calculation_record"

    record = ForeignKeyField(DBRecord)
    name = CharField(index=True, unique=True)
    steps = JSONField()
    hash = FingerprintField(index=True, unique=True)

    @classmethod
    def get_record_DBID(cls, records: List[CalculationRecord]) -> None:
        to_check = dedup_and_saveable(records)

        lookup = {}
        # TODO: Benchmark both approaches
        for chunk in chunked(to_check, 50):
            query = (
                cls.select()
                .join(DBRecord)
                .select(
                    cls.id,
                    cls.hash,
                    DBRecord.stage_id,
                )
                .where(cls.hash << [c.hash for c in chunk])
            )
            lookup.update({h: (i, sid) for i, h, sid in query.tuples()})

        for record in to_check:
            rid, sid = lookup.get(record.hash.hexdigest(), (0, 0))
            if rid:
                record._saved = rid
                record.stage._saved = sid

    @classmethod
    def add_or_update_calculation_record(
        cls, records: List[CalculationRecord], add_only=False
    ) -> List[CalculationRecord]:
        """This can add duplicate records if we are not carful. Make sure to
        check for existing records before adding a new one
        """
        # Check if records already exist
        cls.get_record_DBID(records)

        # Prevent double-checking if system is saved and record is changed
        to_link = [r for r in records if not r._saved]

        # TODO: Check that the system -- record.backend are unique in the database
        DBRecord.add_or_update_records(records, add_only=add_only)

        # Now add all unsaved Calculation records
        insert_many(
            cls,
            (cls.record_id, cls.name, cls.steps, cls.hash),
            ((r._saved, r.name, r.steps, r.hash) for r in to_link),
        )
        return records

    @classmethod
    def all_calculation_names(cls) -> List[Tuple[str, RecordStatus, str]]:
        query = (
            cls.select()
            .join(DBRecord)
            .select(cls.name, DBRecord.status, DBRecord.meta["note"])
        )
        return list(query.tuples())

    @classmethod
    def get_calculation_records_by_hash(
        cls,
        stage: Stage,
        hashes: List["hashlib._Hash"],
        status: Optional[List[RecordStatus]] = None,
    ) -> Dict["hashlib._Hash", CalculationRecord]:
        # Stage must be saved for this to work
        if not stage._saved:
            return {}

        # Get link data
        query = (
            DBRecord.select()
            .join(cls)
            .select(cls.name, cls.steps, *DBRecord.select_fields())
            .where((cls.hash << hashes) & (DBRecord.stage_id == stage._saved))
        )
        if status:
            query = query.where(DBRecord.status << status)

        records = [
            DBRecord.tuple_to_record(
                stage,
                *rec_data[3:],
                RecordBase=CalculationRecord,
                name=rec_data[0],
                steps=rec_data[1],
            )
            for rec_data in query.tuples()
        ]
        return {r.hash.hexdigest(): r for r in records}

    @classmethod
    def get_calculation_records_by_name(
        cls, stage: Stage, names: List[str], status: Optional[List[RecordStatus]] = None
    ) -> Dict[str, CalculationRecord]:
        # Stage must be saved for this to work
        if not stage._saved:
            return {}

        # Get link data
        query = (
            DBRecord.select()
            .join(cls)
            .select(cls.name, cls.steps, *DBRecord.select_fields())
            .where((cls.name << names) & (DBRecord.stage_id == stage._saved))
        )
        if status:
            query = query.where(DBRecord.status << status)

        records = [
            DBRecord.tuple_to_record(
                stage,
                *rec_data[3:],
                RecordBase=CalculationRecord,
                name=rec_data[0],
                steps=rec_data[1],
            )
            for rec_data in query.tuples()
        ]
        return {r.name: r for r in records}
