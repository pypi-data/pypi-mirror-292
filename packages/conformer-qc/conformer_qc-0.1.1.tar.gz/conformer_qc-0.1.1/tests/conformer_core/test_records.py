#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from datetime import datetime
from textwrap import dedent
from uuid import UUID

from conformer_core.db.models import DBRecord
from conformer_core.properties.core import (
    Property,
    PropertySet,
    add_property,
    remove_property,
)
from conformer_core.records import Record, RecordStatus
from conformer_core.stages import Stage
from tests.conformer_core import ConformerCoreTestCase


class RecordTestCases(ConformerCoreTestCase):
    def setUp(self) -> None:
        add_property(
            Property(
                name="test",
                type=int,
                use_coef=False,
                help="TestProperty",
                unit="ints",
                readable_name="Test Property",
            )
        )
        add_property(
            Property(
                name="test_float",
                type=float,
                use_coef=False,
                help="TestProperty",
                unit="floats",
                readable_name="Test Float Property",
            )
        )
        return super().setUp()

    def tearDown(self) -> None:
        remove_property("test")
        remove_property("test_float")
        return super().tearDown()

    def test_record(self):
        rec = Record(stage=Stage())

        self.assertDictEqual(rec.meta, {})
        self.assertEqual(rec.properties, None)
        self.assertEqual(rec.status, RecordStatus.PENDING)

    def test_print(self):
        rec = Record(
            stage=Stage(name="Stage Name"),
            properties=PropertySet.from_dict({"test": 1, "test_float": -1.0}),
            id=UUID(int=0),
            start_time=datetime(2020, 1, 1),
        )

        fixture = dedent(
            """\
        Record 00000000-0000-0000-0000-000000000000: 
          Stage: Stage Name
          Status: PENDING
          Created: 2020-01-01T00:00
          Properties:
            Test Property      :  1 ints
            Test Float Property: -1.000000 floats
        """
        )
        self.assertEqual(fixture, rec.summarize())

    def test_db_props_and_meta(self):
        rec = Record(stage=Stage())
        DBRecord.add_or_update_records([rec])
        db_rec = DBRecord.get_records([rec._saved], {}, {"Stage": Stage})[rec._saved]
        self.assertEqual(rec, db_rec)

    def test_from_db(self):
        stage = Stage()

        # Test record with properties and metadata
        record = Record(
            stage=stage,
            properties=PropertySet.from_dict({"test": 1}),
            meta={"note": "some metadata"},
        )

        DBRecord.add_or_update_records([record])
        self.assertNotEqual(record._saved, 0)

        saved_record = DBRecord.get_records([record._saved], {}, {"Stage": Stage})[
            record._saved
        ]
        db_id = record._saved
        self.assertEqual(db_id, 1)
        self.assertEqual(record.id, saved_record.id)
        self.assertEqual(record.status, saved_record.status)
        self.assertEqual(record.properties.values, saved_record.properties.values)
        self.assertIsInstance(saved_record.status, RecordStatus)

        # Update the record and retrieve it
        record.status = RecordStatus.COMPLETED
        DBRecord.add_or_update_records([record])
        saved_record = DBRecord.get_records([record._saved], {}, {"Stage": Stage})[
            record._saved
        ]
        self.assertEqual(db_id, saved_record._saved)
        self.assertEqual(RecordStatus.COMPLETED, saved_record.status)
