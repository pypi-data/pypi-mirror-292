#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import hashlib
import json
from collections.abc import MutableMapping, MutableSet
from copy import copy, deepcopy
from datetime import datetime
from functools import reduce
from itertools import combinations
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    Final,
    FrozenSet,
    Generator,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    Union,
    overload,
)

import numpy as np
import numpy.typing as npt
from scipy.spatial import KDTree

from conformer_core.caching import Cachable, cached_property
from conformer_core.util import ind, summarize

from .common import (
    GHOST_ATOM,
    PHYSICAL_ATOM,
    AtomRole,
    Mask,
    Maskable,
    mask,
    role_to_bytes,
    role_to_int,
    role_to_str,
)
from .elements import (
    ANGSTROM_TO_BOHR,
    CORE_E_BY_PERIOD,
    VALENCE_SIZE_BY_PERIOD,
    get_covalent_radius,
    get_mass,
    get_period,
    get_vdw_radius,
    get_Z,
)

NPi32 = npt.NDArray[np.int32]
NPf64 = npt.NDArray[np.float64]


R_TOLORANCE_V1: Final[float] = 1e-6
R_TOLORANCE_V2: Final[float] = 1e-8
R_TOLORANCE: Final[float] = R_TOLORANCE_V1  # Global Tolorance
ORIGIN_INT: Final[NPi32] = np.array([0, 0, 0], dtype=np.int32)
HASH_ALG: Final[Type] = hashlib.sha1

ORIGIN_INT: Final[NPi32] = np.array([0, 0, 0], dtype=np.int32)
HASH_ALG: Final[Type] = hashlib.sha1


###########################################################
#                      JOIN_FUNCTIONS                     #
###########################################################


def bound_COM_join(a1: "BoundAtom", a2: "BoundAtom") -> bool:
    if (a1.t != a2.t) or (a1._role != a2._role) or (a1.charge != a2.charge):
        return False
    return np.allclose(a1.r - a1.system.COM, a2.r - a2.system.COM, atol=R_TOLORANCE)


def bound_join(a1: "BoundAtom", a2: "BoundAtom") -> bool:
    if (a1.t != a2.t) or (a1._role != a2._role) or (a1.charge != a2.charge):
        return False
    if a1._atom.r is a2._atom.r:
        return True
    return np.allclose(a1._atom.r, a2._atom.r, atol=R_TOLORANCE)


def unbound_bound_join(a1: "Atom", ba2: "BoundAtom") -> bool:
    if (a1.t != ba2.t) or (a1.charge != ba2._atom.charge):
        return False
    if ba2.system.unit_cell is None:
        return np.allclose(a1.r, ba2.r, atol=R_TOLORANCE)
    else:
        abs_diff = np.abs(a1.r - ba2.r) % ba2.system.unit_cell
        return np.all(abs_diff < R_TOLORANCE)


def unbound_join(a1: "Atom", a2: "Atom") -> bool:
    """Unbound join takes into accoun the properties of the unbound atom and so ignores the role and cell properties.
    """
    if isinstance(a1, BoundAtom):
        a1 = a1._atom
    if isinstance(a2, BoundAtom):
        a2 = a2._atom

    if (a1.t != a2.t) or (a1.charge != a2.charge):
        return False
    if a1.r is a2.r:
        return True
    return np.allclose(a1.r, a2.r, atol=R_TOLORANCE)


def default_join(a1: "AbstractAtom", a2: "AbstractAtom", tolerance=None) -> bool:
    if isinstance(a1, BoundAtom):
        if isinstance(a2, BoundAtom):
            return bound_join(a1, a2)
        else:
            return unbound_bound_join(a2, a1)
    else:
        if isinstance(a2, BoundAtom):
            return unbound_bound_join(a1, a2)
        else:
            return unbound_join(a1, a2)
    return False

    tolerance = R_TOLORANCE if tolerance is None else tolerance

    if a1 is a2:
        return True

    # Normalize atom data
    if isinstance(a1, BoundAtom) and a1._system is not None:
        ua1 = a1._atom
        is_bound1 = True
        uc1 = a1._system.unit_cell
    else:
        ua1 = a1
        is_bound1 = False
        uc1 = None

    # Normalize atom data
    if isinstance(a2, BoundAtom):
        ua2 = a2._atom
        is_bound2 = True
        uc2 = a2._system.unit_cell
    else:
        ua2 = a2
        is_bound2 = False
        uc2 = None

    # TODO: Handle proxys
    if ua1.t != ua2.t or ua1.charge != ua2.charge:
        return False

    # Two Bound Atoms
    if is_bound1 and is_bound2:
        if a1._role != a2._role:
            return False

        # Must have the same unitcell
        if (
            (uc1 is not None)
            and (uc2 is not None)
            and (not np.allclose(uc1, uc2, atol=R_TOLORANCE))
        ):
            return False

        # Perhaps we can get lucky
        if ua1 is ua2:
            return True

    # Get the unitce
    if is_bound1:
        unit_cell = uc1
    elif is_bound2:
        unit_cell = uc2
    else:
        unit_cell = None

    # Check position
    if unit_cell is None:
        if np.allclose(ua1.r, ua2.r, atol=tolerance):
            return True
    else:
        abs_diff = np.abs(ua1.r - ua1.r) % unit_cell
        if np.all(abs_diff < R_TOLORANCE):
            return True
    return False


def is_join(a1: "AbstractAtom", a2: "AbstractAtom") -> bool:
    return a1 is a2


###########################################################
#                      HASH FUNCTIONS                     #
###########################################################


def hash_NPf64_v1(
    a: NPf64, hasher: "hashlib._Hash", tolerance: float, inplace=False
) -> "hashlib._Hash":
    if not inplace:
        a = a.copy()
    a /= tolerance
    hasher.update(a.astype("<i8").tobytes())
    return hasher


