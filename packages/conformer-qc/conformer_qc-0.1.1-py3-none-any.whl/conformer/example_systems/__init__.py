#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from importlib.abc import Traversable
from importlib.resources import files
from typing import Optional

from conformer.geometry_readers.util import read_geometry
from conformer.systems import System


def open_example(file: str) -> Traversable:
    return files("conformer.example_systems").joinpath(file)


def read_example(
    file: str, name: Optional[str] = None, charges: Optional[dict] = None
) -> System:
    name_stem, ext = file.rsplit(".", 1)
    name = name if name else name_stem
    with open_example(file).open("r") as f:
        return read_geometry(name, f, charges=charges, ext="." + ext)
