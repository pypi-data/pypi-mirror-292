#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
"""Migration migration_20240818_231652.py

Early versions of conformer did not have migraitons and so didn't have
a migration table.

This migration adds that table :)
"""

from datetime import datetime

import peewee
from peewee import CharField, DateTimeField, Model


class DBMigration(Model): # Migration fixture
    """Allows migrations to track versions of the code"""
    class Meta:
        table_name = "migration"

    name: str = CharField(unique=True)
    applied: datetime = DateTimeField(default=datetime.now())


def migrate(project_path: str, database: peewee.Database) -> None:
    with database.bind_ctx([DBMigration]):
        database.create_tables([DBMigration])
