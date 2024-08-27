#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from typing import Any, Dict, List

import pydantic


def range_list_from_str(int_str: str) -> List[str]:
    parts = int_str.split(",")
    int_list = []
    for part in parts:
        try:
            int_list.append(int(part))
            continue
        except ValueError:
            pass

        part_range = part.split("-")
        if len(part_range) != 2:
            raise ValueError(f"Cannot parse {part}")
        int_list.extend(range(int(part_range[0]), int(part_range[1]) + 1))
    return int_list


class NamedSystemInfo(pydantic.BaseModel):
    name: str | None = None
    note: str | None = None
    charges: Dict[int, int] | None = None
    roles: Dict[int, int | str | dict] | None = None

class SubsystemModel(NamedSystemInfo):
    """Pydantic model for deriving a subsystem from an imported Supersystem"""

    include_list: List[int]  # TODO: Parse strings to into a correct format

    @pydantic.field_validator("include_list")
    @classmethod
    def unpack_list(cls, v: Any) -> List[int]:
        if isinstance(v, str):
            try:
                return range_list_from_str(v)
            except ValueError:
                raise ValueError(f'Cannot parse "{v}"')
        return v


class SupersystemModel(NamedSystemInfo):
    """Pydantic model for import systems"""
    source: str 
    unit_cell: List[float] | None = None
    subsystems: List[SubsystemModel] | None = None