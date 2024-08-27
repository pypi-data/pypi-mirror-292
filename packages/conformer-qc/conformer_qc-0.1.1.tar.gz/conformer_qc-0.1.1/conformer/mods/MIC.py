#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from itertools import combinations

import networkx as nx
import numpy as np

from conformer import spatial
from conformer.spatial import idx
from conformer.systems import System, SystemKey, is_join, unbound_join
from conformer.util import supersystem_cache
from conformer_core.stages import Stage, StageOptions


def valid_MIC_system(sys: System, group_mask: np.ndarray = None) -> bool:
    # Aperiodic systems always return true
    if sys.unit_cell is None:
        return True

    # This version is valid (validate using code below)
    group_mask, group_COMs = get_group_COMs(sys, group_mask=group_mask)
    return np.all(np.ptp(group_COMs, axis=0) / sys.unit_cell < 0.5)

    cell = sys.unit_cell

    # This is not optimized! Probably just run the last line (assert)
    _size = group_COMs.shape[0]  # rows
    dm = np.zeros((_size**2 - _size) // 2, dtype=np.float64)
    dm_PBC = np.zeros((_size**2 - _size) // 2, dtype=np.float64)

    # Distance based answer
    for i, j in combinations(range(_size), 2):
        dm[idx(_size, i, j)] = np.linalg.norm(group_COMs[i, :] - group_COMs[j, :])

        # Do PBC
        v = group_COMs[i, :] - group_COMs[j, :]
        v %= cell
        v -= cell * (v > cell * 0.5)
        dm_PBC[idx(_size, i, j)] = np.linalg.norm(v)

    # Brute force answer
    systems = []
    for r in group_COMs:
        systems.append(MIC_wrap(sys, wrap_point=r, group_mask=group_mask))
    brute_answer = all((_s1 == _s2 for _s1, _s2 in combinations(systems, 2)))

    # Box answer
    box_answer = np.all(np.ptp(group_COMs, axis=0) / sys.unit_cell < 0.5)
    pairwise = np.allclose(dm, dm_PBC, 1e-8)

    if box_answer != pairwise or brute_answer != pairwise:
        print("PAIR:", pairwise)
        # if not pairwise:
        #     print(dm - dm_PBC)

        print("BRUTE:", brute_answer)
        # if not brute_answer:
        #     for i, s in enumerate(systems):
        #         with open(f"{i}.xyz", "w") as f:
        #             print(s.size, file=f)
        #             print(s.name, file=f)
        #             for a in s:
        #                 r = ' '.join((str(r) for r in a.r))
        #                 print(f"{a.t} {r}", file=f)
        #         print(s.canonize().summarize())

        print("BOX:", box_answer)
        # if not box_answer:
        #     print(np.ptp(group_COMs, axis=0) / sys.unit_cell)
        print()
    return pairwise


@supersystem_cache
def mk_group_mask(sys: System, scale: float = 1.1):
    bonding_graph = spatial.bonding_graph(sys, scale)

    group_mask = np.zeros(len(sys), dtype=np.uint16)
    for i, atoms in enumerate(nx.connected_components(bonding_graph)):
        map = sys.join_map(atoms, is_join)
        group_mask[[j for j, _k in map]] = i
    return group_mask


@mk_group_mask.derive
def derive_group_mask(
    supersystem: System, group_mask: np.ndarray, system: System, scale=1.1
):
    # If the atom has another role, we don't care!
    _map = supersystem.join_map(system, join_fn=unbound_join)
    _map.sort(key=lambda m: m[1])
    map = [m[0] for m in _map]

    # NOTE: this might won't work for certain mods
    # I'm thinking caps. It might leave those behind
    return group_mask[map]


def get_group_COMs(
    sys: System,
    group_mask: np.ndarray | None = None,
):
    if group_mask is None:
        group_mask = mk_group_mask(sys)

    # Renumber groups to be between 0-(n-1)
    groups = np.unique(group_mask)
    for i, g in enumerate(groups):
        group_mask[group_mask == g] = i
        groups[i] = i

    # Calculate group centers of mass
    n_groups = len(groups)

    # Get the COM for ghost atoms too!
    masses = np.array([a._atom.mass for a in sys]).reshape((-1, 1))

    mw_coords = np.multiply(masses, sys.r_matrix)
    group_COMs = np.zeros((n_groups, 3), np.float64)
    for g in groups:
        mask = group_mask == g
        group_COMs[g] = np.sum(mw_coords[mask, :], axis=0) / sum(masses[mask])
    return group_mask, group_COMs


def MIC_wrap(
    sys: System,
    wrap_point: np.ndarray | None = None,
    group_mask: np.ndarray | None = None,
) -> System:
    cell = sys.unit_cell
    group_mask, group_COMs = get_group_COMs(sys, group_mask)

    if wrap_point is None:
        wrap_point = group_COMs[0, :]  # Wrap on first group
    wrap_point = wrap_point - 0.5 * cell

    # This is tedious but will it work?
    # Was having issues with negative numbers. Let's hope this helps
    rel_coord = group_COMs - wrap_point
    shifts = (-(rel_coord // cell)).astype(np.int32)

    new_sys = sys.copy()
    for a, cell_shift in zip(new_sys, shifts[group_mask, :]):
        # Avoid the cache with _cell
        a._cell = a._cell + cell_shift
    new_sys._reset_cache()
    return new_sys


class MICSystemMod(Stage):
    class Options(StageOptions):
        scale: float = 1.1

    opts: Options

    def __call__(self, supersystem: System, key: SystemKey, system: System) -> System:
        if supersystem.unit_cell is None:
            raise Exception(
                f"{self.__class__.__name__} may only be used with periodic systems."
            )
        return MIC_wrap(system)
