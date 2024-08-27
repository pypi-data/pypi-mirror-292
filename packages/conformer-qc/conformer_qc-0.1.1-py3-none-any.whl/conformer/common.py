#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from collections import defaultdict
from copy import copy
from functools import lru_cache
from itertools import product
from typing import (
    Any,
    Dict,
    Final,
    FrozenSet,
    Generator,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)


###########################################################
#                      ATOM ROLES                         #
###########################################################
class AtomRole(NamedTuple):
    is_physical: bool = False
    has_basis_fns: bool = False
    is_point_charge: bool = False
    is_proxy: bool = False
    is_pinned: bool = False

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        attrs = [f + "=" + v.__repr__() for f, v in zip(self._fields, self) if v]
        return f"{class_name}({', '.join(attrs)})"


@lru_cache
def role_to_int(role: AtomRole) -> int:
    """Converts an AtomRole to a int representation
    Oddly enough this was becomming significant when hashing so the result is now cached"""
    int_rep = 0
    for i, f in enumerate(role):
        if f:
            int_rep |= 2**i
    return int_rep


@lru_cache
def role_to_bytes(role: AtomRole) -> bytes:
    return role_to_int(role).to_bytes(2, "little")


@lru_cache
def int_to_role(int_rep) -> AtomRole:
    # CUSTOM ATOM ROLE
    """Converts a bit representation to AtomRole by bit-anding the respective positions"""

    # TODO: Benchmark. It might be faster just to construct this loop instead
    #       of referencing a global variable
    if int_rep not in ROLE_CACHE:
        ROLE_CACHE[int_rep] = AtomRole(
            *(bool(int_rep & 2**i) for i in range(len(AtomRole._fields)))
        )
    return ROLE_CACHE[int_rep]


####### CONSTANT DEFINITIONS #######
ROLE_CACHE = {}

PHYSICAL_ATOM: Final[AtomRole] = AtomRole(is_physical=True)
ROLE_CACHE[role_to_int(PHYSICAL_ATOM)] = PHYSICAL_ATOM

CAPPING_ATOM: Final[AtomRole] = AtomRole(is_physical=True, is_proxy=True)
ROLE_CACHE[role_to_int(CAPPING_ATOM)] = CAPPING_ATOM

GHOST_ATOM: Final[AtomRole] = AtomRole(has_basis_fns=True)
ROLE_CACHE[role_to_int(GHOST_ATOM)] = GHOST_ATOM

POINT_CHARGE: Final[AtomRole] = AtomRole(is_point_charge=True)
ROLE_CACHE[role_to_int(POINT_CHARGE)] = POINT_CHARGE

DUMMY_ATOM: Final[AtomRole] = AtomRole()
ROLE_CACHE[role_to_int(DUMMY_ATOM)] = DUMMY_ATOM

PINNED_ATOM: Final[AtomRole] = AtomRole(is_physical=True, is_pinned=True)
ROLE_CACHE[role_to_int(PINNED_ATOM)] = PINNED_ATOM

ROLE_STRINGS = {
    None: "~",
    PHYSICAL_ATOM: "",
    CAPPING_ATOM: "C",
    GHOST_ATOM: "G",
    POINT_CHARGE: "P",
    DUMMY_ATOM: "D",
}


STRING_TO_ROLE = {v: k for k, v in ROLE_STRINGS.items()}
STRING_TO_ROLE.update(
    PHYSICAL=PHYSICAL_ATOM,
    CAPPING=CAPPING_ATOM,
    GHOST=GHOST_ATOM,
    POINT_CHARGE=POINT_CHARGE,
    DUMMY=DUMMY_ATOM,
    PINNED=PINNED_ATOM,
)


def role_to_str(role: AtomRole | None) -> str:
    try:
        return ROLE_STRINGS[role]
    except KeyError:
        return str(role_to_int(role))


def str_to_role(role_str: str) -> AtomRole:
    try:
        return STRING_TO_ROLE[role_str]
    except KeyError:
        pass # Handle parsing

    try:
        return int_to_role(int(role_str))
    except ValueError:
        raise AttributeError(f"Could not parse string '{role_str}' as role")


