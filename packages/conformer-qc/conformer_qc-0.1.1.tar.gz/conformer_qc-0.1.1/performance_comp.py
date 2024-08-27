#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from random import randint as randi
from random import seed
from time import time

import numpy as np

REPS = 50000
# REPS = 5
SUB_REPS = 200
EL_TYPES = ["H", "C", "N", "B", "Cl"]
COORD_SCALE = 100.0


def randel() -> str:
    return EL_TYPES[randi(0, len(EL_TYPES) - 1)]


def warm():
    from conformer.systems import System

    sys = System.from_tuples(
        ((randel(), float(i), float(i), float(i)) for i in range(50))
    )
    sys.COM


SYSTEMS = []
for _ in range(REPS):
    NATOMS = randi(4, 80)
    ATOMS = []
    for i in range(NATOMS):
        ATOMS.append([randel(), float(i), float(i), float(i)])
    SYSTEMS.append(ATOMS)


def test_conformer():
    from conformer.systems import System

    s = time()
    for ATOMS in SYSTEMS:
        sys = System.from_tuples(ATOMS)
        # sys.r_matrix
        # sys.fingerprint
        # print(sys.mass)
        # sys.fingerprint()
        # sys.__hash__()
        # sys.canonical_coords

        # for _ in range(SUB_REPS):
        #     sub_n = randi(1, natoms - 1)
        #     subset = frozenset((randi(0, natoms - 1) for _ in range(sub_n)))
        #     sys.subsystem(subset)

    print("Conformer", time() - s, "s")


# def test_fragment():
#     from fragment.systems.models import Atom as FA
#     from fragment.systems.models import System as FS

#     seed(314)
#     s = time()
#     for _ in range(REPS):
#         natoms = randi(4, 80)
#         sys = FS(
#             [
#                 FA(
#                     randel(),
#                     np.array(
#                         [
#                             rand() * COORD_SCALE,
#                             rand() * COORD_SCALE,
#                             rand() * COORD_SCALE,
#                         ]
#                     ),
#                 )
#                 for __ in range(natoms)
#             ]
#         )
#         # sys.canonical_coords()

#         # for _ in range(SUB_REPS):
#         #     sub_n = randi(1, natoms - 1)
#         #     subset = frozenset((randi(0, natoms - 1) for _ in range(sub_n)))
#         #     sys.subsystem(subset)
#     print("Fragment", time() - s, "s")


def test_qcelemental():
    from qcelemental.models import Molecule

    s = time()
    for ATOMS in SYSTEMS:
        atom_types = [a[0] for a in ATOMS]
        atom_coords = np.array([a[1:] for a in ATOMS])
        sys = Molecule(symbols=atom_types, geometry=atom_coords)
        # print(sum(sys.mass_numbers))
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
    for ATOMS in SYSTEMS:
        atom_types = [a[0] for a in ATOMS]
        atom_coords = np.array([a[1:] for a in ATOMS])
        sys = Atoms("".join(atom_types), atom_coords)
        # print(sum(sys.get_masses()))
        # desc = SOAP(2.0, 2, 5 ,species=[1, 6, 7, 17, 5], average="outer")
        # sys.orient_molecule()

        # for _ in range(SUB_REPS):
        #     sub_n = randi(1, natoms - 1)
        #     subset = frozenset((randi(0, natoms - 1) for _ in range(sub_n)))
        #     sys.get_fragment(sorted(subset))
    print("ASE", time() - s, "s")


warm()  # Handle caching issues with QCElemental atomic data
print(f"Creating {REPS} random systems")
test_conformer()
# test_fragment()
test_qcelemental()
test_ase()
