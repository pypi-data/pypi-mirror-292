#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from typing import List

import numpy as np

from conformer.common import CAPPING_ATOM
from conformer.elements import get_covalent_radius
from conformer.spatial import bonding_graph, distance
from conformer.systems import Atom, BoundAtom, System, SystemKey
from conformer_core.stages import Stage, StageOptions


class HCapsMod(Stage):
    """R Capper

    TODO: Add math for capping

    Attributes:
        name (str): name of the mod
        note (str): human-readable note on this mod
        tolerance (float): fudge factor used when determining if a bond exists
        cutoff (float): maximum distance to search for capping atoms
        k (int): Number of nearest neighbor atoms to consider
        ignore_charged (bool): prevents capping of atoms that are charged (i.g. metal centers)
    """

    H_radius = get_covalent_radius("H")

    class Options(StageOptions):
        k: int = 8
        tolerance: float | None = None
        cutoff: float | None = None
        ignore_charged: float = False

    opts: Options

    def cap_position(
        self,
        inner_atom: BoundAtom,
        outer_atom: BoundAtom,
    ) -> np.array:
        """
        Calculates cap hydrogen position. See Equation ? in DOI:
        """
        # Calculate contraction relative to covalent radius
        shortening = (outer_atom.covalent_radius + self.H_radius) / (
            distance(inner_atom, outer_atom)
        )

        # Calculate position
        return inner_atom.r + shortening * (outer_atom.r - inner_atom.r)

    def __call__(self, supersystem: System, key: SystemKey, system: System) -> System:
        G = bonding_graph(supersystem)
        caps: List[Atom] = []

        for inner_a in system:
            if self.opts.ignore_charged and inner_a.charge != 0:
                continue
            for outer_a in G.neighbors(inner_a):
                if outer_a in system:  # Is there a faster way?
                    continue
                if not inner_a.is_physical or not outer_a.is_physical:
                    continue
                if self.opts.ignore_charged and outer_a.charge != 0:
                    continue

                # TODO: Validate with semi-periodic systems
                caps.append(
                    Atom(t="H", r=self.cap_position(inner_a, outer_a), charge=0)
                )
        system.add_atoms(*caps, role=CAPPING_ATOM)
        return system
