#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#

# Add the constraint that these blocks are stateless. They cannot be combined
# with systems or view or whatnot
# Descriptor for a deferred pipeline attribute
from datetime import datetime
from inspect import getmembers
from typing import (
    Any,
    ClassVar,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)
from uuid import UUID, uuid4

import pydantic
from pydantic import BaseModel

from conformer_core.accessors import FilterCompositeAccessor, ModCompositeAccessor
from conformer_core.util import ind, summarize

# from conformer_core.accessors import Accessor

World = Dict["str", "Stage"]
DEFAULT_WORLD: World = {}


class StageException(Exception):
    ...


class StageInWorldException(StageException):
    ...


class StageOptions(BaseModel):
    ...


class Stage:
    # Class Variables
    Options: Type[StageOptions] = StageOptions

    # Instance variables
    id: UUID
    name: str
    created: datetime
    meta: Dict[str, Any]
    opts: StageOptions  # Instance of options
    _world: World = DEFAULT_WORLD  # Object is share among all blocks by default
    _link_atrs: ClassVar[Tuple[str, ...]] = tuple()
    _use_db: bool
    _saved: int

    def __init_subclass__(cls) -> None:
        cls._link_atrs = tuple(
            (name for name, _ in getmembers(cls, lambda x: isinstance(x, Link)))
        )
        return super().__init_subclass__()

    def __init__(
        self,
        options: Optional[StageOptions] = None,
        name: str = None,
        id: Optional[UUID] = None,
        meta: Dict[str, Any] = None,
        created: Optional[datetime] = None,
        links: Optional[Dict[str, str]] = None,
        _saved: Optional[int] = 0,
        _use_db: Optional[bool] = False,
        _world: Optional[World] = DEFAULT_WORLD,
        _delay_init=False,
    ) -> None:
        super().__init__()  # Fixes issue with multiple inheretance/PropertyExtractorMixin
        self.opts = options if options else self.Options()
        self._world = _world
        self._saved = _saved

        # Initialize the defaults
        self.id = uuid4() if id is None else id
        self.name = str(self.id) if name is None else name
        self.meta = {} if meta is None else meta
        self.created = datetime.now() if created is None else created
        self._use_db = _use_db

        # Add add this stage to the world
        if self.name in self._world:
            raise StageInWorldException(
                f"A stage named '{self.name}' is already exists."
            )
        else:
            # On some level this seems like a recipe for memory leaks
            self._world[self.name] = self

        # Mark as anonymouse if it wasn't given a formal name
        if name is None:
            self.meta["anonymous"] = True

        # Make soft links for all items in the world
        if links:
            for l, v in links.items():
                setattr(self, l, v)

        if not _delay_init:
            self.__init_stage__()

    def __init_stage__(self):
        pass

    def __del__(self):
        """Remove itself from the world"""
        try:
            del self._world[self.name]
        except KeyError:
            pass

    @classmethod
    def from_options(
        cls,
        name: str = None,
        id: Optional[UUID] = None,
        meta: Optional[Dict[str, Any]] = None,
        links: Optional[Dict[str, str]] = None,
        _world: Optional[World] = DEFAULT_WORLD,
        **kwargs,
    ):
        """Builds a config from keyword arguments instead of an explicit config"""
        return cls(
            cls.Options(**kwargs),
            name=name,
            id=id,
            meta=meta,
            links=links,
            _world=_world,
        )

    def get_links(self):
        for name in self._link_atrs:
            yield (name, getattr(self, name))

    # Customize pickle behaviour
    def acturalize_links(self):
        """Iterates through all link fields and actualizes the fields"""
        for l in self._link_atrs:
            s = getattr(self, l)
            if isinstance(s, Stage):
                s.acturalize_links

    def __getstate__(self) -> Any:
        self.acturalize_links()  # Access all linked stages
        state = self.__dict__.copy()
        if "_world" in state:
            del state["_world"]
        return state

    def __setstate__(self, state: Dict) -> None:
        # These don't have a world
        self.__dict__.update(state)
        if not hasattr(self, "_world"):
            self._world = {}

    # Hashing
    def __hash__(self) -> int:
        return self.name.__hash__()

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, self.__class__):
            return False
        return __value.name == self.name and __value.id == self.id

    def summarize(self, padding=2, level=0) -> str:
        rec_str = ind(padding, level, f"Stage {self.name}: \n")

        level += 1
        rec_str += ind(padding, level, f"Type: {self.__class__.__name__}\n")
        rec_str += ind(padding, level, f"ID: {self.id}\n")
        rec_str += ind(
            padding, level, f"Created: {self.created.isoformat(timespec='minutes')}\n"
        )

        links = list(self.get_links())
        if links:
            rec_str += ind(padding, level, "Links:\n")
            for k, v in links:
                if v is None:
                    _v = "<None>"
                elif isinstance(v, Iterable):
                    _v = [i.name for i in v]
                    if not _v:
                        _v = "<empty>"
                else:
                    _v = v.name
                rec_str += summarize(k, _v, padding=padding, level=level + 1)

        options = self.opts.model_dump(mode="json")
        if options:
            rec_str += summarize("Options", options, padding=padding, level=level)

        if self.meta:
            rec_str += summarize("Meta", self.meta, padding=padding, level=level)

        return rec_str


