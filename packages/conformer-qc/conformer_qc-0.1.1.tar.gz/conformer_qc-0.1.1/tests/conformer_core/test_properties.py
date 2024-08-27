#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import unittest
from io import StringIO, TextIOWrapper
from typing import Match

import numpy as np

from conformer_core.properties.core import (
    MASTER_PROP_LIST,
    MatrixProperty,
    Property,
    PropertySet,
    add_property,
    get_property,
    remove_property,
)
from conformer_core.properties.extraction import (
    Extractor,
    PropertyExtractorMixin,
    SharedStreamDataSource,
    calc_property,
)


class PropertiesTestCases(unittest.TestCase):
    def test_add_property(self):
        prop = Property(
            name="test",
            readable_name="Test",
            type=int,
            unit="",
            use_coef="false",
            help="There is no help here",
        )
        add_property(prop)
        with self.assertRaises(ValueError):
            add_property(prop)

        self.assertIn(prop.name, MASTER_PROP_LIST)
        self.assertIs(prop, get_property(prop))
        self.assertIs(prop, get_property("test"))

        remove_property(prop)
        self.assertNotIn(prop, MASTER_PROP_LIST)

    def test_Property(self):
        float_prop = Property(
            name="float_prop",
            readable_name="",
            type=float,
            unit="",
            use_coef="",
            help="",
        )
        self.assertEqual(1.0, float_prop.validate(1.0))
        with self.assertRaises(AssertionError):
            float_prop.validate(1)
        self.assertEqual(float_prop.to_dict(1.0), 1.0)
        self.assertEqual(float_prop.from_dict(1.0), 1.0)

        int_prop = Property(
            name="float_prop", readable_name="", type=int, unit="", use_coef="", help=""
        )
        self.assertEqual(1, int_prop.validate(1))
        with self.assertRaises(AssertionError):
            int_prop.validate(1.0)
        self.assertEqual(int_prop.to_dict(1), 1)
        self.assertEqual(int_prop.from_dict(1), 1)

    def test_PropertyMatrix(self):
        mat_prop = MatrixProperty(
            name="float_prop",
            readable_name="",
            type=np.float64,
            unit="",
            use_coef="",
            help="",
            window=(3, 3),
            dim_labels=("a", "b"),
        )

        A = np.zeros((3, 3))
        np.testing.assert_allclose(A, mat_prop.validate(A), atol=1e-9)

        with self.assertRaises(AssertionError):
            mat_prop.validate(np.zeros((3, 4)))

        dict_data = dict(
            shape=(3, 3),
            dtype="float64",
            data=[0.0] * 9,
        )
        self.assertDictEqual(mat_prop.to_dict(A), dict_data)
        np.testing.assert_allclose(A, mat_prop.from_dict(dict_data), atol=1e-9)


class PropertySetTestCases(unittest.TestCase):
    def setUp(self) -> None:
        add_property(
            Property(
                name="float_prop",
                readable_name="",
                type=float,
                unit="",
                use_coef="",
                help="",
            )
        )
        add_property(
            Property(
                name="int_prop",
                readable_name="",
                type=int,
                unit="",
                use_coef="",
                help="",
            )
        )

    def tearDown(self) -> None:
        remove_property("float_prop")
        remove_property("int_prop")

    def test_construct(self):
        p = PropertySet({"float_prop": 1.0})
        self.assertSetEqual(p.props, {get_property("float_prop")})
        self.assertDictEqual(p.values, {get_property("float_prop"): 1.0})

        p["int_prop"] = 1
        self.assertEqual(p["int_prop"], 1)
        self.assertSetEqual(
            p.props, {get_property("float_prop"), get_property("int_prop")}
        )
        self.assertDictEqual(
            p.values, {get_property("float_prop"): 1.0, get_property("int_prop"): 1}
        )

        # Add an invalid value
        with self.assertRaises(AssertionError):
            PropertySet({"float_prop": 1})

        # Use an invalid property
        with self.assertRaises(KeyError):
            PropertySet({"bad_prop": 1})

        # Test writing to a dict
        dict_data = {"float_prop": 1.0, "int_prop": 1}
        self.assertDictEqual(p.to_dict(), dict_data)

        # Test reading from dict
        p = PropertySet.from_dict(dict_data)
        self.assertSetEqual(
            p.props, {get_property("float_prop"), get_property("int_prop")}
        )
        self.assertDictEqual(
            p.values, {get_property("float_prop"): 1.0, get_property("int_prop"): 1}
        )


