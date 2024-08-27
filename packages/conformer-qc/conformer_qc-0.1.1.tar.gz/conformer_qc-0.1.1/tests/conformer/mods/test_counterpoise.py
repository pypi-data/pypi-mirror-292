#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase

from conformer.mods.counterpoise import CounterpoiseSubsystemMod
from conformer.systems import System


class CounterpoiseTestCases(TestCase):
    def test_constructors(self):
        s = System.from_tuples(
            [
                ("H", 0, 0, 0),
                ("H", 0, 1, 0),
                ("H", 1, 0, 0),
                ("H", 1, 1, 0),
            ]
        )

        cp_ssm = CounterpoiseSubsystemMod()
        ss = s.subsystem([0], mods=[cp_ssm])
        # print(ss.summarize())

        # Verified that to add other atoms as Ghost atoms
        self.assertEqual(s.fingerprint, "b27570456fe8a6f255b3218a95388ecca652a992")
        self.assertEqual(ss.fingerprint, "0231733aa21bcf41e92a0fb2696372a4cbb8f5d6")
