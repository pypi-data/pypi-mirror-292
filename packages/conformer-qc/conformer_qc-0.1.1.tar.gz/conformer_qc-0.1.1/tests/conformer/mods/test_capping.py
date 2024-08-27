#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import unittest
from itertools import chain

from conformer.common import CAPPING_ATOM
from conformer.example_systems import read_example
from conformer.mods.capping import HCapsMod
from conformer.spatial import distance
from conformer.systems import Atom, BoundAtom, System


class HydrogenCapperTestCases(unittest.TestCase):
    def setUp(self) -> None:
        self.capper = HCapsMod()

    def test_synthetic(self):
        """Synthetic test containing carbon, oxygen, and nitrogen,
        and hydrogen
        """
        sys1 = System(
            [
                Atom("C", [0, 0, 0]),
                Atom("C", [1.5, 0, 0]),  # Single bond
                Atom("C", [-1.3, 0, 0]),  # Double bond (which does not make sense)
                Atom("N", [0, 1.37, 0]),  # Single CN Bond
                Atom("N", [0, -1.07, 0]),  # Single CH Bond
            ]
        )

        sys2 = sys1.subsystem([0], mods=[self.capper])
        capped_atoms = [a for a in sys2 if a.is_proxy]
        capped_atoms.sort()

        self.assertListEqual(
            [distance(sys1[0], a) for a in capped_atoms],
            [1.07, 1.02, 1.02, 1.07],
        )

    def test_ignore_charged(self):
        """Test of charged systems that should NOT be capped"""
        ic_capper = HCapsMod.from_options(ignore_charged=True)
        charged_sys = System(
            [
                Atom("O", [0, 0, 0], charge=-1),
                Atom("H", [1.0, 0, 0]),
            ]
        )

        # Check that O was not capped
        self.assertEqual(
            charged_sys.subsystem([0], mods=[ic_capper]),
            System([Atom("O", [0, 0, 0], charge=-1)]),
        )

        # Check that H was capped
        self.assertEqual(
            charged_sys.subsystem([1], mods=[ic_capper]),
            System([Atom("H", [1.0, 0, 0])]),
        )

        # OH radical test
        neutral_sys = System(
            [
                Atom("O", [0, 0, 0]),
                Atom("H", [1.0, 0, 0]),
            ]
        )

        # Check that O was capped
        self.assertEqual(
            neutral_sys.subsystem([0], mods=[ic_capper]),
            System(
                [
                    Atom("O", [0, 0, 0]),
                    BoundAtom(Atom("H", [0.62, 0, 0]), role=CAPPING_ATOM),
                ]
            ),
        )

        # Check that H was capped
        self.assertEqual(
            neutral_sys.subsystem([1], mods=[ic_capper]),
            System(
                [
                    Atom("H", [1.0, 0, 0]),
                    BoundAtom(Atom("H", [0.03, 0, 0]), role=CAPPING_ATOM),
                ]
            ),
        )

    def test_metal_center(self):
        """Metal coordination test, should not cap between fragments"""

        metal_center = System([Atom("Mg", [0, 0, 0], charge=2)])

        oh_group1 = System(
            [
                Atom("O", [-1.8, 0, 0.3], charge=-1),
                Atom("H", [-2.6, 0, 0.2]),
            ]
        )

        oh_group2 = System(
            [
                Atom("O", [1.8, 0, -0.3], charge=-1),
                Atom("H", [2.6, 0, 0.2]),
            ]
        )

        super_sys = System(chain(metal_center, oh_group1, oh_group2))

        # Assert that the atom list has NOT been changed
        self.assertEqual(super_sys.subsystem([0]).size, 1)
        self.assertEqual(super_sys.subsystem([1, 2]).size, 2)
        self.assertEqual(super_sys.subsystem([3, 4]).size, 2)

    def test_ethanol(self):
        sys = read_example("ethanol.xyz")

        # Test capping the terminal CH3
        CH3 = sys.subsystem([0, 3, 4, 5], mods=[self.capper])
        self.assertEqual(CH3.size, 5)  # one cap
        self.assertEqual(CH3[4].role, CAPPING_ATOM)
        self.assertAlmostEqual(distance(CH3[1], CH3[4]), 1.07)

        # Test capping the intermediate CH2
        CH2 = sys.subsystem([1, 6, 7], mods=[self.capper])
        self.assertEqual(CH2.size, 5)  # two caps
        self.assertEqual(CH2[3].role, CAPPING_ATOM)
        self.assertEqual(CH2[4].role, CAPPING_ATOM)
        self.assertAlmostEqual(distance(CH2[1], CH2[3]), 1.07)
        self.assertAlmostEqual(distance(CH2[1], CH2[4]), 0.97)

        # Terminal OH group. Let's turn this to water
        OH = sys.subsystem([2, 8], mods=[self.capper])
        self.assertEqual(OH.size, 3)  # one cap
        self.assertEqual(OH[2].role, CAPPING_ATOM)
        self.assertAlmostEqual(distance(OH[0], OH[2]), 1.07)

    def test_formaldehyde(self):
        sys = read_example("formaldehyde.xyz")

        O = sys.subsystem([0], mods=[self.capper])  # O
        self.assertEqual(O[1].role, CAPPING_ATOM)
        self.assertAlmostEqual(distance(O[0], O[1]), 1.07, 4)

        CH2 = sys.subsystem([1, 2, 3], mods=[self.capper])
        self.assertEqual(CH2[3].role, CAPPING_ATOM)
        self.assertAlmostEqual(distance(CH2[1], CH2[3]), 0.97, 4)

    def test_two_AA(self):
        sys = read_example("dipeptide.xyz")

        p1 = sys.subsystem([0, 1, 2, 3, 4, 10, 11, 12, 13], mods=[self.capper])
        self.assertEqual(p1.size, 10)
        self.assertAlmostEqual(distance(p1[8], p1[9]), 1.019999, 4)

        p2 = sys.subsystem([5, 6, 7, 8, 9, 14, 15, 16, 17], mods=[self.capper])
        self.assertEqual(p1.size, 10)
        self.assertAlmostEqual(distance(p2[1], p2[9]), 0.97, 4)

    # def test_CappingPDB(self):
    #     supersys = read_geometry("small_protien", path=SMALL_PROTIEN_SYS_PATH)
    #     self.capper.setUp(supersys)
    #     fragmenter = get_fragmenter("PDB")("pdb_frag", "")
    #     p_frags = fragmenter.primary_fragments(supersys)
    #     aux_frags = fragmenter.aux_fragments(p_frags, order=3)

    #     total_caps = 0
    #     for frag in aux_frags.fragments:
    #         self.capper.run(frag)
    #         total_caps += frag.atoms.count(saved=False)

    #     self.assertEqual(total_caps, 160)

    # def test_CappingWater(self):
    #     supersys = read_geometry("water6", path=WATER6_SYS_PATH)
    #     self.capper.setUp(supersys)
    #     fragmenter = get_fragmenter("Water")("water_frag", "")
    #     p_frags = fragmenter.primary_fragments(supersys)
    #     aux_frags = fragmenter.aux_fragments(p_frags, order=3)

    #     total_caps = 0
    #     for frag in aux_frags.fragments:
    #         self.capper.run(frag)
    #         total_caps += frag.atoms.count(saved=False)

    #     self.assertEqual(total_caps, 0)
