#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from conformer.common import GHOST_ATOM
from conformer.systems import System, SystemKey
from conformer_core.stages import Stage


class CounterpoiseSubsystemMod(Stage):
    def __call__(self, supersystem: System, key: SystemKey, system: System) -> System:
        # TODO: Distance threshold
        # TODO: Periodic
        # TODO: Handle proxys
        ghost_idxs = set(range(len(supersystem))).difference(key)
        system.add_atoms(*supersystem[ghost_idxs], role=GHOST_ATOM)
        return system