class PropertyExtractionTest(unittest.TestCase):
    def setUp(self) -> None:
        add_property(
            Property(
                name="coef_prop",
                type=float,
                use_coef=True,
                help="Coef dependent property",
                unit="f",
                readable_name="Coef Prop",
            )
        )
        add_property(
            Property(
                name="no_coef_prop",
                type=float,
                use_coef=False,
                help="Coef independent property",
                unit="f",
                readable_name="Non-Coef Prop",
            )
        )

    def tearDown(self) -> None:
        remove_property("coef_prop")
        remove_property("no_coef_prop")

    def test_construct(self):
        class PropertiedClass(PropertyExtractorMixin):
            @calc_property(prop_name="no_coef_prop")
            def prop_tttime(self, ctx) -> float:
                """Docs"""
                return 1.0

            @calc_property()
            def prop_coef_prop(self, ctx):
                return 1.0

        prop = PropertiedClass()

        self.assertIsInstance(prop.prop_tttime, Extractor)
        self.assertEqual(prop.prop_tttime.property_name, "no_coef_prop")

        self.assertDictEqual(
            prop.get_properties(None, []).to_dict(),
            {"no_coef_prop": 1.0, "coef_prop": 1.0},
        )

    def test_available_props(self):
        class PropertiedClass(PropertyExtractorMixin):
            @calc_property(source="file")
            def prop_no_coef_prop(self, ctx, line, file):
                return 1

            @calc_property(source="regex", patterns=[r"blah"])
            def prop_coef_prop(self, ctx, match):
                return 1

        prop = PropertiedClass()
        self.assertSetEqual(prop.available_properties(), {"no_coef_prop", "coef_prop"})
        self.assertIsInstance(prop._data_providers[0], SharedStreamDataSource)
        self.assertListEqual(
            prop._data_providers[0].extractors,
            [prop.prop_coef_prop, prop.prop_no_coef_prop],
        )

    def test_file_source(self):
        class PropertiedClass(PropertyExtractorMixin):
            def __init__(self) -> None:
                super().__init__()
                self.coef_prop_ctr = 0.0
                self.no_coef_prop_ctr = 0.0

            @calc_property(source="file")
            def prop_coef_prop(self, ctx, line, file_handle: TextIOWrapper):
                self.coef_prop_ctr += 1.0
                assert len(line) != 0

            @calc_property(source="file")
            def prop_no_coef_prop(self, ctx, line, file_handle: TextIOWrapper):
                self.no_coef_prop_ctr += 1
                assert len(line) != 0
                if self.no_coef_prop_ctr == 5.0:
                    return 5.0

        prop = PropertiedClass()
        prop_vals = prop.get_properties(None, [StringIO("Not blank\n" * 23)])
        self.assertDictEqual(prop_vals.to_dict(), {"no_coef_prop": 5.0})
        self.assertEqual(prop.no_coef_prop_ctr, 5.0)
        self.assertEqual(prop.coef_prop_ctr, 23.0)

    def test_re_source(self):
        class PropertiedClass(PropertyExtractorMixin):
            def __init__(self) -> None:
                super().__init__()
                self.call_counter = 0
                self.matches = []

            @calc_property(
                source="regex", patterns=[r"\W+method:\W+(\w+)", r"\W+name:\W+(\w+)"]
            )
            def prop_no_coef_prop(self, ctx, match: Match, _):
                self.matches.append(match[1])
                self.call_counter += 1

        prop = PropertiedClass()
        _ = prop.get_properties(
            None,
            [
                StringIO(
                    """
            method: PDB
            method: Dummy 
            method: PDB
            name: RCaps
            method: Dummy
        """
                )
            ],
        )
        self.assertEqual(prop.call_counter, 5)
        self.assertListEqual(prop.matches, ["PDB", "Dummy", "PDB", "RCaps", "Dummy"])
