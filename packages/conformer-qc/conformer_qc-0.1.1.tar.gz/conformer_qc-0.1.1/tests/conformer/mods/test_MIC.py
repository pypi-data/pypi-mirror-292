#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase

import numpy as np
from numpy.testing import assert_allclose

from conformer.mods.MIC import MIC_wrap, MICSystemMod, mk_group_mask, valid_MIC_system
from conformer.systems import System


class MICTestCases(TestCase):
    def test_wrapping(self):
        sys1 = System.from_tuples(
            [
                ("H", 0, 0, 0),
                ("H", 12, 0, 0),
                ("H", 6, 0, 0),
                ("H", -102, 0, 0),
            ],
            unit_cell=np.array([10, 10, 10]),
        )

        mask = mk_group_mask(sys1)
        assert_allclose(mask, np.array([0, 1, 2, 3]))

        # Just re-wrap to box
        MIC_sys = MIC_wrap(
            sys1,
            wrap_point=np.array([5, 5, 5]),  # Center of box
            group_mask=mask + 1,  # Check that masks don't have to be 0-(n-1)
        )

        assert_allclose(
            MIC_sys.r_matrix,
            np.array(
                [
                    [0.0, 0.0, 0.0],
                    [2.0, 0.0, 0.0],
                    [6.0, 0.0, 0.0],
                    [8.0, 0.0, 0.0],
                ]
            ),
        )

        # Shift "up" by one
        MIC_sys = MIC_wrap(
            sys1,
            wrap_point=np.array([0, 0, 0]),  # Center on first atom in box
            group_mask=mask + 1,  # Check that masks don't have to be 0-(n-1)
        )

        assert_allclose(
            MIC_sys.r_matrix,
            np.array(
                [
                    [0.0, 0.0, 0.0],
                    [2.0, 0.0, 0.0],
                    [-4.0, 0.0, 0.0],
                    [-2.0, 0.0, 0.0],
                ]
            ),
        )

        # The wrapped system is too large!
        self.assertFalse(valid_MIC_system(MIC_sys))

        # So is this sub-fragment
        self.assertFalse(valid_MIC_system(sys1.subsystem([0, 1])))

        # Wrapping fixes this
        MW_mod = MICSystemMod()
        s = sys1.subsystem([0, 1], mods=[MW_mod])
        self.assertTrue(valid_MIC_system(s))

    def test_water(self):
        sys = System.from_tuples(
            [
                ("O", 0.361350, -0.397723, -2.340271),
                ("H", 0.123150, -0.452038, -1.394536),
                ("H", 0.045991, -1.117767, -2.846918),
                ("O", -0.553798, -0.010255, 0.372001),
                ("H", -0.709174, 0.543433, 1.110045),
                ("H", 0.050791, -0.728905, 0.553003),
            ],
            unit_cell=[12.437847] * 3,
        )
        mask = mk_group_mask(sys)
        assert_allclose(mask, [0, 0, 0, 1, 1, 1])
        s = MIC_wrap(sys, group_mask=mask)
        self.assertEqual(s.fingerprint, "2e7979cc0ba84406d25b2c652ed8edf8fd82499f")
