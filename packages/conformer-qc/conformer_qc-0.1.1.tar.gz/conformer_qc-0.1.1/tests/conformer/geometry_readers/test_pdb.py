#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from unittest import TestCase

from conformer.example_systems import open_example
from conformer.geometry_readers.pdb import PDBRead


class PTestCase(TestCase):
    def test_pdb(self):
        with open_example("small_protien.pdb").open("r") as f:
            sys = PDBRead(f)
        atom_types = [a.t for a in sys]
        res_id = [a.meta["frag_group"] for a in sys]
        res_types = [a.meta["residue_type"] for a in sys]

        # Test fixtures
        # Atom Types
        self.assertEqual(
            atom_types,
            [
                "N",
                "C",
                "C",
                "O",
                "N",
                "C",
                "C",
                "O",
                "C",
                "C",
                "O",
                "O",
                "N",
                "C",
                "C",
                "O",
                "C",
                "O",
                "C",
                "N",
                "C",
                "C",
                "O",
                "C",
                "C",
                "C",
                "O",
                "O",
                "N",
                "N",
                "C",
                "C",
                "O",
                "C",
                "C",
                "C",
                "C",
                "N",
                "O",
                "C",
                "O",
                "C",
                "N",
                "O",
                "O",
                "C",
                "C",
                "N",
                "O",
                "O",
                "C",
            ],
        )
        # Residue IDs
        self.assertEqual(
            res_id, [1] * 4 + [2] * 8 + [3] * 7 + [4] * 9 + [5] + [6] * 9 + [7] * 13
        )
        # Residue Types
        self.assertEqual(
            res_types,
            [
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "atom",
                "hetero",
                "hetero",
                "hetero",
                "hetero",
                "hetero",
                "hetero",
                "hetero",
                "hetero",
                "hetero",
                "hetero",
                "hetero",
                "hetero",
                "hetero",
                "hetero",
                "hetero",
                "hetero",
                "hetero",
                "hetero",
                "hetero",
                "hetero",
                "hetero",
                "hetero",
            ],
        )

    def test_pdb_charge(self):
        with open_example("small_protien.pdb").open("r") as f:
            sys = PDBRead(f, {13: 1, 1727: -1, 1728: 1})
        self.assertEqual(sys[12].charge, 1)
        self.assertEqual(sys[12].meta["pdb_atom_no"], 13)
        self.assertEqual(sys[38].charge, -1)
        self.assertEqual(sys[38].meta["pdb_atom_no"], 1727)
        self.assertEqual(sys[39].charge, 1)
        self.assertEqual(sys[39].meta["pdb_atom_no"], 1728)
        self.assertEqual(sys.charge, 1)