def hash_NPf64_v2(
    a: NPf64, hasher: "hashlib._Hash", tolerance: float, inplace=False
) -> "hashlib._Hash":
    """Adds an additional rounding step"""
    if not inplace:
        a = a.copy()
    a /= tolerance
    np.round(a, out=a) # V2 Adds a round
    hasher.update(a.astype("<i8").tobytes())
    return hasher


def hash_Atom_v1(
    atom: "Atom",
    r_offset: Optional[NPf64] = None,
    hasher: Optional["hashlib._Hash"] = None,
) -> "hashlib._Hash":
    """V1 Hash for an abstract atom"""
    if hasher is None:
        hasher = HASH_ALG()

    hasher.update(atom.t.encode("utf-8"))
    if r_offset is None:
        # Little endian 64 bit integer
        r_data = atom.r.copy()
    else:
        r_data = atom.r + r_offset
    hash_NPf64_v1(r_data, hasher, R_TOLORANCE_V1)
    hasher.update(atom.charge.astype("<i2").tobytes())

    # Print, sort, metadata if it exists
    if atom.meta:
        if atom._meta_s is None:
            atom._meta_s = json.dumps(atom.meta, sort_keys=True).encode("utf-8")
        hasher.update(atom._meta_s)

    return hasher


def hash_Atom_v2(
    atom: "Atom",
    r_offset: Optional[NPf64] = None,
    hasher: Optional["hashlib._Hash"] = None,
) -> "hashlib._Hash":
    """V2 Hash for an Atom

    Adds round and increases tolorance from 1e-6 to 1e-8
    """
    if hasher is None:
        hasher = HASH_ALG()

    hasher.update(atom.t.encode("utf-8"))
    if r_offset is None:
        # Little endian 64 bit integer
        hash_NPf64_v2(atom.r, hasher, R_TOLORANCE_V2)
    else:
        hash_NPf64_v2(atom.r + r_offset, hasher, R_TOLORANCE_V2, inplace=True)
    hasher.update(atom.charge.astype("<i2").tobytes())

    # Print, sort, metadata if it exists
    if atom.meta:
        if atom._meta_s is None:
            atom._meta_s = json.dumps(atom.meta, sort_keys=True).encode("utf-8")
        hasher.update(atom._meta_s)
    return hasher

def hash_BoundAtom_v1(
    atom: "BoundAtom",
    r_offset: Optional[NPf64] = None,
    hasher: Optional["hashlib._Hash"] = None,
    atom_hash: Callable = hash_Atom_v1,
) -> "hashlib._Hash":
    """Copy of the Atom byte digest but with added methods for role

    This implicitly takes into account the cell offset because it uses self.r
    instead of self._atom.r. This does mean some code duplication
    """
    if hasher is None:
        hasher = HASH_ALG()

    # Get the atoms hash properties
    if atom._system.unit_cell is None:
        atom_hash(atom._atom, r_offset=r_offset, hasher=hasher)
    else:
        atom_hash(
            atom._atom,
            r_offset=r_offset + atom._system.unit_cell * atom.cell,
            hasher=hasher,
        )

    # Bound-Atom specific
    hasher.update(role_to_bytes(atom.role))
    return hasher


def hash_UnitCell_v1(r: NPf64 | None, hasher: Optional["hashlib._Hash"] = None) -> str:
    """
    Hashes a orthorombic unit cell. Later versions should handle non-orthorombic cells
    """
    if hasher is None:
        hasher = HASH_ALG()

    if r is None:
        return hasher

    # hasher.update((r / R_TOLORANCE).astype("<i8").tobytes())
    # hasher.update((r / R_TOLORANCE_V1).astype("<i8").tobytes())
    # return hasher.hexdigest()

    return hash_NPf64_v1(r, hasher, R_TOLORANCE_V1)


def hash_UnitCell_v2(r: NPf64 | None, hasher: Optional["hashlib._Hash"] = None) -> str:
    """
    Hashes a orthorombic unit cell. Later versions should handle non-orthorombic cells
    """
    if hasher is None:
        hasher = HASH_ALG()

    if r is None:
        return hasher

    return hash_NPf64_v2(r, hasher, R_TOLORANCE_V2)


def hash_System_v1(
    sys: "System", hasher: Optional["hashlib._Hash"] = None, use_fast=True
) -> "hashlib._Hash":
    if hasher is None:
        hasher = HASH_ALG()

    if sys.unit_cell is not None:
        hash_UnitCell_v1(sys.unit_cell, hasher=hasher)

    for a in sys._canonical_atoms:
        hash_BoundAtom_v1(a, r_offset=-sys.COM, hasher=hasher, atom_hash=hash_Atom_v1)
    return hasher


def hash_System_v2(
    sys: "System", hasher: Optional["hashlib._Hash"] = None, use_fast=True
) -> "hashlib._Hash":
    if hasher is None:
        hasher = HASH_ALG()

    if sys.unit_cell is not None:
        hash_UnitCell_v2(sys.unit_cell, hasher)

    if use_fast:
        # TODO: Migrate to doing this column wise? This would let us use the hash_NPf64 function
        r_data = sys.r_matrix - sys.COM
        r_data /= R_TOLORANCE_V2
        np.round(r_data, out=r_data)
        r_int_data = r_data.astype("<i8")

        # Handle non-canonized systems
        if sys.is_canonized:
            data_iterator = zip(r_int_data, sys)
        else:
            _order = sorted(range(len(sys)), key=lambda x: sys[x])
            data_iterator = zip(r_int_data[_order, :], sys[_order])
        return reduce(update_fingerprint, data_iterator, hasher)
    else:
        for a in sys._canonical_atoms:
            hash_BoundAtom_v1(a, r_offset=-sys.COM, hasher=hasher, atom_hash=hash_Atom_v2)
    return hasher


def update_fingerprint(_h: "hashlib._Hash", d: Tuple[NPf64, "BoundAtom"]):
    """Hashing wrapper for atom-data for fingerprinting using map-reduce strategy"""
    r, a = d
    ua = a._atom  #  Operate on the unbound atom
    _h.update(ua.t.encode("utf-8"))
    _h.update(r.data)
    _h.update(ua.charge.astype("<i2").data)
    if a.meta:
        if ua._meta_s is None:
            ua._meta_s = json.dumps(ua.meta, sort_keys=True).encode("utf-8")
        _h.update(ua._meta_s)
    _h.update(role_to_bytes(a.role))
    return _h