###########################################################
#                     INDEX MASKS                         #
###########################################################
class AtomMask(NamedTuple):
    idx: int
    role: Optional[AtomRole] = None  # If None, inherit from parent

    def str_digest(self) -> str:
        if self.role == PHYSICAL_ATOM:
            return f"{self.idx}"
        return f"{self.idx}/{role_to_str(self.role)}"

    @classmethod
    def from_str(cls, input: str) -> "AtomMask":
        parts = input.split("/")

        id = int(parts[0])
        if len(parts) == 2:
            role = str_to_role(parts[1])
        else:  # default
            role = PHYSICAL_ATOM

        return cls(id, role)


class CellIndex(Tuple[int, int, int]):
    def str_digest(self) -> str:
        return "(" + ",".join(str(i) for i in self) + ")"

    @classmethod
    def from_str(cls, input: str) -> "CellIndex":
        # Strip out parens
        _input = input[1:-1]
        parts = _input.split(",")
        return cls((int(p) for p in parts))

    def __add__(self, ci: Sequence | int) -> "CellIndex":
        # TODO: Handle np arrays
        if isinstance(ci, Sequence):
            return self.__class__((self[0] + ci[0], self[1] + ci[1], self[2] + ci[2]))
        if isinstance(ci, int):
            return self.__class__((self[0] + ci, self[1] + ci, self[2] + ci))
        raise NotImplementedError(
            f"Cannot add/subtract a {self.__class__.__name__} and {ci.__class__.__name__}."
        )

    def __radd__(self, ci: Sequence | int) -> "CellIndex":
        return self.__add__(ci)

    def __sub__(self, ci: "CellIndex") -> "CellIndex":
        if isinstance(ci, Sequence):
            return self.__class__((self[0] - ci[0], self[1] - ci[1], self[2] - ci[2]))
        if isinstance(ci, int):
            return self.__class__((self[0] - ci, self[1] - ci, self[2] - ci))

    def __rsub__(self, ci: "CellIndex") -> "CellIndex":
        if isinstance(ci, Sequence):
            return self.__class__((ci[0] - self[0], ci[1] - self[1], ci[2] - self[2]))
        if isinstance(ci, int):
            return self.__class__((ci - self[0], ci - self[1], ci - self[2]))

    # def __mul__(self, val: int) -> 'CellIndex':
    #     return self.__class__((self[0] * val, self[1] * val, self[2] * val))

    # def __rmul__(self, val: SupportsIndex) -> tuple[int, ...]:
    #     return super().__mul__(val)


