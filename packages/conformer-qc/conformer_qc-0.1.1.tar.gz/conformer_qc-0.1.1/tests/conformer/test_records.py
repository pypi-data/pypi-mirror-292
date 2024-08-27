#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#

###################################################################
#                  Test layer built on properties                 #
###################################################################

import unittest

import numpy as np
import xarray as xa

import conformer.db.models as cdb
import conformer_core.db.models as ccdb
from conformer.records import (
    RecordStatus,
    SystemMatrixProperty,
    SystemRecord,
    empty_properties,
)
from conformer.systems import System
from conformer_core.properties.core import (
    MatrixProperty,
    Property,
    PropertySet,
    add_property,
    get_property,
    remove_property,
)
from conformer_core.stages import Stage
from tests.conformer import ConformerTestCase


class SystemMatrixTestCases(unittest.TestCase):
    def test_SystemMatrixProperty(self):
        mat_prop = SystemMatrixProperty(
            name="float_prop",
            readable_name="",
            type=np.float64,
            unit="",
            use_coef="",
            help="",
            window=(3, 3),
            extensive=(True, False),
            dim_labels=("a", "b"),
        )

        A = np.zeros((3, 3))
        np.testing.assert_allclose(A, mat_prop.validate(A), atol=1e-9)
        with self.assertRaises(AssertionError):
            mat_prop.validate(np.zeros((3, 4)))
        with self.assertRaises(AssertionError):
            mat_prop.validate(np.zeros((4, 3)))

        # Test indexing
        self.assertListEqual(mat_prop.intensive_index(3), list(range(3)))
        self.assertListEqual(mat_prop.extensive_index(3, [0, 4]), [0, 1, 2, 12, 13, 14])

        # Test xarray creation
        A_xa = mat_prop.index_data(np.zeros((9, 3)), [0, 2, 4])

        xa.testing.assert_equal(
            A_xa,
            xa.DataArray(
                np.zeros((9, 3)),
                [("a", [0, 1, 2, 6, 7, 8, 12, 13, 14]), ("b", [0, 1, 2])],
            ),
        )

        dict_data = dict(
            shape=(3, 3),
            dtype="float64",
            data=[0.0] * 9,
        )
        self.assertDictEqual(mat_prop.to_dict(A), dict_data)
        np.testing.assert_allclose(A, mat_prop.from_dict(dict_data), atol=1e-9)


class SystemRecordTestCases(unittest.TestCase):
    def setUp(self) -> None:
        add_property(
            Property(
                name="A",
                readable_name="",
                type=int,
                unit="",
                use_coef=False,
                help="",
            )
        )
        add_property(
            MatrixProperty(
                name="B",
                readable_name="",
                type=np.int64,
                unit="",
                use_coef=True,
                help="",
                window=(2, 2),
                dim_labels=("dof1", "dof2"),
            )
        )
        add_property(
            SystemMatrixProperty(
                name="C",
                readable_name="",
                type=np.int64,
                unit="",
                use_coef=True,
                help="",
                window=(2, 2),
                extensive=(True, False),
                dim_labels=("a", "b"),
            )
        )
        add_property(
            SystemMatrixProperty(
                name="2D",
                readable_name="",
                type=np.int64,
                unit="",
                use_coef=True,
                help="",
                window=(1, 2),
                extensive=(True, True),
                dim_labels=("a", "b"),
            )
        )

    def tearDown(self) -> None:
        remove_property("A")
        remove_property("B")
        remove_property("C")
        remove_property("2D")

    def test_empty_properties(self):
        p = empty_properties(
            System.from_tuples([("H", 0, 0, 0), ("H", 1, 0, 0)]),
            [get_property("A"), get_property("B"), get_property("C")],
        )
        self.assertEqual(p["A"], 0)
        np.testing.assert_equal(p["B"], np.zeros((2, 2), dtype=np.int64))
        xa.testing.assert_equal(
            p["C"],
            xa.DataArray(
                np.zeros((4, 2), dtype=np.int64),
                [("a", [0, 1, 2, 3]), ("b", [0, 1])],
            ),
        )

    def test_add_into(self):
        sys1 = System.from_tuples([("H", 0, 0, 0), ("H", 1, 0, 0)])
        rec1 = SystemRecord(
            Stage(),
            system=sys1,
            properties=PropertySet(
                dict(
                    A=1,
                    B=np.ones((2, 2), dtype=np.int64),
                    C=np.ones((4, 2), dtype=np.int64),
                )
            ),
        )

        sys2 = System.from_tuples([("H", 0, 0, 0), ("H", 2, 0, 0)])
        rec2 = SystemRecord(
            Stage(),
            system=sys2,
            properties=PropertySet(
                dict(
                    A=1,
                    B=np.ones((2, 2), dtype=np.int64),
                    C=np.ones((4, 2), dtype=np.int64),
                )
            ),
        )

        # Test add_into for rec.properties is None
        rec3 = SystemRecord(Stage(), system=sys1)
        rec3.add_into(rec2)
        p = rec3.properties
        self.assertEqual(p["A"], 1)
        np.testing.assert_equal(p["B"], np.ones((2, 2), dtype=np.int64))
        xa.testing.assert_equal(
            p["C"],
            xa.DataArray(
                np.array([[1, 1], [1, 1], [0, 0], [0, 0]], dtype=np.int64),
                [("a", [0, 1, 2, 3]), ("b", [0, 1])],
            ),
        )

        # Test addition to existing record
        rec1.add_into(rec2, coef=-1)
        p = rec1.properties
        self.assertEqual(p["A"], 2)  # Does not use coef
        np.testing.assert_equal(p["B"], np.zeros((2, 2), dtype=np.int64))
        xa.testing.assert_equal(
            p["C"],
            xa.DataArray(
                np.array([[0, 0], [0, 0], [1, 1], [1, 1]], dtype=np.int64),
                [("a", [0, 1, 2, 3]), ("b", [0, 1])],
            ),
        )

    def test_swap(self):
        sys1 = System.from_tuples(
            [
                ("H", 2, 0, 0),
                ("H", 1, 0, 0),
                ("H", 0, 0, 0),
            ]
        )
        sys2 = sys1.canonize()

        M_sys1 = np.array(
            [
                [22, 22, 21, 21, 20, 20],
                [12, 12, 11, 11, 10, 10],
                [2, 2, 1, 1, 0, 0],
            ]
        )

        M_sys2 = np.array(
            [
                [0, 0, 1, 1, 2, 2],
                [10, 10, 11, 11, 12, 12],
                [20, 20, 21, 21, 22, 22],
            ]
        )

        sys2_record = SystemRecord(
            Stage(), system=sys2, properties=PropertySet({"2D": M_sys2})
        )

        sys1_record = sys2_record.swap_system(sys1)
        np.testing.assert_equal(M_sys1, sys1_record.properties["2D"])
        np.testing.assert_equal(M_sys2, sys2_record.properties["2D"])