###########################################################
#                       ATOM CLASSES                      #
###########################################################
class AbstractAtom:
    # Don't define slots. They clash with pickle when overwriting with @property methods
    __slots__ = tuple()

    REQUIRED_ATTRS = ("t", "r", "charge")

    @classmethod
    def __init_subclass__(cls) -> None:
        for attr in cls.REQUIRED_ATTRS:
            if not hasattr(cls, attr):
                raise AttributeError(
                    f"Subclass of `{cls.__name__}` is missing attribute '{attr}'"
                )

    #########   ATOM PROPERTIES   #########
    @property
    def Z(self) -> int:
        """Atomic number"""
        return get_Z(self.t)

    @property
    def period(self) -> int:
        """Period on The Table"""
        return get_period(self.t)

    @property
    def electrons(self) -> int:
        """Number of bound electrons"""
        return self.Z - self.charge

    @property
    def core_electrons(self) -> int:
        """Number of core electrons"""
        return min(CORE_E_BY_PERIOD[get_period(self.t)], self.electrons)

    @property
    def valence_electrons(self) -> int:
        """Actual number of valence electrons"""
        return self.electrons - self.core_electrons

    @property
    def max_valence(self) -> int:
        """Maximum number of valence electrons"""
        return VALENCE_SIZE_BY_PERIOD[get_period(self.t)]

    # General properties
    @property
    def mass(self) -> float:
        """Atomic mass in a.u."""
        return get_mass(self.t)

    @property
    def covalent_radius(self) -> float:
        """Covalent radius in Å"""
        return get_covalent_radius(self.t)

    @property
    def vdw_radius(self) -> float:
        """van der Waals radius in Å"""
        return get_vdw_radius(self.t)

    def __eq__(self, other_atom: Any) -> bool:
        if not isinstance(other_atom, AbstractAtom):
            return False
        return default_join(self, other_atom)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        attrs = getattr(self, "__slots__", ("t", "r", "charge"))
        args = ", ".join((i + "=" + getattr(self, i).__repr__() for i in attrs))
        return f"{class_name}({args})"


class Atom(AbstractAtom):
    __slots__: ClassVar[Tuple[str, ...]] = (
        "t",
        "r",
        "charge",
        "meta",
        "_meta_s",
        "_saved",
    )

    # Define required attrs as variables
    t: str
    r: NPf64
    charge: np.int16

    # # Store additional information (e.g., partial charge)
    meta: Dict[str, Any]
    _saved: int  # Allows use with the saveable API

    def __init__(
        self,
        t: str,
        r: Union[NPf64, Sequence[float]],
        charge=0,
        meta: Optional[Dict[str, Any]] = None,
        _saved: int = 0,
    ):
        super().__init__()
        self.t = t
        self.r = np.array(r, dtype=np.float64)
        self.charge = np.int16(charge)
        # self.charge = int(charge)
        self.meta = {} if meta is None else meta
        self._meta_s = None
        self._saved = _saved

    def copy(self):
        """Simply copy. How does this work with r?"""
        return copy(self)

    ######### HASHING AND EQUALITY #########
    @property
    def fingerprint(self) -> str:
        return hash_Atom_v2(self).hexdigest()

    def hash_data(self, r_offset: Optional[NPf64] = None) -> Tuple:
        # Handle coordinates
        if r_offset is None:
            _r = self.r / R_TOLORANCE
        else:
            _r = self.r + r_offset
            _r /= R_TOLORANCE
        r = tuple(map(int, _r))

        # Handle metadata
        # DO NOT include metadata is hash. Performance
        # if self.meta:
        #     meta = json.dumps(self.meta, sort_keys=True)
        # else:
        #     meta = None

        return (self.t, r, self.charge)

    def __hash__(self) -> int:
        return self.hash_data().__hash__()  # Don't include any offsets by default :)


