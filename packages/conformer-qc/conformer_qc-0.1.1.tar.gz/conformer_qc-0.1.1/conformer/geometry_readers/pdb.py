#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import enum
from typing import Dict, TextIO

import numpy as np

from conformer.systems import Atom, NamedSystem


class PDBCols(enum.IntEnum):
    RES_TYPE = 0  # Residue or hetero atom
    ATOM_NO = 1
    RES_NUM = 5
    X = 6
    Y = 7
    Z = 8
    ATOM_TYPE = 11


def PDBRead(file: TextIO, charges: Dict[int, int] = {}) -> NamedSystem:
    atoms = []

    content = file.readlines()
    for line in content:
        # TODO: Make this support multi-protien files
        if line.startswith("ATOM") or line.startswith("HETATM"):
            atoms.append(atom_from_line(line, charges))

    # TODO: Add more metadata to system
    return NamedSystem(atoms)


def atom_from_line(line, charges: Dict[int, int]) -> Atom:
    """
    Creates an atom from a PDB lines
    """
    data = line.split()
    frag_type = "atom" if data[PDBCols.RES_TYPE] == "ATOM" else "hetero"

    # assign x,y,z coordinate using PDB
    x = float(data[PDBCols.X])
    y = float(data[PDBCols.Y])
    z = float(data[PDBCols.Z])

    t = data[PDBCols.ATOM_TYPE]
    pdb_atom_no = int(data[PDBCols.ATOM_NO])
    try:
        charge = charges[pdb_atom_no]
    except KeyError:
        charge = 0

    frag_i = int(data[PDBCols.RES_NUM])  # used to identify/number fragment

    return Atom(
        t,
        np.array([x, y, z]),
        charge=charge,
        meta={
            "residue_type": frag_type,
            "frag_group": frag_i,
            "pdb_atom_no": pdb_atom_no,
        },
    )