class Mask:
    __slots__ = ("cells", "isminimized")
    cells: Dict[CellIndex, FrozenSet[AtomMask]]
    isminimized: bool

    def __init__(
        self,
        cells: Dict[CellIndex, FrozenSet[AtomMask]],
        minimize: bool = True,
    ):
        self.isminimized = minimize
        if minimize:
            self.cells = self._minimize(cells)
        else:
            self.cells = cells

    @classmethod
    def from_itr(cls, els: Iterable[int | Tuple], minimize: bool = True) -> "Mask":
        ooo = CellIndex((0, 0, 0))
        cells = defaultdict(default_factory=list) 
        for el in els:
            if isinstance(el, int):
                cells[ooo].append(AtomMask(el))
            else:
                cells[el[1]].append(AtomMask(el[0], el[2]))
        
        return cls({k: frozenset(v) for k, v in cells.items()}, minimize=minimize)
            

    @classmethod
    def _minimize(cls, cells: Dict[CellIndex, FrozenSet[AtomMask]]) -> None:
        """Minimize in place. Should only be called by the constructor"""
        min = cls._get_minima(cells)
        return {(k - min): v for k, v in cells.items()}

    @staticmethod
    def _get_minima(cells: Dict[CellIndex, FrozenSet[AtomMask]]) -> CellIndex:
        x_min = min((c[0] for c in cells.keys()))
        y_min = min((c[1] for c in cells.keys()))
        z_min = min((c[2] for c in cells.keys()))
        return CellIndex((x_min, y_min, z_min))

    def sorted_indexs(self) -> List[CellIndex]:
        return sorted(self.cells.keys())

    def str_digest(self) -> str:
        cell_digests = []
        for c in self.sorted_indexs():
            atoms_digest = ",".join([a.str_digest() for a in sorted(self.cells[c])])
            cell_digests.append(f"{c.str_digest()}:{atoms_digest}")

        return ";".join(cell_digests)

    @classmethod
    def from_str(cls, input: str, minimize=True) -> "Mask":
        parts = input.split(";")
        data = {}
        for c, a_data in (p.split(":") for p in parts):
            data[CellIndex.from_str(c)] = frozenset(
                (AtomMask.from_str(a) for a in a_data.split(","))
            )
        return cls(data, minimize=True)

    def union(self, *others: "Mask", minimize: bool = True) -> "Mask":
        d = copy(self.cells)
        for m in others:
            for k, v in m.items():
                try:
                    d[k] = d[k].union(v)
                except KeyError:
                    d[k] = v
        return self.__class__(d, minimize=minimize)

    def get_displacements(self: "Mask", b: "Mask") -> Set[CellIndex]:
        """Generates all unique displacements in the cell system."""
        return set(
            (b_c - a_c for a_c, b_c in product(self.cells.keys(), b.cells.keys()))
        )

    def intersection(self, m: "Mask") -> "Mask":
        if len(self.cells) != 1 and len(m.cells) != 1:
            raise ValueError(
                "Cannot performa simple intersection with multi-cell masks"
            )
        for i in self.intersections(m):
            return i

    @property
    def num_cells(self) -> int:
        return len(self.cells)

    @property
    def num_elements(self) -> int:
        return sum(len(i) for i in self.cells.items())

    def intersections(self, m: "Mask") -> Generator["Mask", None, None]:
        # m1 will be smaller than or equal to in length of m2
        if self.num_cells <= m.num_cells:
            m1 = self
            m2 = m
        else:
            m1 = m
            m2 = self

        for displacement in m1.get_displacements(m2):
            data = {}
            for c in m1.cells.keys():
                c_ = c + displacement
                try:
                    d = m1.cells[c].intersection(m2.cells[c_])
                    if d:  # Don't add empty sets
                        data[c_] = d
                except KeyError:
                    pass
            if data:
                yield self.__class__(data)

    def issubset(self, m: "Mask") -> bool:
        if self.num_cells > m.num_cells:
            return False

        for displacement in self.get_displacements(m):
            is_subset = True
            for c in self.cells.keys():
                c_ = c + displacement
                try:
                    if self.cells[c].issubset(m.cells[c_]):
                        continue
                    else:
                        is_subset = False
                        break
                except KeyError:
                    is_subset = False
                    break  # Try next displacement
            if is_subset:
                return True
        return False

    def issuperset(self, m: "Mask") -> bool:
        if self.num_cells < m.num_cells:
            return False

        for displacement in m.get_displacements(self):
            is_subset = True
            for c in m.cells.keys():
                c_ = c + displacement
                try:
                    if m.cells[c].issuperset(self.cells[c_]):
                        continue
                    else:
                        is_subset = False
                        break
                except KeyError:
                    is_subset = False
                    break
            if is_subset:
                return True
        return False

    def __len__(self) -> int:
        return self.cells.__len__

    def __eq__(self, m: Any) -> bool:
        if not isinstance(m, Mask):
            return False
        if m.isminimized != self.isminimized:
            raise AttributeError("Cannot compair minimized and unminimized mask")
        if len(self.cells) != len(m.cells):
            return False
        for k, _v in self.cells.items():
            if _v != m.cells[k]:
                return False
        return True

    def __hash__(self) -> int:
        # XOR should is order invarient so no need to sort
        # Should this be cached? It *should* not change
        return tuple(((i, self.cells[i]) for i in self.sorted_indexs())).__hash__()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.cells.__repr__()})"


Maskable = Union[Mask, Iterable[int]]


def mask(m: Maskable) -> Mask:
    """TODO: Add masking logic"""
    return sorted(m)
