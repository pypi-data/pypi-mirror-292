#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from playhouse.sqlite_ext import SqliteExtDatabase

from .registry import load_app, load_models, load_stages
from .stages import DEFAULT_WORLD

TEST_CONFIG = {
    "requires": ["conformer_core"],
    "settings": {
        "DEFAULT_DB_FILENAME": ":memory:",
    },
}


class DBTestCase(unittest.TestCase):
    enable_tmpdir = False
    enable_db = False
    CONFIG = TEST_CONFIG

    def __init_subclass__(
        cls,
        enable_tmpdir=False,
        enable_db=True,
    ) -> None:
        cls.enable_tmpdir = enable_tmpdir
        cls.enable_db = enable_db

        cls._conf = load_app(cls.CONFIG)
        cls._models = load_models(cls._conf)
        cls.STAGE_REGISTRY = load_stages(cls._conf)

    def run(self, *args, **kwargs):
        # Construct the supporting structure
        DEFAULT_WORLD.clear()  # Start with fresh stages!
        try:
            if self.enable_db:
                # Bootstrap the database. No migrations
                self.db = SqliteExtDatabase(":memory:")
                self.db.bind(self._models)
                self.db.connect()
                self.db.create_tables(self._models)
            if self.enable_tmpdir:
                self.tmpdir = TemporaryDirectory()
                self.tmpdir_path = Path(self.tmpdir.name)

            return super().run(*args, **kwargs)
        finally:
            if self.enable_db:
                self.db.close()
                del self.db
            if self.enable_tmpdir:
                self.tmpdir.cleanup()
