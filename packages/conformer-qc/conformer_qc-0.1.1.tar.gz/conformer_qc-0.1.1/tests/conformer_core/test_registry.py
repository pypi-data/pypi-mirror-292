#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import unittest

from conformer_core.db.models import (
    DBCalculationRecord,
    DBMigration,
    DBRecord,
    DBStage,
    DBStageLink,
)
from conformer_core.registry import Config, load_app, load_models

REGISTRY_FIXTURE = {
    "database": {
        "provides": {
            "conformer_core.db.models.DBCalculationRecord",
            "conformer_core.db.models.DBMigration",
            "conformer_core.db.models.DBRecord",
            "conformer_core.db.models.DBStage",
            "conformer_core.db.models.DBStageLink",
        }
    },
    "environment_vars": {},
    "requires": ["conformer_core"],
    "settings": {"DB_NAME": ":memory:", "TEST_SETTING": 1},
    "stages": {"provides": set()},
}


class RegistryTestCases(unittest.TestCase):
    def test_load_app(self):
        self.maxDiff = None
        base_config = Config(
            requires=["conformer_core"],
            settings={"DB_NAME": ":memory:", "TEST_SETTING": 1},
        )

        self.assertDictEqual(load_app(base_config).model_dump(), REGISTRY_FIXTURE)

        del base_config.settings["DB_NAME"]
        self.assertEqual(load_app(base_config).settings["DB_NAME"], ":memory:")

    def test_get_models(self):
        base_config = Config(
            requires=["conformer_core"],
            settings={"DB_NAME": ":memory:", "TEST_SETTING": 1},
        )

        config = load_app(base_config)
        models = load_models(config)
        self.assertSetEqual(
            set(models),
            {
                DBMigration,
                DBStage,
                DBStageLink,
                DBRecord,
                DBCalculationRecord,
            },
        )
