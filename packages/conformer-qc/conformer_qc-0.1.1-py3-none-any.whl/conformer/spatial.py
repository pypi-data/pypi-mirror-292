#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from collections.abc import Mapping
from itertools import chain, combinations, product
from typing import Callable, Dict, Iterable, Iterator, List, Tuple

import networkx as nx
import numpy as np
import numpy.typing as npt
from scipy.spatial import Delaunay
from scipy.spatial.distance import pdist

from conformer.systems import Atom, BoundAtom, System, merge
from conformer.util import supersystem_cache

MAX_VALUE = 1e12
RAD_TO_DEGREES = 180 / np.pi

#############################################################################
###     CORE METHODS
#############################################################################


def idx(m: int, i: int, j: int) -> int:
    # See scipy pdist documentation
    if i > j:
        i, j = j, i  # Swap if needed
    return m * i + j - ((i + 2) * (i + 1)) // 2


def dist_matrix(n: int) -> npt.NDArray[np.float64]:
    """Distance matrix. See scipy.spatial.distance.pdist docs

    Includes pair-wise elements excluding the diagonal (all 0 by definition).
    using the `idx` method to access elements.
    """
    return np.zeros((n**2 - n) // 2, dtype=np.float64)


def MIC_norm(
    u: npt.NDArray[np.float64], r1: npt.NDArray[np.float64], r2: npt.NDArray[np.float64]
) -> float:
    """Calculate the norm between two vectors using the minimal image convention"""
    v = r1 - r2
    v %= u
    v -= u * (v > u * 0.5)

    return np.linalg.norm(v)


def MIC_pdist(
    u: npt.NDArray[np.float64], r: npt.NDArray[np.float64]
) -> npt.NDArray[np.float64]:
    """MIC implementation of SciPy's pdist method"""

    # Thanks to https://carlostgameiro.medium.com/fast-pairwise-combinations-in-numpy-c29b977c33e2
    comb_idx = np.stack(np.triu_indices(r.shape[0], k=1), axis=-1)

    v = r[comb_idx[:, 0], :] - r[comb_idx[:, 1], :]
    v %= u
    v -= u * (v > u * 0.5)

    return np.linalg.norm(v, axis=1)


#############################################################################
###     DISTANCE METRICS
#############################################################################


def distance(a_i: Atom, a_j: Atom) -> float:
    """Return distance between two atoms.

    if the entire distance matrix is required use distance_matrix or KDTree
    """
    # TODO: Give answer for periodic systems?
    return np.linalg.norm(a_j.r - a_i.r)


def vecotrized_distance(system: System) -> npt.NDArray[np.float64]:
    return pdist(system.r_matrix)


def MIC_distance(a_i: BoundAtom, a_j: BoundAtom) -> float:
    assert a_i.system is a_j.system
    if a_j.system.unit_cell is None:
        return distance(a_i, a_j)
    return MIC_norm(a_i.system.unit_cell, a_i.r, a_j.r)


def vecotrized_MIC_distance(system: System) -> npt.NDArray[np.float64]:
    if system.unit_cell is None:
        return vecotrized_distance(system)

    return MIC_pdist(system.unit_cell, system.r_matrix)

    # TESTING CODE!
    # M = dist_matrix(system.size)
    # for i, (a1, a2) in enumerate(combinations(system, 2)):
    #     M[i] = MIC_distance(a1, a2)
    # np.testing.assert_allclose(M, np.linalg.norm(v, axis=1))


def system_COM_distance(sys1: System, sys2: System) -> float:
    """Distance between systems centers of mass"""
    return np.linalg.norm(sys1.COM - sys2.COM)


def vectorized_system_COM_distance(
    supersystem: System, systems=List[System]
) -> npt.NDArray[np.float64]:
    r = np.stack([s.COM for s in systems])
    return pdist(r)


def system_MIC_COM_distance(sys1: System, sys2: System) -> float:
    """Distance between systems centers of mass with minimal image convention"""
    if sys1.unit_cell is None and sys2.unit_cell is None:
        return system_COM_distance(sys1, sys2)

    return MIC_norm(sys1.unit_cell, sys1.COM, sys2.COM)


def vectorized_system_MIC_COM_distance(
    supersystem: System, systems=List[System]
) -> npt.NDArray[np.float64]:
    if supersystem.unit_cell is None:
        return vectorized_system_COM_distance(supersystem, systems)

    r = np.stack([s.COM for s in systems])
    return MIC_pdist(supersystem.unit_cell, r)


def system_CA_distance(sys1: System, sys2: System) -> float:
    """Closest approach distance between two systems"""
    # TODO: Add some caching for parent system....
    if sys1.supersystem == sys2.supersystem:
        dm = atom_distance_matrix(sys1.supersystem, distance)
    else:
        dm = atom_distance_matrix(merge(sys1, sys2), distance)

    return min((dm[a1, a2] for a1, a2 in product(sys1, sys2)))


def vectorized_system_CA_distance(
    supersystem: System, systems=List[System]
) -> npt.NDArray[np.float64]:
    adm = atom_distance_matrix(supersystem, distance)
    lookups = [  # Prevents expensive equality checks
        [adm.idx(a) for a in s] for s in systems
    ]

    M = dist_matrix(len(systems))
    for i, (l1, l2) in combinations(lookups, 2):
        M[i] = min((adm[a1, a2] for a1, a2 in product(l1, l2)))
    return M


def system_MIC_CA_distance(sys1: System, sys2: System) -> float:
    """Closest approach distance between two systems using the minimal image convention"""
    if sys1.supersystem == sys2.supersystem:
        dm = atom_distance_matrix(sys1.supersystem, MIC_distance)
    else:
        dm = atom_distance_matrix(merge(sys1, sys2), MIC_distance)
    return min((dm[a1, a2] for a1, a2 in product(sys1, sys2)))


def vectorized_system_MIC_CA_distance(
    supersystem: System, systems=List[System]
) -> npt.NDArray[np.float64]:
    adm = atom_distance_matrix(supersystem, MIC_distance)
    lookups = [  # Prevents expensive equality checks
        [adm.atom_to_idx[a] for a in s] for s in systems
    ]

    M = dist_matrix(len(systems))
    for i, (l1, l2) in enumerate(combinations(lookups, 2)):
        M[i] = min((adm[a1, a2] for a1, a2 in product(l1, l2)))
    return M


#############################################################################
###     ADJUSTED ATOMIC RADIUS
#############################################################################


def bonding_radius(a: Atom, fudge_factor: float = 0.65) -> float:
    """Adjusts an atomic radius for bond determination.

    Unfortunatly there is no good answer for how to do this cleanly. Data from emperical
    sources can be used or we could develop an emperical model. Currently I'm using a
    fudge factor of 0.65**dn where dn is an integer change in the max n quantum number

    Eventually I should re-key data from R. D. Shannon, “Revised effective ionic radii and systematic studies of interatomic distances in halides and chalcogenides,” Acta Crystallographica 32, no. 5 (1976): 751–767
    """
    if isinstance(a, BoundAtom):
        a = a._atom  # Ingnore role information

    # Default case
    if a.charge == 0:
        return a.covalent_radius

    if a.valence_electrons >= a.max_valence:
        # Gained electrons. Will be bigger
        return a.covalent_radius / fudge_factor
    elif a.valence_electrons <= 0:
        # Lost electrons. Will be smaller
        return a.covalent_radius * fudge_factor
    else:
        return a.covalent_radius


#############################################################################
###     GEOMETRIC METHODS
#############################################################################


def unit_vector(a_i: Atom, a_j: Atom) -> np.ndarray:
    v = a_i.r - a_j.r
    return (v) / np.linalg.norm(v)


def angle(a_i: Atom, a_j: Atom, a_k: Atom, use_degrees=False) -> float:
    e_ji = unit_vector(a_j, a_i)
    e_jk = unit_vector(a_j, a_k)

    if use_degrees:
        return np.arccos(np.dot(e_ji, e_jk)) * RAD_TO_DEGREES
    else:
        return np.arccos(np.dot(e_ji, e_jk))


def torsion_angle(
    a_i: Atom, a_j: Atom, a_k: Atom, a_l: Atom, use_degrees=False
) -> float:
    e_ij = unit_vector(a_i, a_j)
    e_jk = unit_vector(a_j, a_k)
    e_kl = unit_vector(a_k, a_l)

    theta_ijk = angle(a_i, a_j, a_k)
    theta_jkl = angle(a_j, a_k, a_l)

    e_ij_X_e_jk = np.cross(e_ij, e_jk)
    e_jk_X_e_kl = np.cross(e_jk, e_kl)

    # Calculate sin term denominator
    sin_ijk_sin_jkl = np.sin(theta_ijk) * np.sin(theta_jkl)

    # Threshold to prevent unrelistic values
    if sin_ijk_sin_jkl > 1e-12:
        dot = np.dot(e_ij_X_e_jk, e_jk_X_e_kl)
        cos_angle = dot / sin_ijk_sin_jkl

        # Mild error checking:
        if cos_angle > 1.0:
            cos_angle = 1.0
        if cos_angle < -1.0:
            cos_angle = -1.0

        _angle = np.arccos(cos_angle)

        # Convert
        if use_degrees:
            return _angle * RAD_TO_DEGREES
        else:
            return _angle
    else:
        return np.nan


#############################################################################
###     DISTANCE MATRIX TYPES
#############################################################################


class AtomDistanceMatrix(Mapping):
    data: npt.NDArray[np.float64]
    system: System
    size: int
    metric: Callable[[Atom, Atom], float]
    atom_to_idx: Dict[Atom, int]

    def __init__(
        self,
        system: System,
        metric: Callable[[Atom, Atom], float],
        vectorized_metric: Callable[[System, List[System]], npt.NDArray[np.float64]]
        | None = None,
    ) -> None:
        self.system = system
        self.metric = metric
        self.size = system.size

        # Minimum pair-wise size
        self.atom_to_idx = {a: i for i, a in enumerate(system)}
        if vectorized_metric:
            self.data = vectorized_metric(self.system)
        else:
            self.data = dist_matrix(self.size)
            self.build()

    def __getitem__(self, key: Tuple[Atom | int, Atom | int]) -> float:
        return self.data[self.idx(*key)]

    def __iter__(self) -> Iterator:
        # What make sense? The keys are not ideal
        for a1, a2 in combinations(self.system, 2):
            yield a1, a2, self[a1, a2]

    def __len__(self) -> int:
        return self.data.__len__()

    def idx(self, a1: Atom | int, a2: Atom | int) -> int:
        """Converts Atoms to DM matrix index
        Matrix indecies are accepted too!
        """

        return idx(
            self.size,
            a1 if isinstance(a1, int) else self.atom_to_idx[a1],
            a2 if isinstance(a2, int) else self.atom_to_idx[a2],
        )

    def build(self) -> None:
        for a1, a2 in combinations(self.system, 2):
            self.data[self.idx(a1, a2)] = self.metric(a1, a2)


class SystemDistanceMatrix(Mapping):
    data: npt.NDArray[np.float64]
    supersystem: System
    size: int
    metric: Callable[[System, System], float]
    system_to_idx: Dict[System, int]

    def __init__(
        self,
        systems: Iterable[System],
        metric: Callable[[Atom, Atom], float],
        supersystem: System | None = None,
        vectorized_metric: Callable[[System, List[System]], npt.NDArray[np.float64]]
        | None = None,
    ) -> None:
        self.systems = list(systems)
        if supersystem:
            self.supersystem = supersystem
        else:
            self.supersystem = merge(*self.systems)
        self.metric = metric
        self.size = len(self.systems)

        # Minimum pair-wise size
        self.system_to_idx = {s: i for i, s in enumerate(systems)}
        if vectorized_metric:
            self.data = vectorized_metric(self.supersystem, self.systems)
        else:
            self.data = dist_matrix(self.size)
            self.build()

    def __getitem__(self, key: Tuple[System | int, System | int]) -> float:
        return self.data[self.idx(*key)]

    def __iter__(self) -> Iterator:
        # What make sense? The keys are not ideal
        for s1, s2 in combinations(self.systems, 2):
            yield s1, s2, self[s1, s2]

    def __len__(self) -> int:
        return self.data.__len__()

    def idx(self, s1: System | int, s2: System | int) -> int:
        """Converts Atoms to DM matrix index
        Matrix indecies are accepted too!
        """
        return idx(
            self.size,
            s1 if isinstance(s1, int) else self.system_to_idx[s1],
            s2 if isinstance(s2, int) else self.system_to_idx[s2],
        )

    def build(self) -> None:
        # TODO: Add parallel build for accessors
        for s1, s2 in combinations(self.systems, 2):
            self.data[self.idx(s1, s2)] = self.metric(s1, s2)


@supersystem_cache
def atom_distance_matrix(sys: System, metric: Callable) -> AtomDistanceMatrix:
    """Returns an atom-based distance matrix for a system"""
    if metric is distance:
        return AtomDistanceMatrix(sys, metric, vectorized_metric=vecotrized_distance)
    elif metric is MIC_distance:
        return AtomDistanceMatrix(
            sys, metric, vectorized_metric=vecotrized_MIC_distance
        )
    return AtomDistanceMatrix(sys, metric)


def system_distance_matrix(
    systems: Iterable[System], metric: Callable, supersystem: System | None = None
) -> SystemDistanceMatrix:
    """Returns distance matrix for a list of systems

    TODO: Add caching :)
          the main issue with caching is the list of systems is non-cachable
          (which is fine). Modded and unmodded systems are also indestinguishible
    """
    if metric is system_COM_distance:
        return SystemDistanceMatrix(
            systems,
            metric,
            supersystem=supersystem,
            vectorized_metric=vectorized_system_COM_distance,
        )
    elif metric is system_CA_distance:
        return SystemDistanceMatrix(
            systems,
            metric,
            supersystem=supersystem,
            vectorized_metric=vectorized_system_MIC_COM_distance,
        )
    elif metric is system_MIC_COM_distance:
        return SystemDistanceMatrix(
            systems,
            metric,
            supersystem=supersystem,
            vectorized_metric=vectorized_system_CA_distance,
        )
    elif metric is system_MIC_CA_distance:
        return SystemDistanceMatrix(
            systems,
            metric,
            supersystem=supersystem,
            vectorized_metric=vectorized_system_MIC_CA_distance,
        )

    return SystemDistanceMatrix(systems, metric, supersystem=supersystem)


#############################################################################
###     GRAPH METHODS
#############################################################################


# TODO: Re-enable caching once we handle the r parameter.
# @supersystem_cache
def primative_neighbor_graph(sys: System, r: float = 3.0) -> nx.Graph:
    """Returns primative connectivity graph for system

    Graph should be refined with additional post-processing
    """
    G = nx.Graph()
    G.add_nodes_from(sys)  # Make sure all atoms appear in tree
    G.add_edges_from(
        (sys[i], sys[j], {"r": MIC_distance(sys[i], sys[j])})
        for i, j in sys.kdtree.query_pairs(r)
    )
    return G


# @primative_neighbor_graph.derive
def derive_primative_neighbor_graph(
    supersystem: System, G: nx.Graph, sys: System, r: float
) -> nx.Graph:
    return G.subgraph(sys)


@supersystem_cache
def bonding_graph(sys: System, scale: float = 1.1) -> nx.Graph:
    search_r = 2 * max((bonding_radius(a) for a in sys)) * scale
    G = primative_neighbor_graph(sys, search_r)

    # Prune long bonds
    to_delete = []
    for u, v, d in G.edges(data=True):
        expected = (bonding_radius(u) + bonding_radius(v)) * scale

        if d["r"] > expected:
            to_delete.append((u, v))
    G.remove_edges_from(to_delete)
    return G


@bonding_graph.derive
def derive_bonding_graph(supersystem: System, G: nx.Graph, sys: System) -> nx.Graph:
    return G.subgraph(sys)


def covalent_components(system: System, scale: float | None = None) -> Iterable[System]:
    """Returns individual covalently connected systems as generator function"""
    G = bonding_graph(system, scale) if scale else bonding_graph(system)
    for comp in nx.connected_components(G):
        yield System(comp, unit_cell=system.unit_cell, supersystem=system)


def raw_Delaunay_graph(points: np.array) -> nx.Graph:
    """Returns the Delaunay graph for a collection of points"""
    tri = Delaunay(points)
    G = nx.Graph()
    G.add_edges_from(
        ((i, j) for (i, j) in chain(*(combinations(s, 2) for s in tri.simplices)))
    )

    return G


def Delaunay_graph(sys: System) -> nx.Graph:
    """Returns the Delaunay graph for the system"""
    tri = Delaunay(sys.r_matrix)

    G = nx.Graph()
    G.add_edges_from(
        (
            (sys[i], sys[j], {"r": distance(sys[i], sys[j])})
            for (i, j) in chain(*(combinations(s, 2) for s in tri.simplices))
        )
    )
    return G


#############################################################################
###     SPATIAL FILTERING
#############################################################################


def filter_r(dm: SystemDistanceMatrix, target: System, r: float) -> List[System]:
    """Returns all systems within a cutoff `r` of a target system for all
    systems in a distance matrix.
    """
    assert target in dm.systems
    included = []
    for sys in dm.systems:
        if sys == target:
            continue
        if dm[target, sys] < r:
            included.append(sys)
    included.sort(key=lambda s: dm[s, target])
    return included


def filter_n_closest(dm: SystemDistanceMatrix, target: System, n: int) -> List[System]:
    """Returns returns the closest `n` neighbors of a target system for all
    systems in a distance matrix
    """
    assert target in dm.systems
    others = [s for s in dm.systems if s != target]
    others.sort(key=lambda s: dm[s, target])
    return others[0:n]