LinkType = Optional[Union[str, Stage]]


class Link:
    def set(self, obj, value, isdirty=True):
        setattr(obj, self.private_name, (value, isdirty))

    def clean(self, obj, value):
        if isinstance(value, str):
            value = obj._world[value]
        elif isinstance(value, Stage):
            pass  # This is ok
        elif value is None:
            pass  # This is also ok
        else:
            raise ValueError(f"Links cannot be of type {type(value)}")
        return value

    """Reference to another stage"""

    def __set_name__(self, owner, name):
        self.private_name = "_" + name

    def __get__(self, obj: Stage, objtype=None) -> List["Stage"]:
        try:
            val, isdirty = getattr(obj, self.private_name)
        except AttributeError:  # We want links to be optional
            val = None
            isdirty = True

        if isdirty:
            val = self.clean(obj, val)
            self.set(obj, val, isdirty=False)
        return val

    def __set__(self, obj, value):
        self.set(obj, value, isdirty=True)


StackType = Optional[List[Union[str, Stage]]]


class Stack(Link):
    """An 'array' of stages"""

    def clean(self, obj, stack):
        if stack is None:
            return []
        _stack = []
        for val in stack:
            val = super().clean(obj, val)
            if val is None:
                continue
            _stack.append(val)
        return _stack


class ModStack(Stack):
    def clean(self, obj, stack):
        val = super().clean(obj, stack)
        return ModCompositeAccessor(val)


class FilterStack(Stack):
    def clean(self, obj, stack):
        val = super().clean(obj, stack)
        return FilterCompositeAccessor(val)


####   YAML-BASED STORAGE   ####
class StoredStage(BaseModel):
    """
    Pydantic model for parsing/storing Stage data
    """

    type: str  # Which class to use to reconstitute this model
    id: Optional[UUID] = None
    name: Optional[str] = None
    note: Optional[str] = None  # stored in Stage.meta
    options: Optional[Dict[str, Any]] = pydantic.Field(
        default_factory=dict
    )  # Will be passed to Stage.Options
    links: Optional[
        Dict[str, Union[Union[str, "StoredStage"], List[Union[str, "StoredStage"]]]]
    ] = pydantic.Field(default_factory=dict)
    created: Optional[datetime] = pydantic.Field(default_factory=dict)
    meta: Dict[str, Any] = pydantic.Field(default_factory=dict)
    db_id: int = 0


def get_stage_names(stage: StoredStage | str, names: Set[str] | None) -> Set[str]:
    """Retrieves all stage names from a StoredStage"""
    if names is None:
        names = set()

    # Handle case where stage is str
    if isinstance(stage, str):
        names.add(stage)
        return  # Stop!

    if stage.name:
        names.add(stage.name)

    for link in stage.links.values():
        if isinstance(link, List):
            get_stage_names_from_list(link, names)
        else:
            get_stage_names(link, names)

    return names


def get_stage_names_from_list(
    stages: List[StoredStage | str], names: Set[str] | None = None
) -> Set[str]:
    """Retrieves all stage names from a list of StoredStage information"""
    if names is None:
        names = set()

    for stage in stages:
        get_stage_names(stage, names)
    return names


def reconstitute(
    data: StoredStage, stage_registry: Dict[str, Type[Stage]], world: Dict[str, Stage]
) -> Stage:
    # If stage exists, return the existing version!
    if data.name and data.name in world:
        stage = world[data.name]
        if data.type != stage.__class__.__name__:
            raise Exception(
                f"Stored data is requesting a Stage of type {data.type} but the Stage in the registry is of type {stage.__class__.__name__}"
            )
        return stage  # Use the existing stage

    # Immediatly create the stage. Handle links later (prevents infinite loops)
    StageClass = stage_registry[data.type]

    if data.note and "note" not in data.meta:
        data.meta["note"] = data.note
    stage = StageClass(
        name=data.name,
        id=data.id,
        meta=data.meta,
        created=data.created,
        options=StageClass.Options(**data.options),
        _world=world,
        _use_db=data.db_id > 0,
        _saved=data.db_id,
    )

    # Handle links. Stored stages will be reconstituted.
    for k, l in data.links.items():
        # Scalar links...
        if isinstance(l, str):  # Link is a string
            setattr(stage, k, world[l])
            # links[k] = l
        elif isinstance(l, List):  # If links are part of a stack...
            sub_list = []
            for _l in l:
                if isinstance(_l, str):
                    sub_list.append(_l)
                elif isinstance(_l, StoredStage):
                    rec = reconstitute(_l, stage_registry, world)  # Do this recursivly
                    sub_list.append(rec)
            setattr(stage, k, sub_list)
        elif isinstance(l, StoredStage):  # Link is anonymous
            rec = reconstitute(l, stage_registry, world)  # Do this recursivly
            setattr(stage, k, rec)

    stage.__init_stage__()
    return stage
