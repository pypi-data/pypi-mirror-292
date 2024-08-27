#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from random import randint as randi
from random import random as rand
from random import seed
from time import time

import numpy as np

REPS = 1000
SUB_REPS = 200
EL_TYPES = ["H", "C", "N", "B", "Cl"]
COORD_SCALE = 100.0


def randel() -> str:
    return EL_TYPES[randi(0, len(EL_TYPES) - 1)]


def test_conformer():
    from conformer.systems import System

    seed(314)
    s = time()
    for _ in range(REPS):
        # natoms = randi(4, 80)
        natoms = 20
        sys = System.from_tuples(
            atom_tuples=(("C", float(i), float(i), float(i)) for i in range(natoms))
        )
        # sys.hash()
        # sys.canonical_coords

        # for _ in range(SUB_REPS):
        #     sub_n = randi(1, natoms - 1)
        #     subset = frozenset((randi(0, natoms - 1) for _ in range(sub_n)))
        #     sys.subsystem(subset)

    print("Conformer", time() - s, "s")


def test_fragment():
    from fragment.systems.models import Atom as FA
    from fragment.systems.models import System as FS

    seed(314)
    s = time()
    for _ in range(REPS):
        natoms = randi(4, 80)
        sys = FS(
            [
                FA(
                    randel(),
                    np.array(
                        [
                            rand() * COORD_SCALE,
                            rand() * COORD_SCALE,
                            rand() * COORD_SCALE,
                        ]
                    ),
                )
                for __ in range(natoms)
            ]
        )
        # sys.canonical_coords()

        # for _ in range(SUB_REPS):
        #     sub_n = randi(1, natoms - 1)
        #     subset = frozenset((randi(0, natoms - 1) for _ in range(sub_n)))
        #     sys.subsystem(subset)
    print("Fragment", time() - s, "s")


def test_qcelemental():
    from qcelemental.models import Molecule

    seed(314)
    s = time()
    for _ in range(REPS):
        natoms = randi(4, 80)
        atom_types = []
        atom_coords = np.zeros((natoms, 3))
        for i in range(natoms):
            atom_types.append(randel())
            atom_coords[i, :] = (
                rand() * COORD_SCALE,
                rand() * COORD_SCALE,
                rand() * COORD_SCALE,
            )
        sys = Molecule(symbols=atom_types, geometry=atom_coords)
        # sys.orient_molecule()

        # for _ in range(SUB_REPS):
        #     sub_n = randi(1, natoms - 1)
        #     subset = frozenset((randi(0, natoms - 1) for _ in range(sub_n)))
        #     sys.get_fragment(sorted(subset))
    print("QCElemental", time() - s, "s")


def test_ase():
    from ase import Atoms

    seed(314)
    s = time()
    for _ in range(REPS):
        natoms = randi(4, 80)
        atom_types = []
        atom_coords = []
        for i in range(natoms):
            atom_types.append(randel())
            atom_coords.append(
                (
                    rand() * COORD_SCALE,
                    rand() * COORD_SCALE,
                    rand() * COORD_SCALE,
                )
            )
        sys = Atoms("".join(atom_types), atom_coords)
        # desc = SOAP(2.0, 2, 5 ,species=[1, 6, 7, 17, 5], average="outer")
        # sys.orient_molecule()

        # for _ in range(SUB_REPS):
        #     sub_n = randi(1, natoms - 1)
        #     subset = frozenset((randi(0, natoms - 1) for _ in range(sub_n)))
        #     sys.get_fragment(sorted(subset))
    print("ASE", time() - s, "s")


test_conformer()
test_fragment()
test_qcelemental()
test_ase()