class BoundAtom(AbstractAtom):
    """
    In-system context for an atom

    Atoms may have different roles on a system-by-system basis
    """

    __slots__: ClassVar[Tuple[str, ...]] = (
        "_atom",
        "_system",
        "_role",
        "_cell",
    )

    _atom: Atom
    _system: Optional["System"]  # Not optional. But construction is circular
    _role: AtomRole
    _cell: NPi32

    # def __new__(cls,
    #         a: Union[Atom, 'BoundAtom'],
    #         s: Optional['System'] = None,
    #         role: Optional[AtomRole] = None,
    #         cell: Optional[Iterable[int]] = None
    #     ) -> 'BoundAtom':
    #     if isinstance(a, cls) and a.system is None:
    #         return a
    #     return super().__new__(cls)

    def __init__(
        self,
        a: Union[Atom, "BoundAtom"],
        s: Optional["System"] = None,
        role: Optional[AtomRole] = None,
        cell: Optional[Iterable[int]] = None,
    ):
        # Reuse ORIGIN_INT if possible
        if cell is None:
            _cell = ORIGIN_INT
        elif cell is ORIGIN_INT:
            _cell = cell
        else:
            _cell = np.array(cell, dtype=np.int32)

        if isinstance(a, BoundAtom):
            self._atom = a._atom
            self._system = s
            self._role = a.role if role is None else role
            self._cell = a.cell if cell is None else _cell
        else:
            self._atom = a
            self._system = s
            self._role = PHYSICAL_ATOM if role is None else role
            self._cell = ORIGIN_INT if cell is None else _cell

    ######### ALTERNATE CONSTRUCTORS #########
    def bind_or_copy(self, s: "System") -> "BoundAtom":
        # NOTE: Could this be replaced with `__new__` method?
        if self._system is None:
            self.system = s
            return self
        else:
            return self.__class__(self, s)

    ######### GETTERS AND SETTERS #########
    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, v: AtomRole) -> None:
        self._role = v
        self.system._saved = 0
        self.system.is_canonized = False
        self.system._reset_cache()

    @property
    def cell(self) -> NPi32:
        return self._cell

    @cell.setter
    def cell(self, v: NPi32) -> None:
        self._cell = v
        self.system._saved = 0
        self.system.is_canonized = False
        self.system._reset_cache()

    @property
    def system(self) -> "System":
        if self._system is None:
            raise ValueError("BoundAtom.system should not be None.")
        return self._system

    @system.setter
    def system(self, s: "System") -> None:
        if self._system is not None:
            raise ValueError("BoundAtoms cannot be rebound.")
        self._system = s

    ######### PASSTHROUGH PROPERTIES #########
    @property
    def t(self) -> str:
        return self._atom.t

    @property
    def r(self) -> NPf64:
        if self.system.unit_cell is None:
            return self._atom.r
        else:
            return self._atom.r + self.system.unit_cell * self.cell

    @property
    def charge(self) -> np.int16:
        if self.is_physical or self.is_point_charge:
            return self._atom.charge
        else:
            return np.int16(0)

    @property
    def electrons(self) -> int:
        if self.role.is_physical:
            return super().electrons
        return 0

    @property
    def core_electrons(self) -> int:
        if self.role.is_physical:
            return super().core_electorons
        return 0

    @property
    def valence_electrons(self) -> int:
        """Actual number of valence electrons"""
        if self.role.is_physical:
            return super().core_electorons
        return 0

    @property
    def mass(self) -> np.float64:
        if self.is_physical:
            return np.float64(self._atom.mass)
        else:
            return np.float64(0.0)

    @property
    def meta(self) -> Dict[str, Any]:
        return self._atom.meta

    @property
    def _saved(self) -> int:
        return self._atom._saved

    ######### ATOM ROLE PROPERTIES #########
    @property
    def is_physical(self) -> bool:
        return self.role.is_physical

    @property
    def is_proxy(self) -> bool:
        return self.role.is_proxy

    @property
    def has_basis_fns(self) -> bool:
        return self.role.has_basis_fns

    @property
    def is_point_charge(self) -> bool:
        return self.role.is_point_charge

    ######### ATOM HASHING HELPERS #########

    def sort_data(self) -> Tuple:
        return (
            tuple(self._cell),
            self._role,
            tuple(self.r),
            self.t,
            self.charge,
        )

    def __lt__(self, other: "BoundAtom") -> bool:
        # Sort by role, cell, position, t, charge
        if self._system.unit_cell is not None:
            for s, o in zip(self._cell, other._cell):
                if s < o:
                    return True
                elif s != o:
                    return False

        if self._role < other.role:
            return True
        elif self._role != other.role:
            return False

        for s, o in zip(self._atom.r, other._atom.r):
            if s < o:
                return True
            elif s != o:
                return False

        if self.t < other.t:
            return True
        elif self.t != other.t:
            return False

        if self.charge < other.charge:
            return True
        return False

        # return self.sort_data() < other.sort_data()

    def hash_data(self, r_offset: Optional[NPf64] = None) -> Tuple:
        # Calculate custom offset based on self.cell
        if self._system.unit_cell is None:
            offset = r_offset
        elif r_offset is None:
            offset = self._system.unit_cell * self.cell
        else:
            offset = r_offset + self._system.unit_cell * self.cell

        return (
            self._atom.hash_data(offset),  # Accounts for self.cell
            self.role,
        )

    def __hash__(self) -> int:
        return self.hash_data().__hash__()

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        attrs = [
            "t=" + self.t,
            "r=" + str(self.r),
        ]

        role = role_to_str(self.role)
        if role:
            attrs.append("role='" + role + "'")
        args = ", ".join(attrs)
        return f"{class_name}({args})"


###########################################################
#                     SYSTEM MODEL                        #
###########################################################


