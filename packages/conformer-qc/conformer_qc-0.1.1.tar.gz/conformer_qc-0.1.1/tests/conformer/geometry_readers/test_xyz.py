#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase

from conformer.example_systems import open_example
from conformer.geometry_readers.xyz import XYZRead


class XYZTestCase(TestCase):
    def test_xyz(self):
        with open_example("water-6-cluster.xyz").open("r") as f:
            sys = XYZRead(f)
        self.assertListEqual(
            [a.t for a in sys],
            [
                "O",
                "H",
                "H",
                "O",
                "H",
                "H",
                "O",
                "H",
                "H",
                "O",
                "H",
                "H",
                "O",
                "H",
                "H",
                "O",
                "H",
                "H",
            ],
        )

    def test_xyz_charge(self):
        with open_example("water-6-cluster.xyz").open("r") as f:
            sys = XYZRead(f, charges={1: -1, 4: 2})
        self.assertEqual(sys[0].charge, -1)
        self.assertEqual(sys[3].charge, 2)
        self.assertEqual(sys.charge, 1)
