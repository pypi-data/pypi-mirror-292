#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
"""Typed interface to QCElemental (which is not typed for mypyc)"""

from functools import cache
from typing import Final, List

import numpy as np
from qcelemental import (
    constants,
    covalentradii,  # type: ignore
    vdwradii,
)
from qcelemental import periodictable as ptable  # type: ignore


@cache
def get_Z(t: str) -> np.uint16:
    return np.uint16(ptable.to_atomic_number(t))


@cache
def get_period(t: str) -> int:
    return ptable.to_period(t) - 1


@cache
def get_mass(t: str) -> float:
    ret = ptable.to_mass(t)
    return np.float64(ret)


@cache
def get_covalent_radius(t: str) -> np.float64:
    """Cached wrapper around QCElemental's covalent radii"""
    return np.float64(covalentradii.get(t, units="angstrom"))


@cache
def get_vdw_radius(t: str) -> np.float64:
    """Cached wrapper around QCElemental's Van der Waals radii"""
    return np.float64(vdwradii.get(t, units="angstrom"))


ZERO = 1e-9
VALENCE_SIZE_BY_PERIOD: Final[List[int]] = [2, 8, 8, 18, 18, 32, 32]
CORE_E_BY_PERIOD: Final[List[int]] = [0, 2, 10, 18, 36, 54, 86]
TOTAL_E_BY_PERIOD: Final[List[int]] = [
    a + b for a, b in zip(VALENCE_SIZE_BY_PERIOD, CORE_E_BY_PERIOD)
]

BOHR_TO_ANGSTROM: Final[float] = constants.conversion_factor("bohr", "angstrom")
ANGSTROM_TO_BOHR: Final[float] = constants.conversion_factor("angstrom", "bohr")
KCAL_MOL_TO_HARTREE = constants.conversion_factor("kcal / mol", "hartree")
HARTREE_TO_KCAL_MOL = constants.conversion_factor("hartree", "kcal / mol")
HARTEE_TO_JOULE: Final[float] = constants.conversion_factor("hartree", "joule")
BOHR_TO_METER: Final[float] = constants.conversion_factor("bohr", "meter")
AMU_TO_KG: Final[float] = constants.conversion_factor("amu", "kg")