class System(Cachable, Sequence[BoundAtom]):
    """A system is a collection of atoms.

    Atoms and their context are kept separate because we would like to
    reuse atoms as ghost atoms or as point charges in subsystems.
    """

    # Internal data
    _atoms: List[BoundAtom]
    unit_cell: Optional[NPf64]
    supersystem: Optional["System"]
    is_canonized: bool = False
    _saved: int = 0

    def __init__(
        self,
        atoms: Iterable[AbstractAtom],
        unit_cell: Optional[NPf64] = None,
        supersystem: Optional["System"] = None,
        is_canonized: bool = False,
        _saved: int = 0,
    ):
        self._atoms = [self.bind_atom(a) for a in atoms]
        self.unit_cell = (
            None if unit_cell is None else np.array(unit_cell, dtype=np.float64)
        )
        self.supersystem = supersystem
        self.is_canonized = is_canonized
        self._saved = _saved

        # DEBUG: Remove once stability improves
        for a in self:
            assert self is a.system

    def bind_atom(
        self,
        a: AbstractAtom,
        role: Optional[AtomRole] = None,
        cell: Optional[NPi32] = None,
    ) -> BoundAtom:
        """Normalizes any Atom-Like type into a BoundAtom"""
        if isinstance(a, Atom):
            return BoundAtom(a, self, role, cell)
        elif isinstance(a, BoundAtom):
            if role is None and cell is None:
                return a.bind_or_copy(self)
            role = a._role if role is None else role
            cell = a._cell if cell is None else cell
            return BoundAtom(a, self, role, cell)

        raise ValueError(f"Unknown atom class `{a.__class__.__name__}`")

    def add_atoms(
        self,
        *atoms: AbstractAtom,
        role: Optional[AtomRole] = None,
        cell: Optional[NPi32] = None,
    ) -> None:
        """Adds atoms to system with optional context

        If no context is specified, it is a physical atom
        """
        for a in atoms:
            self._atoms.append(self.bind_atom(a, role, cell))
        self._saved = 0
        self.is_canonized = False
        self._reset_cache()

    def update_atoms(
        self,
        idxs: List[int],
        role: Optional[AtomRole] = None,
        cell: Optional[NPi32] = None,
    ) -> None:
        for a in self[idxs]:
            if role is not None:
                a._role = role
            if cell is not None:
                a._cell = np.array(cell, dtype=np.int32)
        self._saved = 0
        self.is_canonized = False
        self._reset_cache()

    def reorder(self, order: List[int]) -> None:
        """Reorders the system to match `order`"""
        assert set(range(len(self._atoms))) == set(order)
        self._atoms = list(self[order])
        self.is_canonized = False
        self._reset_cache()

    def _canonize(self) -> None:
        """Reorders the system into canonical order (see `BoundAtom.__lt__`)"""
        if self._atoms:
            self._atoms.sort()

            # # Renormalize the cells
            # if self.unit_cell is None:
            #     for a in self._atoms:
            #         a._cell = ORIGIN_INT
            # else:
            #     cells = np.array([a._cell for a in self._atoms])
            #     min_cell = cells.min(axis=0)
            #     for a in self._atoms:
            #         a._cell = a._cell - min_cell

        self.is_canonized = True
        self._reset_cache()

    #################################
    #####     CONSTRUCTORS      #####
    #################################
    @classmethod
    def from_tuples(
        cls, atom_tuples: Iterable[Tuple[str, float, float, float]], **kwargs
    ) -> "System":
        return cls((Atom(d[0], d[1:4]) for d in atom_tuples), **kwargs)

    @classmethod
    def from_string(
        cls,
        atom_str: str,
    ) -> "System":
        atoms: List[BoundAtom] = []
        for l in atom_str.splitlines():
            l = l.strip()
            if not l:
                continue
            a_data = l.split()
            if len(a_data) != 4:
                raise Exception(f'Invalid atom definition "{l}"')
            t, x, y, z = a_data
            if t.startswith("@"):
                a_role = GHOST_ATOM
                t = t[1:]
            else:
                a_role = PHYSICAL_ATOM
            atoms.append(
                BoundAtom(
                    Atom(t, [float(i) for i in (x, y, z)]),
                    None,  # Don't bind yet
                    role=a_role,
                )
            )
        return cls(atoms=atoms)

    def copy(self) -> "System":
        """Returns a copy of the object as a `System`

        .. note::
            This will include named systems or tother special types of systems
        """
        new_sys = System(
            self,
            unit_cell=None if self.unit_cell is None else self.unit_cell.copy(),
            supersystem=self.supersystem,
        )
        return new_sys

    def deepcopy(self) -> "System":
        atoms = [BoundAtom(deepcopy(a._atom), role=a.role, cell=a.cell) for a in self]
        return System(
            atoms,
            unit_cell=None if self.unit_cell is None else self.unit_cell.copy(),
            supersystem=self.supersystem,
            _saved=self._saved,
        )

    def canonize(self) -> "System":
        """Returns a canonized copy of the system"""
        sys = self.copy()
        sys._canonize()
        sys._saved = self._saved  # Canonization doesn't change DBID
        return sys

    def shift(self, delta: NPf64) -> "System":
        # Don't recenter if we don't need to
        if np.allclose(delta, np.array([0.0, 0.0, 0.0]), atol=R_TOLORANCE):
            return self

        sys = self.deepcopy()
        for a in sys:
            a._atom.r += delta
            a._atom._saved = 0
        return sys

    def recenter(self, first_atom_r: NPf64) -> "System":
        if self.is_canonized:
            first_atom = self[0]
        else:
            first_atom = next(self._canonical_atoms)
        delta = first_atom_r - first_atom.r
        return self.shift(delta)

    def subsystem(
        self,
        _mask: Maskable,
        mods: Optional[Sequence[Callable[["System", "System"], "System"]]] = None,
    ) -> "System":
        """Create a subsystem from current system

        .. NOTE::
            This does allow duplicates of atoms which is intentional

        .. NOTE::
            This intentionally forces the result to be a System object
        """
        m = mask(_mask)
        sys = System(
            atoms=self[m],
            supersystem=self,
            unit_cell=self.unit_cell,
        )

        # Handle system modification
        if mods is None:
            sys.is_canonized = True
            return sys

        for mod in mods:
            sys = mod(self, m, sys)
            sys._canonize()
        return sys

    def merge(self, *other_systems: "System") -> "System":
        # Check the the unit cells are compatible
        return merge(self, *other_systems)


    def join_map(
        self, other_sys: "System" | Iterable[AbstractAtom], join_fn=default_join
    ) -> List[Tuple[int, int]]:
        """Returns a mapping from this system (`self`) to the `other_sys` using a
        nested list join.

        The nested loop, though slower than a hash lookup, was chosen because it allows
        for easy equality checking using `join_fn`.
        """

        mapping = []
        if isinstance(other_sys, System):
            points = other_sys.r_matrix
            atoms = other_sys
        else:
            points = []
            atoms = []
            for a in other_sys:  # Could something besides a sequence
                points.append(a.r)
                atoms.append(a)
            points = np.array(points)

        for i2, nearby in enumerate(self.atoms_near(points, search_r=0.1)):
            a2 = atoms[i2]
            for i1, a1 in nearby:
                if join_fn(a1, a2):
                    mapping.append((i1, i2))
        return mapping


    def subsystem_mask(self, other: "System", join_fn=default_join, ignore_missing=False) -> Maskable:
        key = set()
        use_mask = False
        for i, j in self.join_map(other, join_fn=unbound_join):
            key.add(i)
            # cell = None
            # role = None
            # a1 = self[i]
            # a2 = self[j]
            # if a1.role != a2.role:
            #     role = a2.role
            # if not np.all(a1.cell == a2.cell):
            #     cell = a2.cell
            # if role is None and cell is None:
            #     key.add(idx)
            # else:
            #     key.add((idx, CellIndex(cell), role))

        if not ignore_missing:
            assert len(key) == len(other)

        if use_mask:
            return Mask.from_itr(key)
        else:
            return frozenset(key)


    #################################
    #####    Sequence methods   #####
    #################################
    def __len__(self) -> int:
        return self._atoms.__len__()

    @property
    def size(self) -> int:
        return len(self)

    @property
    def _canonical_atoms(self) -> Iterable[BoundAtom]:
        if self.is_canonized:
            return self._atoms.__iter__()
        else:
            _order = sorted(range(len(self)), key=lambda x: self[x])
            return self[_order]

    def __iter__(self) -> Iterator[BoundAtom]:
        return self._atoms.__iter__()

    def atoms_near(
        self, _points: NPf64, k=1, search_r=None
    ) -> Iterable[List[Tuple[int, Atom]]]:
        _points = np.array(_points)
        points = _points.reshape((-1, 3))
        if search_r is None:
            if k == 1:  # Because scipy thinks it's fun to have returns depend on inputs
                _, _a = self.kdtree.query(points, k=k)
                a = [[i] for i in _a]
            else:
                _, a = self.kdtree.query(points, k=k)
        else:
            a = self.kdtree.query_ball_point(points, search_r)

        for i in a:
            yield zip(i, self[i])

    def in_(self, a: AbstractAtom, search_r=None) -> bool:
        if not self._atoms:
            return False # Always false for empty system

        if isinstance(a, BoundAtom) and a._system is self:
            return True

        # Do more expensive search
        try:
            nearby = next(self.atoms_near(a.r, search_r=search_r))  # Get first
        except StopIteration:
            return False

        for _, in_a in nearby:
            if in_a.__eq__(a):
                return True
        return False

    def __contains__(self, val: AbstractAtom) -> bool:
        return self.in_(val)

    @overload
    def __getitem__(self, idx: int) -> BoundAtom: ...

    @overload
    def __getitem__(self, idx: slice) -> List[BoundAtom]: ...

    @overload
    def __getitem__(self, idx: Iterable[int]) -> Generator[BoundAtom, None, None]: ...

    def __getitem__(self, idx):
        # if isinstance(idx, Iterable):
        # This is an order of magnitude faster that checking if Iterable
        if isinstance(idx, (int, slice, np.int32, np.int64)):
            return self._atoms[idx]
        return self.iter_from_idxs(idx)

    def iter_from_idxs(self, idxs: Iterable[int]) -> Generator[BoundAtom, None, None]:
        for i in idxs:
            yield self[i]

    #################################
    #####        Hashing        #####
    #################################

    @cached_property
    def fingerprint(self) -> str:
        return hash_System_v2(self).hexdigest()

    def hash_data(self, use_fast=True) -> FrozenSet:
        """Returns data for hasing the system

        # TODO: Improve performance. The hash does not need to be perfect
                for in-python
                usage. It should account for COM shifts though
        """
        # Calculate atom hash data all at once

        if use_fast:
            # r_data = self.r_matrix - self.r_matrix.mean(axis=0)
            r_data = self.r_matrix / R_TOLORANCE
            r_data = r_data.astype(int)
            r_data[:, 1] <<= 20
            r_data[:, 2] <<= 40
            r_hash = np.bitwise_xor.reduce(r_data, axis=1)

            role_data = np.fromiter(
                (role_to_int(a._role) for a in self._atoms), dtype=int, count=len(self)
            )

            return frozenset(role_data ^ r_hash)
        # NOTE: Use this as the reference implementation if the data schema changes
        #       This is slower but leans on low-level set data
        else:
            return frozenset((a.hash_data(r_offset=-self.COM) for a in self))

    @cached_property
    def _hash_val_prop(self) -> int:
        """Cached property version of `hash_data`

        Used to make subsequent hashes more efficient... Hashing still takes too long :/
        """
        return self.hash_data().__hash__()

    def __hash__(self) -> int:
        return self._hash_val_prop

    def __eq__(self, other_sys: Any) -> bool:
        return self.eq(other_sys, bound_join)

    def eq(
        self, other_sys: Any, join_fn: Callable[[BoundAtom, BoundAtom], bool]
    ) -> bool:
        # Allows anything that is a system to be considered equal
        if self is other_sys:
            return True
        if not isinstance(other_sys, System):
            return False
        if self.size != other_sys.size:
            return False

        # Check the unit cell
        if self.unit_cell is not None:
            if other_sys.unit_cell is not None:
                if not np.allclose(
                    self.unit_cell, other_sys.unit_cell, atol=R_TOLORANCE
                ):
                    return False
            else:  # One has a unit cell, one does not
                return False

        # Quick check for equality
        if self is other_sys:
            return True

        return all(
            map(
                lambda a: join_fn(a[0], a[1]),
                zip(self._canonical_atoms, other_sys._canonical_atoms),
            )
        )

    def eq_TI(self, other_sys: "System") -> bool:
        """Translationally invarient equality"""
        if np.allclose(self.COM, other_sys.COM, atol=R_TOLORANCE):
            return self == other_sys
        else:  # This is fairly expensive
            return self.eq(other_sys, bound_COM_join)

    @property
    def name(self) -> str:
        return "sys-" + self.fingerprint[0:8]

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        if self._saved:
            return f'{class_name}(formula="{self.chemical_formula()}", name="{self.name}, _saved="{self._saved}")'
        else:
            return (
                f'{class_name}(formula="{self.chemical_formula()}", name="{self.name}")'
            )

    #################################
    #####   MATRIX  ROPERTIES   #####
    #################################

    @cached_property
    def r_matrix(self) -> NPf64:
        """Matrix of atomic coordinates."""
        return np.array([a.r for a in self])

    @cached_property
    def kdtree(self) -> KDTree:
        if self.unit_cell is None:
            return KDTree(self.r_matrix)
        else:
            return KDTree(self.r_matrix % self.unit_cell, boxsize=self.unit_cell)

    @cached_property
    def masses(self) -> NPf64:
        """Matrix of masses. Non-physical atoms are m=0"""
        return np.array([a.mass for a in self]).reshape((-1, 1))

    @cached_property
    def mass(self) -> float:
        return self.masses.sum()

    @cached_property
    def charges(self) -> NPf64:
        """Matrix of assigned charges. This is not the same as partial charges"""
        return np.array([a.charge for a in self]).reshape((-1, 1))

    @cached_property
    def charge(self) -> int:
        """
        A good mechanism for calculating this has not yet been
        determine so we are assuming all fragments are neutral
        This can be overwritten at a per-implementation level
        """
        return self.charges.sum()

    @cached_property
    def electrons(self) -> npt.NDArray[np.int64]:
        """Number of electrons per atom"""
        electrons = np.zeros((self.size, 1), np.int64)
        for num, a in zip(electrons, self):
            if a.is_physical:
                num[:] = a.electrons
        return electrons

    @cached_property
    def multiplicity(self) -> int:
        """
        As with change, there is not general concept for how to set
        this although input is always welcome

        TODO: It will be important for this to be set manually. Caching
              for this property highly encouraged
        """
        return 1 if self.electrons.sum() % 2 == 0 else 2

    @cached_property
    def Z_matrix(self) -> npt.NDArray[np.uint16]:
        """Atomic number matrix"""
        return np.vstack([a.Z for a in self], dtype=np.uint16)

    @cached_property
    def COM(self) -> NPf64:
        COM = (self.r_matrix.T @ self.masses).reshape((3,))
        COM /= self.mass
        return COM

    @cached_property
    def nuclear_repulsion_energy(self) -> float:
        NRE = 0.0
        for a1, a2 in combinations(self, 2):
            if a1.is_physical and a2.is_physical:
                NRE += a1.Z * a2.Z / np.linalg.norm(a1.r - a2.r)
        return NRE / ANGSTROM_TO_BOHR

    @cached_property
    def moment_of_inertia_tensor(self) -> NPf64:
        I = np.zeros((3, 3))
        r_COM = self.r_matrix - self.COM
        r_COM_2 = r_COM**2

        # Diagonal elements
        I[0, 0] = np.sum(self.masses * (r_COM_2[:, 1] + r_COM_2[:, 2]))
        I[1, 1] = np.sum(self.masses * (r_COM_2[:, 0] + r_COM_2[:, 2]))
        I[2, 2] = np.sum(self.masses * (r_COM_2[:, 0] + r_COM_2[:, 1]))

        # Off diagonal elements
        I[0, 1] = I[1, 0] = -np.sum(self.masses * r_COM[:, 0] * r_COM[:, 1])
        I[0, 2] = I[2, 0] = -np.sum(self.masses * r_COM[:, 0] * r_COM[:, 2])
        I[1, 2] = I[2, 1] = -np.sum(self.masses * r_COM[:, 1] * r_COM[:, 2])

        return I

    def chemical_formula(self) -> str:
        # Give chemical formula
        counts = {}
        for a in sorted(self, key=lambda a: a.Z):
            if not a.is_physical:
                continue
            try:
                counts[a.t] += 1
            except KeyError:
                counts[a.t] = 1
        formula = ""
        for k, v in counts.items():
            if v == 1:
                formula += k
            else:
                formula += k + str(v)
        return formula

    @cached_property
    def inertial_coords(self) -> NPf64:
        I = self.moment_of_inertia_tensor
        e_val, e_vec = np.linalg.eig(I)

        # Sort eigenvalues. Largest -> Smallest = Z, Y, X
        sort_idx = np.argsort(e_val)

        # Rotate along x, y to align z then rotate along z
        rot_mat = e_vec[:, sort_idx]
        r_COM = self.r_matrix - self.COM
        return r_COM @ rot_mat

    def summarize(self, padding=2, level=0, with_atoms=True) -> str:
        if hasattr(self, "name"):
            rec_str = ind(padding, level, f"System {self.name}:\n")
        else:
            rec_str = ind(padding, level, "System:\n")

        level += 1
        if hasattr(self, "created"):
            rec_str += ind(
                padding,
                level,
                f"Created: {self.created.isoformat(timespec='minutes')}\n",
            )
        rec_str += ind(padding, level, f"Fingerprint: {self.fingerprint}\n")

        if self._saved:
            rec_str += ind(padding, level, f"Database ID: {self._saved}\n")
        rec_str += ind(padding, level, f"Chemical Formula: {self.chemical_formula()}\n")
        rec_str += ind(padding, level, f"Number of Atoms: {len(self)}\n")

        if self.unit_cell is not None:
            rec_str += ind(padding, level, f"Unit Cell: {self.unit_cell}\n")
        rec_str += ind(padding, level, f"Charge: {self.charge}\n")
        rec_str += ind(padding, level, f"Multiplicity: {self.multiplicity}\n")
        rec_str += ind(padding, level, f"Mass: {self.mass: .8f} amu\n")

        if hasattr(self, "meta") and self.meta:
            rec_str += summarize("Meta", self.meta, padding=padding, level=level + 1)

        if with_atoms:
            rec_str += ind(padding, level, "Atoms:\n")

            if self.unit_cell is None:
                header = (
                    "{0:<4s} {1:>13s} {2:>13s} {3:>13s} {4:4s} {5:4s} {6}\n".format(
                        "T", "X", "Y", "Z", "CHRG", "ROLE", "META"
                    )
                )
                rec_str += ind(padding, level + 1, header)
                for a in self:
                    rec_str += ind(
                        padding,
                        level + 1,
                        f"{a.t:<4s} {a.r[0]:> 13.6f} {a.r[1]:> 13.6f} {a.r[2]:> 13.6f} {a.charge:> 4d} {role_to_str(a.role):<4s} {a.meta}\n",
                    )
            else:
                header = "{0:<4s} {1:>13s} {2:>13s} {3:>13s} {4:>8s} {5:4s} {6:4s} {7}\n".format(
                    "T", "X", "Y", "Z", "CELL", "CHRG", "ROLE", "META"
                )
                rec_str += ind(padding, level + 1, header)
                for a in self:
                    cell = ",".join((str(i) for i in a.cell))
                    rec_str += ind(
                        padding,
                        level + 1,
                        f"{a.t:<4s} {a.r[0]:> 13.6f} {a.r[1]:> 13.6f} {a.r[2]:> 13.6f} {cell:>8s} {a.charge:> 4d} {role_to_str(a.role):<4s} {a.meta}\n",
                    )
        return rec_str


