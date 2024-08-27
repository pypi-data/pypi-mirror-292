#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from hashlib import sha1
from io import StringIO, TextIOWrapper
from pathlib import Path
from typing import Dict, Iterable, Optional, TextIO, Union

import numpy as np

from conformer.common import AtomRole, int_to_role, str_to_role
from conformer.systems import NamedSystem

from .frag import FragRead
from .pdb import PDBRead
from .xyz import XYZRead

REGISTRY = {
    ".frag": FragRead,
    ".pdb": PDBRead,
    ".xyz": XYZRead,
}


class UnsupportedFileType(Exception):
    pass


class SystemExists(Exception):
    pass


class SystemDoesNotExist(Exception):
    pass


def hash_file_contents(fs_content: str) -> str:
    return sha1(fs_content.encode("utf-8")).hexdigest()


def read_geometry(
    name: str,
    source: Union[str, Path, StringIO],
    note: Optional[str] = None,
    charges: Optional[Dict[int, int]] = None,
    roles: Optional[Dict[int, int | str | dict | AtomRole]] = None,
    unit_cell: Optional[Iterable[float]] = None,
    ext=None,
) -> NamedSystem:
    """
    Reads a geometry file from a a path, string, or stream and returns a `NamedSystem` object.
    """
    meta = {}
    if note:
        meta["note"] = note

    # Let's let the user specify an paths as a string.
    # Google suggest the longest filename on linux is 205 characters.
    # I have encountered this error when providing a file as string
    if isinstance(source, str) and len(source) < 150:
        if Path(source).is_file():
            source = Path(source)

    if isinstance(source, Path):
        if not source.is_file():
            raise FileNotFoundError("Input file `{}` does not exist.".format(source))
        # Assume this is a text file. Day it might not be...
        source_str = source.read_text()
        ext = source.suffix
        meta["path"] = str(source.absolute())
    elif isinstance(source, (TextIO, StringIO, TextIOWrapper)):
        source_str = source.read()
    elif isinstance(source, str):
        source_str = source
    else:
        raise TypeError(f"Unknown source type {source.__repr__()}")

    if ext is None:
        raise ValueError("Could not infer file type. Please specify extension")

    meta["hash"] = hash_file_contents(source_str)

    # Get geometry reader function and use it
    # TODO: Add a proper registry framework

    try:
        geometry_reader = REGISTRY[ext.lower()]
    except KeyError:
        raise UnsupportedFileType(
            'Fragment does not support reading ".{}" geometry files.'.format(ext)
        )

    sys_label: NamedSystem = geometry_reader(
        StringIO(source_str), charges=charges or {}
    )
    sys_label.name = name
    sys_label.meta.update(**meta)

    if unit_cell:
        sys_label.unit_cell = np.array(unit_cell)

    # Override atom roles in the system
    if roles:
        for ai, _r in roles.items():
            if isinstance(_r, int):
                r = int_to_role(_r)
            elif isinstance(_r, str):
                r = str_to_role(_r)
            elif isinstance(_r, dict):
                r = AtomRole(**_r)
            elif isinstance(_r, AtomRole):
                r = _r
            sys_label[ai - 1].role = r

    return sys_label
