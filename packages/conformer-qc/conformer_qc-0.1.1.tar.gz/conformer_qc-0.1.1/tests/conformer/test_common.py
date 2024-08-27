#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase

from conformer.common import (
    GHOST_ATOM,
    PHYSICAL_ATOM,
    AtomRole,
    Mask,
    int_to_role,
    role_to_int,
)
from conformer.common import (
    AtomMask as AM,
)
from conformer.common import (
    CellIndex as CI,
)


class CommonTestCases(TestCase):
    def test_AtomRole(self):
        r1 = AtomRole(is_physical=True)
        self.assertEqual(role_to_int(r1), 1)
        self.assertEqual(int_to_role(1), r1)

        r2 = AtomRole(has_basis_fns=True)
        self.assertEqual(role_to_int(r2), 2)
        self.assertEqual(int_to_role(2), r2)

        r3 = AtomRole(is_point_charge=True)
        self.assertEqual(role_to_int(r3), 4)
        self.assertEqual(int_to_role(4), r3)

        r4 = AtomRole(is_proxy=True)
        self.assertEqual(role_to_int(r4), 8)
        self.assertEqual(int_to_role(8), r4)

        self.assertListEqual(sorted([r2, r1, r4, r3]), [r4, r3, r2, r1])

    def test_AM(self):
        a1 = AM(0, PHYSICAL_ATOM)
        a2 = AM(1, PHYSICAL_ATOM)
        a3 = AM(0, GHOST_ATOM)

        self.assertEqual(a1.str_digest(), "0")
        self.assertEqual(AM.from_str("0"), a1)

        self.assertEqual(a2.str_digest(), "1")

        self.assertEqual(a3.str_digest(), "0/G")
        self.assertEqual(AM.from_str("0/G"), a3)

        self.assertEqual(AM(1, None).str_digest(), "1/~")
        self.assertEqual(
            AM(
                0, AtomRole(is_physical=True, is_proxy=True, is_point_charge=True)
            ).str_digest(),
            "0/13",
        )

        self.assertListEqual(sorted([a2, a1, a3]), [a3, a1, a2])

    def test_CI(self):
        c1 = CI((0, 0, 0))
        self.assertEqual(c1 + 1, CI((1, 1, 1)))
        self.assertEqual(1 + c1, CI((1, 1, 1)))
        self.assertEqual(c1 + [1, 2, 3], CI((1, 2, 3)))

        self.assertEqual(c1 - 1, CI((-1, -1, -1)))
        self.assertEqual(1 - c1, CI((1, 1, 1)))
        self.assertEqual(c1 - [1, 2, 3], CI((-1, -2, -3)))

        self.assertEqual(c1.str_digest(), "(0,0,0)")
        self.assertEqual(CI.from_str("(0,0,0)"), c1)

        # Multiplication is not implemented
        # NOTE: There is a commented implementation of __mul__ which works as expected
        #       for the `c1 * n` case; however `n * c1 returns a n *3 int long tuple`
        #       and this cannot be changed with `__rmul__`
        # Division is not implemented

    def test_masks(self):
        MASK_STR = "(0,0,0):0,1;(0,1,0):0/G;(1,0,0):0"
        m1 = Mask(
            {
                CI((-1, -1, -1)): frozenset(
                    {AM(0, PHYSICAL_ATOM), AM(1, PHYSICAL_ATOM)}
                ),
                CI((-1, 0, -1)): frozenset({AM(0, GHOST_ATOM)}),
                CI((0, -1, -1)): frozenset({AM(0, PHYSICAL_ATOM)}),
            },
            minimize=True,
        )

        self.assertListEqual(m1.sorted_indexs(), [(0, 0, 0), (0, 1, 0), (1, 0, 0)])

        self.assertEqual(m1.str_digest(), MASK_STR)
        self.assertEqual(m1, Mask.from_str(MASK_STR))

    def test_mask_intersections(self):
        # TEST DISPLACEMENT CODE
        # m1: #     m2: #     m3:     m4:
        #     ##         #        ##      #

        ALL_ELEMENTS = frozenset({AM(0), AM(1), AM(2)})
        m1 = Mask(
            {
                CI((0, 0, 0)): frozenset({AM(0)}),
                CI((0, 1, 0)): frozenset({AM(1)}),
                CI((1, 0, 0)): frozenset({AM(2)}),
            }
        )
        m2 = Mask({CI((0, 1, 0)): ALL_ELEMENTS, CI((1, 0, 0)): ALL_ELEMENTS})
        m3 = Mask({CI((0, 0, 0)): ALL_ELEMENTS, CI((1, 0, 0)): ALL_ELEMENTS})
        m4 = Mask({CI((0, 0, 0)): ALL_ELEMENTS})

        # TEST EQUALITY AND HASHING
        mask_sets = {m1, m2, m3, m4}
        self.assertTrue(
            Mask(  # Shuffle order
                {
                    CI((1, 0, 0)): frozenset({AM(2)}),
                    CI((0, 1, 0)): frozenset({AM(1)}),
                    CI((0, 0, 0)): frozenset({AM(0)}),
                },
            )
            in mask_sets
        )
        self.assertTrue(
            Mask(
                {
                    CI((1, 0, 0)): ALL_ELEMENTS,
                    CI((0, 1, 0)): ALL_ELEMENTS,
                },
            )
            in mask_sets
        )
        self.assertFalse(
            Mask(
                {
                    CI((1, 0, 0)): frozenset({AM(2)}),
                },
            )
            in mask_sets
        )

        # TEST INTERSECTIONS
        self.assertSetEqual(
            {(0, 1, 0), (0, 0, 0), (1, 0, 0), (-1, 1, 0), (1, -1, 0)},
            m1.get_displacements(m2),
        )

        self.assertEqual(
            set(m1.intersections(m2)),
            {
                Mask(
                    {
                        CI((0, 1, 0)): frozenset({AM(1)}),
                        CI((1, 0, 0)): frozenset({AM(2)}),
                    }
                ),
                Mask({CI((0, 0, 0)): frozenset({AM(0)})}),
                Mask({CI((0, 0, 0)): frozenset({AM(1)})}),
                Mask({CI((0, 0, 0)): frozenset({AM(2)})}),
            },
        )
        self.assertSetEqual(set(m1.intersections(m2)), set(m2.intersections(m1)))

        # Test second intersection
        int2 = set(m1.intersections(m3))
        self.assertEqual(
            int2,
            {
                Mask(
                    {
                        CI((0, 0, 0)): frozenset({AM(0)}),
                        CI((1, 0, 0)): frozenset({AM(2)}),
                    }
                ),
                Mask({CI((0, 0, 0)): frozenset({AM(0)})}),
                Mask({CI((0, 0, 0)): frozenset({AM(1)})}),
                Mask({CI((0, 0, 0)): frozenset({AM(2)})}),
            },
        )
        self.assertSetEqual(set(m1.intersections(m3)), set(m3.intersections(m1)))

        # Test third intersection
        int3 = set(m1.intersections(m4))
        self.assertEqual(
            int3,
            {
                Mask({CI((0, 0, 0)): frozenset({AM(0)})}),
                Mask({CI((0, 0, 0)): frozenset({AM(1)})}),
                Mask({CI((0, 0, 0)): frozenset({AM(2)})}),
            },
        )

    def test_mask_issubset(self):
        m1 = Mask(
            {
                CI((0, 0, 0)): frozenset({AM(0)}),
                CI((0, 1, 0)): frozenset({AM(1)}),
                CI((1, 0, 0)): frozenset({AM(2)}),
            }
        )
        self.assertTrue(m1.issubset(m1))

        m2 = Mask(
            {
                CI((0, 0, 2)): frozenset({AM(0)}),
                CI((0, 1, 2)): frozenset({AM(1)}),
            },
            minimize=False,
        )
        self.assertTrue(m2.issubset(m1))
        self.assertFalse(m1.issubset(m2))

        m3 = Mask(
            {
                CI((0, 0, 2)): frozenset({AM(0)}),
                CI((0, 1, 2)): frozenset({AM(0)}),
            },
            minimize=False,
        )
        self.assertFalse(m3.issubset(m1))

    def test_mask_issuperset(self):
        m1 = Mask(
            {
                CI((0, 0, 0)): frozenset({AM(0)}),
                CI((0, 1, 0)): frozenset({AM(1)}),
                CI((1, 0, 0)): frozenset({AM(2)}),
            }
        )
        self.assertTrue(m1.issuperset(m1))

        m2 = Mask(
            {
                CI((0, 0, 2)): frozenset({AM(0)}),
                CI((0, 1, 2)): frozenset({AM(1)}),
            },
            minimize=False,
        )
        self.assertTrue(m1.issuperset(m2))
        self.assertFalse(m2.issuperset(m1))

        m3 = Mask(
            {
                CI((0, 0, 2)): frozenset({AM(0)}),
                CI((0, 1, 2)): frozenset({AM(0)}),
            },
            minimize=False,
        )
        self.assertFalse(m1.issuperset(m3))

        m4 = Mask(
            {
                CI((0, -1, 2)): frozenset({AM(0)}),
                CI((0, 1, 2)): frozenset({AM(0)}),
            },
            minimize=False,
        )
        self.assertFalse(m1.issuperset(m4))
