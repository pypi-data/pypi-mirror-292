#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import shutil
from datetime import datetime
from functools import wraps
from inspect import signature
from os import environ
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Iterator,
    List,
    Optional,
    Tuple,
    Type,
    get_args,
    get_origin,
)
from uuid import UUID

import peewee as pw
import pydantic
from playhouse.sqlite_ext import SqliteExtDatabase

from conformer.db.models import DBSystem, DBSystemLabel, DBSystemRecord
from conformer.geometry_readers.common import SupersystemModel
from conformer.geometry_readers.util import read_geometry
from conformer.stages import Calculation, GetSystem, Identifyer, get_systems
from conformer.systems import NamedSystem, System
from conformer_core.calculation import CalculationRecord
from conformer_core.db.migrations.__main__ import (
    apply_migrations,
    check_migrations,
    fake_migrations,
)
from conformer_core.db.models import DBCalculationRecord, DBRecord, DBStage
from conformer_core.properties.core import PropertySet
from conformer_core.records import Record, RecordStatus
from conformer_core.registry import (
    Config,
    load_app,
    load_models,
    load_stages,
    load_yaml,
)
from conformer_core.stages import (
    Stage,
    StageInWorldException,
    StoredStage,
    get_stage_names_from_list,
    reconstitute,
)

NULL_STAGE_NAME = "_calculation"
GET_SYSTEM_STAGE_NAME = "_get_system"


class CalculationModel(pydantic.BaseModel):
    steps: List[str]
    systems: List[str]

    name: Optional[str] = None
    note: Optional[str] = None


def db_method(fn):
    """Method decorator for binding a project database before running"""

    @wraps(fn)
    def wrapper(self: "Project", *args, **kwargs):
        with self:
            return fn(self, *args, **kwargs)

    return wrapper


class ProjectException(Exception):
    """Exception for Project-related errors."""

    ...


class UnknownStageException(ProjectException):
    """Exception raised if Stage is not in the database."""

    ...


class UnknowCalculationException(ProjectException):
    """Exception raised if Calculation is not in database"""

    ...


def _pass_fn(*args, **kwargs): ...


def wrap_to_generator(fn: Callable, *args) -> Generator:
    yield
    return fn(*args)


def parse(T: Type, S: str) -> Any:
    if get_origin(T) is None:
        return T(S)
    for _T in get_args(T):
        try:
            return _T(S)
        except ValueError:
            pass
    raise ValueError(f"Could not parse '{S}' as {T}")