def merge(*systems: System) -> System:
    """
    Combines systems into a single system preventing duplicate atoms
    """
    # Empty system based on first unit cell
    new_system = System([], unit_cell=systems[0].unit_cell)

    _supersystem = None
    same_supersystem = True
    for sys in systems:
        if new_system.unit_cell is None:
            if sys.unit_cell is not None:
                raise ValueError("Cannot merge a periodic system with a cluster")
        elif new_system.unit_cell is not None and not np.allclose(
            new_system.unit_cell, sys.unit_cell, atol=R_TOLORANCE
        ):
            raise ValueError("Cannot merge two systems with different unit cells")

        if _supersystem is None:
            _supersystem = sys.supersystem
        elif _supersystem != sys.supersystem:
            same_supersystem = False

        # Allow overlapping systems
        new_system.add_atoms(*(a for a in sys if a not in new_system))

    if _supersystem is not None and same_supersystem:
        new_system.supersystem = _supersystem

    return new_system


def subsystem_merge(*systems: System, mods: List[Callable] | None =None, supersystem: System | None = None) -> System:
    """
    Combines systems into a single system only including atoms in a common superystem

    An optional mods parameter can be passed to facilitate subsystem modification
    """
    idxs: Set[int] = set()
    if supersystem is None:
        supersystem = systems[0].supersystem
        if supersystem is None: # Check that this is a valid assignment
            raise ValueError("Systems must have supersystem data.")
        if not all((supersystem == s.supersystem for s in systems)):
            raise ValueError("All systems must have a a supersystem in common.")

    for system in systems:
        # Join with parent. Does not account proxies.
        # All role information is ignored!
        idxs.update((i for i, j in supersystem.join_map(system)))

    return supersystem.subsystem(idxs, mods=mods)

