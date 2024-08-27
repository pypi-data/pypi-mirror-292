#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import importlib
import importlib.machinery
import importlib.util
from datetime import UTC, datetime
from importlib.machinery import ModuleSpec
from pathlib import Path
from pkgutil import iter_modules
from sys import argv
from typing import Any, Dict, List, Tuple

from conformer_core.db.models import DBMigration

MIGRATION_PREFIX = "migration_"
MIGRATION_TEMPLATE = '''
"""Migration {name}

Please explain why this migration is necessary
"""
import peewee


def migrate(project_path: str, database_path: peewee.Database) -> None:
    ...
'''

def create_migration(module_name: str) -> None:
    """Creates a new migration file in the given `module`

    Migration name is the UTC date and time of creation. This allows 
    migration to be applied in the order in which they were added to the project. 
    """
    now = datetime.now(UTC)
    spec = get_migrations_modules([module_name])[0]
    # now.tzinfo = None
    # now.microsecond = 0
    # TODO: Check that this is a local install
    if "/site-packeges/" in spec.origin:
        raise ValueError(f"Module `{spec.name.name}` is not installed for development.")
    migration_name = MIGRATION_PREFIX + now.strftime("%Y%m%d_%H%M%S") + ".py"

    path = Path(spec.origin).parent / migration_name
    with path.open("w") as f:
        f.write(MIGRATION_TEMPLATE.format(name=migration_name))
    print("A New empty migration has been created:")
    print("  ", path.absolute())

def get_migrations_modules(module_names: List[str]) -> List[ModuleSpec]:
    """
    Opens a conformer-based projet and returns the module corresponding to the migrations folder
    """
    specs = []
    for module_name in module_names:
        module_str = module_name + ".db.migrations"
        try:
            mod_spec = importlib.util.find_spec(module_str)
        except ModuleNotFoundError:
            continue
        if mod_spec is not None:
            specs.append(mod_spec)
    return specs

def gather_migrations(module_names: List[ModuleSpec]) -> List[ModuleSpec]:
    parent_specs = get_migrations_modules(module_names)

    migrations: List[ModuleSpec] = []
    for pspec in parent_specs:
        for m in iter_modules(pspec.submodule_search_locations):
            if m.name.startswith(MIGRATION_PREFIX):
                migrations.append((m.name, pspec.name + "." + m.name))
    migrations.sort(key=lambda x: x[0])
    return migrations

def check_migrations(module_names: List[str]) -> Dict[str, Any]:
    migrations = gather_migrations(module_names)
    current_migrations = migration_data()

    applied_migrations = []
    missing_migrations = []
    for n, m in migrations:
        if n in current_migrations:
            applied_migrations.append((n, m))
        else:
            missing_migrations.append((n, m))
    return applied_migrations, missing_migrations

def apply_migrations(project_path: str, migration_list: List[Tuple[str, str]]) -> None:
    database = DBMigration._meta.database
    with database.atomic():
        for n, m in migration_list:
            print(f"Applying migration {n}")
            mod = importlib.import_module(m)
            if hasattr(mod, "migrate"):
                mod.migrate(project_path, DBMigration._meta.database)
            DBMigration(name=n).save()

def fake_migrations(migration_list: List[Tuple[str, str]]) -> None:
    DBMigration.bulk_create((
        DBMigration(name=n) for n, m in migration_list 
    ))

def migration_data() -> dict[str, DBMigration]:
    if not DBMigration.table_exists():
        return {} # Creating the migrations table is, in fact, a migration
    return {m.name: m for m in DBMigration.select()}

if __name__ == "__main__":
    if len(argv) < 2:
        print("Please provide a module name")
        exit(1)
    module_name = argv[1]
    create_migration(module_name)
    # print(module)
    # print(sys.modules[__name__])
    # importlib.import_module(migrations[0])