class Project:
    # PATH DATA
    PATH: Path

    # GENERAL
    DEFAULT_CONFIG = "conformer"
    CONFIG: Config

    # STAGES
    STAGE_WORLD: Dict[str, Stage]
    STAGE_REGISTRY: Dict[str, Type[Stage]]
    STAGE_SOURCES = ("stages",)
    SYSTEM_SOURCES = ("systems",)

    # DATABASE
    DB: pw.Database
    DB_MODELS: List[pw.Model]
    DB_NAME: str
    DB_TMPDIR: Optional[Path]

    # CALCULATIONS
    CALC_RESERVED_WORDS = {"system", "driver"}

    # HOOKS
    HOOKS = Dict["str", Callable]
    HOOKS_DEFAULT = {
        "calc_start": _pass_fn,
        "calc_finish": _pass_fn,
        "stages_add": _pass_fn,
        "systems_add": _pass_fn,
        "calculations_add": _pass_fn,
        "calculation_status": _pass_fn,
        "calculation_start_step": _pass_fn,
        "calculation_finish_step": _pass_fn,
        "calculation_failed": _pass_fn,
        "wrap_driver_accessor": lambda x, y: x.as_completed(),
    }

    # INTERNAL
    debug: bool
    _bound: int

    def __init__(
        self,
        base_path: str | Path | None = None,
        db_name: str | None = None,
        tmpdir: str | Path | None = None,
        hooks: Dict | None = None,
        debug=False,
        cpus: int | None = None,
        **settings
    ) -> None:
        # Internal flags
        self.debug = debug
        self._bound = 0

        # Configure paths
        if base_path is None:
            self.PATH = Path.cwd()
        elif isinstance(base_path, str):
            self.PATH = Path(base_path).absolute()
        else:
            self.PATH = base_path.absolute()

        # Handle an out-of-path run
        if tmpdir:
            self.DB_TMPDIR = Path(tmpdir)
        else:
            self.DB_TMPDIR = None

        # Configure registry
        if (self.PATH / "settings.yaml").exists():
            with (self.PATH / "settings.yaml").open("r") as f:
                config = Config(**load_yaml(f))
            if self.DEFAULT_CONFIG not in config.requires:
                config.requires.append(self.DEFAULT_CONFIG)
        else:
            config = self.DEFAULT_CONFIG
        self.CONFIG = load_app(config)
        self.CONFIG.settings.update(settings)

        # Update the environment
        for k, v in self.CONFIG.environment_vars.items():
            environ[k] = v

        # Configure Stages
        self.STAGE_REGISTRY = load_stages(self.CONFIG)
        self.STAGE_WORLD = {}

        # Configure the database
        self.configure_database(db_name)

        self.HOOKS = self.HOOKS_DEFAULT.copy()
        if hooks:
            self.HOOKS.update(hooks)

    def configure_database(self, db_name, migrate=False):
        # Configure the database
        if not db_name:
            db_name = self.CONFIG.settings["DB_NAME"]

        if db_name == ":memory:":
            self.DB_NAME = db_name
            make_tables = True
        else:
            # Handle temporary database
            DB_NAME: Path = self.PATH / db_name
            if self.DB_TMPDIR:
                # Make a backup. We don't trust ourselves!
                print(f"Making a backup of {DB_NAME.name}")
                backup_file = DB_NAME.parent / (DB_NAME.name + ".backup")
                DB_NAME.rename(backup_file)

                print(f"Copying {backup_file} to {self.DB_TMPDIR}")
                shutil.copy(
                    backup_file, self.DB_TMPDIR / backup_file.stem
                )  # Strip off the ".backup" flag
                print(f"All changes will be written to {backup_file}")

                # Redefine to point to temp dir version
                self.DB_NAME = self.DB_TMPDIR / DB_NAME.name
            else:
                self.DB_NAME = DB_NAME
            make_tables = not self.DB_NAME.exists()

        self.DB_MODELS = load_models(self.CONFIG)
        self.DB = SqliteExtDatabase(
            self.DB_NAME,
            pragmas=(
                ("foreign_keys", "ON"),
                # ('journal_mode', 'wal') # !!! DOES NOT WORK ON NFS
            ),
        )

        # List of things which should happen only once.
        if make_tables:
            with self.DB.bind_ctx(self.DB_MODELS):
                self.DB.create_tables(self.DB_MODELS)
                DBStage.add_stages(
                    [
                        Calculation.from_options(
                            name=NULL_STAGE_NAME,
                            meta={
                                "note": "Stage to indicate calculation. Added automatically to new projects."
                            },
                        ),  # INTERNAL null stage
                        GetSystem.from_options(
                            name=GET_SYSTEM_STAGE_NAME,
                            meta={
                                "note": "Retrieves a NamedSystem from the database. Added automatically to new projects."
                            },
                        ),
                    ]
                )
                # Since this is a new database apply all the migrations
                # _, missing = self.check_migrations()
                fake_migrations(self.check_migrations()[1])
        else:
            # Check that migrations are applied. If they are not, refuse to run!
            _, missing = self.check_migrations()
            if missing and self.CONFIG.settings.get("check_migrations", True):
                raise Exception("Missing migrations!")
                for n, m in missing:
                    print("    ", m)

    def __enter__(self) -> None:
        if not self._bound:
            self._bind_ctx = self.DB.bind_ctx(self.DB_MODELS)
            self._bind_ctx.__enter__()
        self._bound += 1

    def __exit__(self, type_, value, traceback):
        self._bound -= 1
        if not self._bound:
            self._bind_ctx.__exit__(type_, value, traceback)

    def __del__(self) -> None:
        if hasattr(self, "DB"):
            with self:
                # RUN ANALYZE ON EXIT
                self.DB.pragma("analysis_limit", 400)
                self.DB.pragma("optimize")
            self.DB.close()
        if self.DB_TMPDIR and hasattr(self, "DB_NAME") and self.DB_NAME.exists():
            print("Copying back the temporary database")
            shutil.copy(self.DB_NAME, self.PATH / self.DB_NAME.name)

    def run_hook(self, hook_name, *args) -> Any:
        fn = self.HOOKS[hook_name]
        return fn(*args)

    def normalize_path(self, path: str | Path, *args, **kwargs) -> Path:
        if isinstance(path, str):
            path = Path(path)
        return path.absolute()

    def load_file_data(self, path: str | Path) -> Dict["str", Any]:
        path = self.normalize_path(path)
        if not path.exists():
            raise FileNotFoundError(f"The file {str(path)} does not exist.")

        if path.suffix in (".yaml", ".yml"):
            with path.open("r") as f:
                res = load_yaml(f)
                return res
        elif path.suffix in (".py"):
            return self.run_python_script(path)

        raise ValueError(f"Cannot load file {path}")
        # TODO: Do this for TOML and other file types
        # TODO: Do for Python scripts

    @db_method
    def run_python_script(self, path: Path) -> None:
        script = path.read_text()
        with path.open("r") as f:
            project = self
            exec(script, globals(), locals())

    # Stage methods
    def import_stages(
        self, data: str | Path | Dict, keys=None, add_to_db=False
    ) -> Dict[str, Stage]:
        if isinstance(data, (str, Path)):
            _data = self.load_file_data(data)
        else:
            _data = data

        # Load stages from database
        if keys is None:  # generally not greate
            keys = data.keys()

        stored_stages = []
        for key in keys:
            if key not in _data:
                continue
            stored_stages.extend([StoredStage(**d) for d in _data[key]])

        self.get_stages(*get_stage_names_from_list(stored_stages), _check_missing=False)
        old_stages = set(self.STAGE_WORLD.keys())

        # Now parse stages (skip those those in WORLD)
        for d in stored_stages:
            try:
                reconstitute(d, self.STAGE_REGISTRY, self.STAGE_WORLD)
            except StageInWorldException:
                pass  # Is there a better way to handle it?

        # Summarize what we added
        new_stages = set(self.STAGE_WORLD.keys()).difference(old_stages)
        if add_to_db:
            self.add_stages(*(self.STAGE_WORLD[s] for s in new_stages))
        return {d.name: self.STAGE_WORLD[d.name] for d in stored_stages if d.name}

    @db_method
    def add_stages(self, *stages: Stage) -> None:
        DBStage.add_stages(list(stages))
        self.run_hook("stages_add", stages)

    @db_method
    def get_stages(self, *stage_names: str, _check_missing=True) -> Dict["str", Stage]:
        stages = {}
        to_query = set()
        for name in stage_names:
            try:
                stages[name] = self.STAGE_WORLD[name]
            except KeyError:
                to_query.add(name)

        # Handle stages which are not in the database
        db_stages = DBStage.get_stages_by_name(
            to_query, self.STAGE_WORLD, self.STAGE_REGISTRY
        )
        stages.update(db_stages)

        if _check_missing and set(stage_names) != set(stages.keys()):
            missing_names = ", ".join(set(stage_names).difference(set(stages.keys())))
            raise UnknownStageException(
                f"Project does not contain stage(s) with the name(s): {missing_names}"
            )
        return stages

    def get_stage(self, stage_name: str) -> Stage:
        return self.get_stages(stage_name)[stage_name]

    @db_method
    def update_stage(self, stage: Stage) -> None:
        DBStage.update_options(stage)

    @db_method
    def get_stage_names(self) -> List[Tuple[str, str, str]]:
        return DBStage.all_stage_names()

    # System methods
    def import_systems(
        self, data: str | Path | Dict, key="systems", add_to_db=False
    ) -> Dict[str, NamedSystem]:
        if isinstance(data, (str, Path)):
            _data = self.load_file_data(data)
        else:
            _data = data

        to_add = [SupersystemModel(**d) for d in _data[key]]
        check_names = set()
        for s in to_add:
            check_names.add(s.name)
            if s.subsystems is None:
                continue
            for ss in s.subsystems:
                check_names.add(ss.name)

        systems = DBSystemLabel.get_systems_by_name(check_names)
        add_names = check_names.difference(set(systems.keys()))

        # Loop through again and add new systems!
        for s in to_add:
            if s.name in add_names:
                systems[s.name] = self.read_geometry(
                    s.name,
                    s.source,
                    note=s.note,
                    charges=s.charges,
                    roles=s.roles,
                    unit_cell=s.unit_cell,
                )

            # Add subsystems
            if s.subsystems is None:
                continue
            for ss in s.subsystems:
                subsys = systems[s.name].subsystem(ss.include)
                # TODO: Update role
                # TODO: Update charges
                systems[ss.name] = NamedSystem.from_system(
                    subsys,
                    name=ss.name,
                    meta={
                        "note": ss.note if ss.note else f"Subsystem of {s.name}",
                        "derived_from": s.name,
                    },
                )
        if add_to_db:
            self.add_systems(*(systems[n] for n in add_names))
        return systems

    def read_geometry(
        self, name: str, path: str, add_to_db=False, **kwargs
    ) -> NamedSystem:
        """Wrapper around `read_geometry` method from Conformer"""
        # TODO: Relative path
        file_path = Path(path)
        if not file_path.exists():
            raise ValueError(f"Geometry file `{path}` does not exist.")
        sys = read_geometry(name, source=path, **kwargs)

        if add_to_db:
            self.add_systems(sys)
        return sys

    @db_method
    def get_systems(self, *identifyer: str | int) -> System | Dict[Identifyer, System]:
        """Retrieves multiple NamedSystems from the database"""
        return get_systems(*identifyer)

    @db_method
    def add_systems(self, *sys: System):
        """Adds System to the project database"""
        DBSystem.add_systems(list(sys))
        self.run_hook("systems_add", sys)

    @db_method
    def import_strategy(self, path: str | Path, add_to_db=True):
        data = self.load_file_data(path)
        if not data:
            return

        # Load all stages
        self.import_stages(data, keys=self.STAGE_SOURCES, add_to_db=add_to_db)

        # Load all systems
        for section in self.SYSTEM_SOURCES:
            if section in data:
                self.import_systems(data, key=section, add_to_db=add_to_db)

        if "calculations" in data:
            self.import_calculations(data, key="calculations")

    def import_calculations(
        self, data: str | Path | Dict, key="calculations", add_to_db=False
    ) -> None:
        if isinstance(data, (str, Path)):
            _data = self.load_file_data(data)
        else:
            _data = data

        # Load stages from database
        calcs = [CalculationModel(**d) for d in _data[key]]

        # Now parse stages (skip those those in WORLD)
        for c in calcs:
            self.add_calculations(c.systems, c.steps, c.name, c.note)

    @db_method
    def get_calculations(self, *calc_names: str) -> Dict[str, CalculationRecord]:
        if "ALL" in calc_names:
            calc_names = [c[0] for c in DBCalculationRecord.all_calculation_names()]

        calcs = DBCalculationRecord.get_calculation_records_by_name(
            self.get_stage(NULL_STAGE_NAME), list(calc_names)
        )
        if set(calc_names) != set((c.name for c in calcs.values())):
            missing = set(calc_names).difference(set((c.name for c in calcs.values())))
            raise UnknowCalculationException(
                f"The database does not cantain calculations named {', '.join(missing)}"
            )
        return calcs

    def get_calculation(self, calc_name) -> CalculationRecord:
        # return self.get_calculations(calc_name)[calc_name]
        ret = self.get_calculations(calc_name)[calc_name]
        return ret

    @db_method
    def add_calculations(
        self,
        system_names: List["str"],
        steps: List["str"],  # steps needs to be parsed
        name: str | None = None,
        note: str | None = None,
        run: bool = False,
    ) -> List[CalculationRecord]:
        # Parse the steps
        stage_names = []
        stage_arg_strs = []
        for _line in steps:
            line = _line.strip()
            if line[-1] == ")":
                stage_name, arg_str = line[:-1].rsplit("(", maxsplit=1)
                args = tuple(arg_str.split(","))
            else:
                stage_name = line
                args = tuple()
            stage_names.append(stage_name)
            stage_arg_strs.append(args)

        _stages = set(stage_names)
        stages = self.get_stages(NULL_STAGE_NAME, GET_SYSTEM_STAGE_NAME, *_stages)

        # Convert args from strings
        # TODO: This is fragile
        steps = []
        for sn, args in zip(stage_names, stage_arg_strs):
            # Introspect arguments
            stage = stages[sn]
            sig = signature(stage)
            params = list(sig.parameters.values())
            param_list = []
            for param, val in zip(params[1:], args):
                param_list.append(parse(param.annotation, val.strip()))
            # Build the steps
            steps.append((sn, tuple(param_list)))

        if note:
            meta = {"note": note}
        else:
            meta = {}

        # Check that all systems exist
        systems = self.get_systems(*system_names)

        if name is None:
            _name_parts = []
            for n, args in steps:
                if args:
                    part = n + "(" + ", ".join([str(a) for a in args]) + ")"
                else:
                    part = n
                _name_parts.append(part)
            name = "--".join(_name_parts)

        calculations = []
        for sys_name in systems.keys():
            record = CalculationRecord(
                stage=stages[NULL_STAGE_NAME],
                name=sys_name + "--" + name,
                meta=meta,
                steps=[(GET_SYSTEM_STAGE_NAME, (sys_name,))] + steps,
            )
            calculations.append(record)

        # Exclude calculations which already exist
        DBCalculationRecord.get_record_DBID(calculations)

        # Should not overwrite...
        to_add = [c for c in calculations if not c._saved]
        DBCalculationRecord.add_or_update_calculation_record(to_add, add_only=True)
        self.run_hook("calculations_add", name, to_add)

        # Optionally run calculations
        # Let run get a fresh copy
        if run:
            self.run_calculations(*(c.name for c in calculations))

        return calculations

    @db_method
    def run_calculations(
        self, *calc_names, rerun: bool = False, limit=20
    ) -> Dict["str", CalculationRecord]:
        calcs = self.get_calculations(*calc_names)
        to_run = list(calcs.keys())
        activate_calcs = []

        # Top off the active calcs
        while to_run and len(activate_calcs) <= limit:
            calc_name = to_run.pop()
            activate_calcs.append(self._run_calculation(calc_name, rerun=rerun))

        completed_cals = {}
        while activate_calcs:
            to_remove = []
            for i, calc in enumerate(activate_calcs):
                try:
                    _ = next(calc)
                except StopIteration as e:
                    record = e.value
                    completed_cals[record.name] = record
                    to_remove.append(i)
                # Update the app about how were are doing
                self.run_hook("calculation_status", self, completed_cals, False)

            # Remove completed calculations
            to_remove.reverse()
            for i in to_remove:
                activate_calcs.pop(i)

            # Top off the active calcs again
            while to_run and len(activate_calcs) <= limit:
                calc_name = to_run.pop()
                activate_calcs.append(self._run_calculation(calc_name, rerun=rerun))

        self.run_hook("calculation_status", self, completed_cals, True)
        return completed_cals

    @db_method
    def _run_calculation(
        self, calc: CalculationRecord | str, rerun: bool = False
    ) -> Generator[None, None, CalculationRecord]:
        if isinstance(calc, str):
            calc = self.get_calculation(calc)

        if not (calc.status == RecordStatus.PENDING or rerun):
            return calc

        self.run_hook("calc_start", calc)

        stages = self.get_stages(*(p[0] for p in calc.steps))
        callable_steps = [(stages[s], a) for s, a in calc.steps]

        try:
            value = None
            for stage, args in callable_steps:
                self.run_hook("calculation_start_step", stage, args, value)
                _step_itr = self.call_stage(value, stage, args)
                while True:
                    try:
                        next(_step_itr)
                        yield
                    except StopIteration as e:
                        value = e.value
                        self.run_hook("calculation_finish_step", stage, args, value)
                        break

            calc.status = RecordStatus.COMPLETED
            if isinstance(value, Record):
                # Copy over as much information as possible
                calc.properties = value.properties
                calc.status = value.status
                calc.meta = value.meta
            elif isinstance(value, PropertySet):
                calc.properties = value

        except Exception as e:
            calc.status = RecordStatus.FAILED
            calc.meta["error"] = (
                e.__class__.__name__ + ": " + str(e)
            )  # What should I really put here?
            calc.meta["failed_on"] = stage.name
            self.run_hook("calculation_failed", stage, args, value)
            if self.debug:
                raise e
        finally:
            calc.end_time = datetime.now()
            DBCalculationRecord.add_or_update_calculation_record([calc])

        self.run_hook("calc_finish", calc)
        return calc

    def call_stage(self, in_value, stage, args) -> Generator[None, None, Any]:
        if hasattr(stage, "as_generator"):
            return stage.as_generator(in_value, *args)
        return wrap_to_generator(stage, in_value, *args)

    @db_method
    def failed_calculations(self, limit=0) -> Iterator[Tuple[UUID, str]]:
        query = (
            DBRecord.select()
            .join(DBStage)
            .select(DBStage.name, DBRecord.uuid)
            .where(DBRecord.status == RecordStatus.FAILED)
        )
        if limit:
            query = query.limit(limit)
        for name, id in query.tuples():
            yield name, id

    @db_method
    def get_system_records(self, *record_ids: str) -> Dict[UUID, Record]:
        return DBSystemRecord.get_record_by_uuid(
            record_ids, self.STAGE_WORLD, self.STAGE_REGISTRY
        )

    @db_method
    def check_migrations(self) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
        return check_migrations(self.CONFIG.requires)

    
    @db_method
    def run_migrations(self) -> None:
        apply_migrations(self.PATH, self.check_migrations()[1])
