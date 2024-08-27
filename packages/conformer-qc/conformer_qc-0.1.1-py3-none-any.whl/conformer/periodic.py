#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Optional, Sequence, overload

import networkx as nx
import numpy as np
import numpy.typing as nt

from conformer.spatial import primative_neighbor_graph
from conformer_core.caching import cached_property

from .systems import Atom, System


class AmbigiousSystem(Exception):
    ...


@dataclass(slots=True)
class AtomImage(Atom):
    """Passthrough entity to a real atom"""

    _atom: Atom = field(default_factory=lambda: Atom("X", np.zeros(3)))
    _shift: nt.NDArray[np.int64] = field(default_factory=lambda: np.zeros(3))

    @property
    def _saved(self) -> int:
        return self._atom._saved


@dataclass
class PeriodicSystem(System):
    """Initialized to None because dataclasses"""

    cell: nt.NDArray[np.float64] = None  # Only support orthorhombic cells
    _system: Optional[System] = None  # Reference geometry

    atom_groups: nt.NDArray[np.int32] = None
    wrap_point: Optional[nt.NDArray[np.float64]] = None  # Defaults to center of cell
    _group_COMs: Optional[nt.NDArray[np.float64]] = None

    @cached_property
    def _wrapped_atoms(self) -> List[AtomImage]:
        # TODO: Cache some of these properties

        # Step 0: Get data from reference system
        # TODO: Cache some of this informatin?
        ref_coords = self._system.r_matrix

        # Step 1: Get COMs of groups
        if self._group_COMs is None:
            groups = np.unique(self.atom_groups)
            n_groups = len(groups)
            masses = self._system.masses
            mw_coord = np.multiply(masses, ref_coords)
            self._group_COMs = np.zeros((n_groups, 3), np.float64)
            for g in groups:
                mask = self.atom_groups == g
                self._group_COMs[g] = np.sum(mw_coord[mask, :], axis=0) / sum(
                    masses[mask]
                )

        # Wrap point is the center of the cell
        global_shift = (self.cell / 2 - self.wrap_point) % self.cell

        # Steph 2: Get offsets
        shifts = (self._group_COMs + global_shift) // self.cell - global_shift

        # Shift all atoms to world center
        coords = ref_coords - shifts[self.atom_groups, :]

        # All these allocations feel like a performance bottleneck waiting to happen...
        self._atoms = [
            AtomImage(t=a.t, r=r, role=a.role, charge=a.charge, meta=a.meta, _atom=a)
            for a, r in zip(self._atoms, coords)
        ]
        return self._atoms

    def recenter(self, wrap_point: nt.ArrayLike) -> List[AtomImage]:
        self.wrap_point = np.array(wrap_point, np.float64)
        self._reset_cache()

    @overload
    def __getitem__(self, idx: int) -> AtomImage:
        ...

    @overload
    def __getitem__(self, s: slice) -> Sequence[AtomImage]:
        ...

    def __getitem__(self, idx):
        return self._wrapped_atoms[idx]

    def __iter__(self) -> Iterator[AtomImage]:
        return self._wrapped_atoms.__iter__()

    def add_atoms(self, atoms: Iterable[Atom]) -> None:
        # Add atom to the reference system as our source of truth
        self._reset_cache()
        self._system._atoms += list(atoms)

    ### Custom Periodic constructors
    @classmethod
    def from_System(
        cls,
        sys: System,
        cell: nt.ArrayLike,
        wrap_point: Optional[nt.ArrayLike] = None,
        groups: Optional[nt.ArrayLike] = None,
    ) -> "PeriodicSystem":
        """Upconverts and existing system object into a periodic system

        Perhaps not the most efficient method but in an ideal world this will only
        have to be done once
        """
        # Check cell
        if not isinstance(cell, np.ndarray):
            cell = np.array(cell, np.float64)

        # Check wrapping
        if wrap_point:
            if not isinstance(wrap_point, np.ndarray):
                wrap_point = np.array(wrap_point)
        else:
            wrap_point = cell / 2  # The center of the cell

        # Check groups
        if groups:
            if not isinstance(groups, np.ndarray):
                groups = np.array(groups, np.int32)
        else:
            groups = cls._group_by_distance(sys)
        # groups.sort() # Makes subsysteming easier
        assert len(groups) == sys.size

        return cls(
            _system=sys,
            _atoms=sys._atoms,  # Temporary
            supersystem=sys.supersystem,
            supersystem_idxs=sys.supersystem_idxs,
            cell=cell,
            wrap_point=wrap_point,
            atom_groups=groups,
        )

    def subsystem(self, idxs: Iterable[int]) -> System:
        """
        Get a subsystem using the minimal image convention

        Raises:
            ValueError: If system is larger than 1/2 L for the cell
        """
        sys = self._system.subsystem(idxs)
        idxs = sys.supersystem_idxs

        # Groupes needs to be sequential so...
        _groups = self.atom_groups[idxs]
        groups = np.zeros(len(idxs), np.int32)
        for i, g in enumerate(np.unique(_groups)):
            groups[_groups == g] = i

        self._wrapped_atoms  # Create group_COMs
        group_COMs = self._group_COMs[idxs, :]
        psys = self.__class__(
            _system=sys,
            _atoms=sys._atoms,  # Temporary
            supersystem=self,
            supersystem_idxs=idxs,
            cell=self.cell,
            wrap_point=group_COMs[0, :],
            atom_groups=groups,
            _group_COMs=group_COMs,
        )

        if any(np.ptp(psys.r_matrix, axis=0) / psys.cell > 0.5):
            raise AmbigiousSystem("Subsystem is larger than 0.5 L and is ambigious.")

        return psys

    @staticmethod
    def _group_by_distance(sys: System, r=2.5, s=1.1):
        """Generates atom groups based on covalent radius cuttofs"""
        ng = primative_neighbor_graph(sys, r)
        to_delete = []
        for u, v, d in ng.edges(data=True):
            if d["r"] > s * (sys[u].covalent_radius + sys[v].covalent_radius):
                to_delete.append((u, v))

        ng.remove_edges_from(to_delete)

        groups = np.zeros(sys.size, int)
        for i, comp in enumerate(nx.connected_components(ng)):
            for j in comp:
                groups[j] = i
        return groups
