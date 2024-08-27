#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from typing import Dict

from conformer.db.models import DBSystem, DBSystemLabel
from conformer.systems import System
from conformer_core.stages import Stage


class UnknownSystemException(Exception):
    """Exception raised if System is not in the database."""

    ...


Identifyer = str | int | System


def get_systems(*identifyer: str | int | System) -> System | Dict[Identifyer, System]:
    """Retrieves multiple NamedSystems from the database"""
    sys_names = []
    sys_ids = []
    fingerprints = []
    just_systems = []
    for id in identifyer:
        if isinstance(id, str):
            # Very low chances someone would make this bad a name
            if len(id) == 40 and id.isalnum():
                fingerprints.append(id)
            else:
                # TODO: Allow lookups like sys-3d506b8f
                try:
                    sys_ids.append(int(id))
                except ValueError:
                    sys_names.append(id)
        elif isinstance(id, int):
            sys_ids.append(id)
        elif isinstance(id, System):
            just_systems.append(id)
        else:
            raise Exception(f"connot get system based on id of type `{type(id)}")

    # Get named systems
    if "ALL" in sys_names:
        sys_names = DBSystemLabel.all_system_names()

    if sys_names:
        systems = DBSystemLabel.get_systems_by_name(list(sys_names))
        # Check that we got all the systems
        missing = set(sys_names).difference(set(systems.keys()))
        if missing:
            raise UnknownSystemException(
                f"Project does not contain system(s) named: {', '.join(missing)}"
            )
    else:
        systems = {}

    # Get systems by IDs
    if sys_ids:
        id_systems = DBSystem.get_systems(sys_ids)
        missing = set(sys_ids).difference(set(id_systems.keys()))
        if missing:
            raise UnknownSystemException(
                f"Project does not contain system(s) with IDs: {', '.join(missing)}"
            )
        systems.update(id_systems)

    if fingerprints:
        fp_systems = DBSystem.get_systems_by_fingerprint(fingerprints)
        missing = set(fingerprints).difference(set(fp_systems.keys()))
        if missing:
            raise UnknownSystemException(
                f"Project does not contain system(s) with Fingerprints: {', '.join(missing)}"
            )
        systems.update(fp_systems)

    # Handle any systems passed to the function
    if just_systems:
        DBSystem.get_system_DBID(just_systems)
        systems.update({s: s for s in just_systems})

    return systems


def get_system(id: str | int | System) -> System:
    return next(get_systems(id).values().__iter__())


class GetSystem(Stage):
    """Simple stage which retrieves a System from the database by name"""

    def __call__(self, _null: None, system_name: str) -> System:
        return get_system(system_name)


class Calculation(Stage):
    ...