class DBSystemRecordTestCases(ConformerTestCase):
    def test_system_records(self):
        """Test SystemRecords in the DB"""
        stage = Stage()  # Create anonymous stage

        # Save a system to this record
        sys1 = System.from_tuples([("O", 0, 0, 0)])
        rec1 = SystemRecord(stage, system=sys1)

        cdb.DBSystemRecord.add_or_update_system_record([rec1])

        db_rec1 = cdb.DBSystemRecord.get_system_records(stage, [sys1])[sys1]
        self.assertEqual(rec1._saved, 1)
        self.assertEqual(rec1._saved, db_rec1._saved)

        self.assertEqual(ccdb.DBRecord.select().count(), 1)
        self.assertEqual(ccdb.DBStage.select().count(), 1)
        self.assertEqual(cdb.DBSystem.select().count(), 1)
        self.assertEqual(cdb.DBSystemRecord.select().count(), 1)

        self.assertEqual(cdb.DBRecord.select().first().status, RecordStatus.PENDING)

        rec1.system = sys1.copy()
        rec1.status = RecordStatus.RUNNING
        cdb.DBSystemRecord.add_or_update_system_record([rec1])

        # Should have been an update
        self.assertEqual(ccdb.DBRecord.select().count(), 1)
        self.assertEqual(ccdb.DBStage.select().count(), 1)
        self.assertEqual(cdb.DBSystem.select().count(), 1)
        self.assertEqual(cdb.DBSystemRecord.select().count(), 1)

        # Check that the DBIDs get updated properly
        # Create another record...
        rec2 = SystemRecord(Stage(), system=sys1.copy())
        cdb.DBSystemRecord.add_or_update_system_record([rec2])

        # Create copies
        rec1_copy = SystemRecord(stage, system=sys1.copy())
        rec2_copy = SystemRecord(rec2.stage, system=sys1.copy())

        cdb.DBSystemRecord.get_record_DBID([rec1_copy, rec2_copy])
        self.assertEqual(rec1_copy._saved, 1)
        self.assertEqual(rec1_copy.id, rec1.id)
        self.assertEqual(rec1_copy.system._saved, 1)

        self.assertEqual(rec2_copy._saved, 2)
        self.assertEqual(rec2_copy.id, rec2.id)
        self.assertEqual(rec2_copy.system._saved, 1)

        # Double check that we haven't changed the status with DBID update
        self.assertEqual(ccdb.DBRecord.select().first().status, RecordStatus.RUNNING)

        # Test get or create
        sys2 = System.from_tuples([("H", 0, 0, 0)])
        records = cdb.DBSystemRecord.get_or_create_system_records(stage, [sys1, sys2])

        self.assertEqual(
            cdb.DBRecord.select().where(cdb.DBRecord.stage_id == stage._saved).count(),
            2,
        )
        self.assertEqual(records[sys1]._saved, 1)
        self.assertEqual(records[sys2]._saved, 3)

        uuid_lookup = cdb.DBSystemRecord.get_record_by_uuid(
            [str(rec1.id)[0:5]], {}, {"Stage": Stage}
        )
        self.assertDictEqual(uuid_lookup, {str(rec1.id): rec1})
