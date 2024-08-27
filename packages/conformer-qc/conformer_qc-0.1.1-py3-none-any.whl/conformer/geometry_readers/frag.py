#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from io import TextIOWrapper
from typing import Dict, List

import numpy as np

from conformer.systems import Atom, NamedSystem


def FragRead(file: TextIOWrapper, charges: Dict[int, int]) -> NamedSystem:
    atoms: List[Atom] = []
    frag_group = 1
    atoms_in_group = 0

    for i, line in enumerate(file):
        line = line.strip()
        if i == 0:  # Number of atoms
            num_atoms = int(line)
            continue
        if i == 1:  # Comment line
            continue
        if line.startswith("---"):
            if atoms_in_group:
                frag_group += 1
            continue
        if not line:
            break

        atoms_in_group += 1
        charge = charges.get(atoms_in_group, 0)
        atoms.append(atom_from_line(line, frag_group, charge=charge))

    if num_atoms != len(atoms):
        raise Exception("XYZ input contains a different number of atoms than promised.")
    return NamedSystem(atoms)


def atom_from_line(line: str, frag_group: int, charge=0) -> Atom:
    """
    Creates an atom from a PDB lines
    """
    data = line.split()
    t = data[0]
    x = float(data[1])
    y = float(data[2])
    z = float(data[3])

    return Atom(t, np.array([x, y, z]), charge=charge, meta={"frag_group": frag_group})