class NamedSystem(System):
    _name: str
    created: datetime
    meta: Dict[str, Any]

    def __init__(
        self,
        atoms: Iterable[AbstractAtom],
        name: Optional[str] = None,  # Make this optional to allow
        unit_cell: Optional[NPf64] = None,
        supersystem: Optional["System"] = None,
        created: Optional[datetime] = None,
        meta: Optional[Dict[str, Any]] = None,
        _saved: int = 0,
    ):
        super().__init__(atoms, unit_cell, supersystem, _saved=_saved)
        self.name = name.strip() if name else ""
        self.created = datetime.now() if created is None else created
        self.meta = {} if meta is None else meta

        # Reorder system to match the stored metatdata
        order = self.meta.get("order", None)
        if order:
            self.reorder(order)
        else:
            idxs = np.argsort(self._atoms)  # type: ignore --> This does work...
            _order = [0] * len(idxs)
            for i, j in enumerate(idxs):
                _order[j] = i
            self.meta["order"] = _order

        # Offset from canonical version of the system
        offset = self.meta.get("offset", None)
        if offset:
            o = np.array(offset)
            for a in self:
                a._atom.r += o

        # Things which probably should go meta:
        #  - source_path
        #  - content_hash
        #  - note

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, val: str) -> None:
        self._name = val

    def bind_atom(
        self, a: AbstractAtom, role: AtomRole | None = None, cell: NPi32 | None = None
    ) -> BoundAtom:
        """Normalizes any Atom-Like type into a BoundAtom"""
        if isinstance(a, Atom):
            new_a = deepcopy(a)
            new_a._saved = 0
            return BoundAtom(new_a, self, role, cell)
        elif isinstance(a, BoundAtom):
            role = a._role if role is None else role
            cell = a._cell if cell is None else cell
            new_a = deepcopy(a._atom)
            new_a._saved = 0
            return BoundAtom(new_a, self, role, cell)

    @classmethod
    def from_system(cls, sys: System, name: str, meta: Dict[str, Any]) -> "NamedSystem":
        return cls(
            sys,
            name=name,  # Make this optional to allow
            unit_cell=sys.unit_cell,
            supersystem=sys.supersystem,
            meta=meta,
            _saved=sys._saved,
        )


