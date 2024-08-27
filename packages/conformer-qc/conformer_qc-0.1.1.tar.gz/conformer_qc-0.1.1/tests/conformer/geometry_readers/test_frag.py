#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase

from conformer.example_systems import open_example
from conformer.geometry_readers.frag import FragRead


class FragTestCase(TestCase):
    def test_frag(self):
        with open_example("water-6-cluster.frag").open("r") as f:
            sys = FragRead(f, charges={4: -1})
        self.assertListEqual(
            [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 6],
            [a.meta["frag_group"] for a in sys],
        )
        self.assertEqual(sys[3].charge, -1)
