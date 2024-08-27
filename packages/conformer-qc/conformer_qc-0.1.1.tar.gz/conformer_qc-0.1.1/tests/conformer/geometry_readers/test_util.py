#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from importlib.resources import as_file, files
from io import StringIO
from unittest import TestCase

from conformer.common import GHOST_ATOM
from conformer.example_systems import read_example
from conformer.geometry_readers.util import UnsupportedFileType, read_geometry


class TestUtil(TestCase):
    def test_read_geometry(self):
        descriptor = files("conformer.example_systems").joinpath("water-6-cluster.xyz")

        with self.assertRaises(ValueError):
            read_geometry("As Text", descriptor.read_text())
        with self.assertRaises(UnsupportedFileType):
            read_geometry("As Text", descriptor.read_text(), ext=".abc")

        as_text = read_geometry("As Text", descriptor.read_text(), ext=".xyz")
        as_stream = read_geometry(
            "As Stream", StringIO(descriptor.read_text()), ext=".xyz"
        )
        with as_file(descriptor) as P:
            with P.open("r") as f:
                as_fileIO = read_geometry("As FileIO", f, ext=".xyz")
            as_path = read_geometry("As Path", P, ext=".xyz")

        self.assertDictEqual(
            as_text.meta,
            {
                "comment": "TIP4 water fragment",
                "hash": "3ab060b4c040288a585783ff8aa90937cea3cc27",
                "order": [4, 10, 5, 9, 6, 11, 16, 12, 17, 7, 8, 3, 1, 2, 0, 14, 15, 13],
            },
        )

        self.assertEqual(as_text, as_stream)
        self.assertEqual(as_text, as_fileIO)
        self.assertEqual(as_text, as_path)

    def test_custom_roles(self):
        """Tests role overrides for reading systems"""
        source = files("conformer.example_systems").joinpath("water-6-cluster.xyz")
        sys = read_geometry(
            "RoleTest",
            source.read_text(),
            ext=".xyz",
            roles={
                1: "GHOST",  # Test with string
                2: 2,  # Test with ints
                3: GHOST_ATOM,  # Test role
                4: {"has_basis_fns": True},  # Test dict
            },
        )

        # First four atoms are ghost atoms:
        self.assertEqual(sys.fingerprint, "8ff774b2390a43cc7ff5c716512a0939fbac3fea")

    def test_read_example(self):
        """Test that we can easily open example file"""
        sys = read_example("water-6-cluster.xyz")
        self.assertDictEqual(
            sys.meta,
            {
                "comment": "TIP4 water fragment",
                "hash": "3ab060b4c040288a585783ff8aa90937cea3cc27",
                "order": [4, 10, 5, 9, 6, 11, 16, 12, 17, 7, 8, 3, 1, 2, 0, 14, 15, 13],
            },
        )