class UniqueSystemDict(MutableMapping):
    def __init__(self) -> None:
        super().__init__()
        self.data: Dict[str, Any] = {}
        self.systems: Dict[str, System] = {}

    def __getitem__(self, __key: System) -> Any:
        return self.data[__key.fingerprint]

    def __setitem__(self, __key: System, __value: Any) -> None:
        self.data[__key.fingerprint] = __value
        self.systems[__key.fingerprint] = __key

    def __delitem__(self, __key: System) -> None:
        del self.data[__key.fingerprint]
        del self.systems[__key.fingerprint]

    def __iter__(self) -> Iterator:
        return self.systems.values()

    def __len__(self) -> int:
        return len(self.data)


class UniqueSystemSet(MutableSet):
    def __init__(self, values: Iterable[System]) -> None:
        super().__init__()
        self.systems: Dict[str, System] = {}
        for v in values:
            self.systems[v.fingerprint] = v

    def __contains__(self, x: System) -> bool:
        return x.fingerprint in self.systems

    def __iter__(self) -> Iterator:
        return iter(self.systems.values())

    def __len__(self) -> int:
        return len(self.systems)

    def add(self, value: System) -> None:
        self.systems[value.fingerprint] = value

    def discard(self, value: System) -> None:
        del self.systems[value.fingerprint]


class SystemKey(FrozenSet[int]):
    @classmethod
    def from_system(cls, sys: System):
        key = cls((a._saved for a in sys))
        if len(key) != sys.size:
            raise ValueError(
                "len(key) ~= system.size. Most likely the atoms have not been saved yet."
            )
        return key
