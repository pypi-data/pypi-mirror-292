#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
__all__ = ["SystemRecord", "RecordStatus", "SystemMatrixProperty"]

from copy import copy
from dataclasses import dataclass
from itertools import chain
from typing import Any, Callable, Iterable, Optional, Tuple

import numpy as np
import xarray as xa

from conformer.systems import default_join
from conformer_core.properties.core import (
    MASTER_PROP_LIST,
    MatrixProperty,
    Property,
    PropertySet,
)
from conformer_core.records import Record, RecordStatus
from conformer_core.util import ind, summarize

from .systems import Atom, NamedSystem, System


@dataclass
class SystemMatrixProperty(MatrixProperty):
    extensive: Tuple[str, ...] = tuple()
    join_fn: Callable = default_join

    @staticmethod
    def atom_filter(a: Atom):
        return a.is_physical

    def __post_init__(self):
        super().__post_init__()
        if len(self.window) != len(self.extensive):
            raise ValueError(
                "The length of `window`, `extensive`, and `dim_labels` must be the same length"
            )

    def validate(self, d: Any):
        if isinstance(d, list):
            d = np.array(d, dtyp=self.type)
        assert isinstance(d, (np.ndarray, xa.DataArray))
        assert d.dtype == self.type
        assert len(d.shape) == len(self.window)
        for dim, w, e in zip(d.shape, self.window, self.extensive):
            if e:
                assert dim % w == 0
            else:
                assert dim == w
        return d

    @staticmethod
    def extensive_index(window: int, elements: Iterable[int]):
        return list(chain(*(range(e * window, e * window + window) for e in elements)))

    @staticmethod
    def intensive_index(window: int):
        return list(range(window))

    def index_data(
        self, data: np.ndarray | xa.DataArray, elements: Iterable[int]
    ) -> xa.DataArray:
        # TODO: Handle cases with repeating elements!
        assert len(set(elements)) == len(
            elements
        ), "Cannot handle quasi-periodic systems yet"
        dims = []
        for w, ext, dim_label in zip(self.window, self.extensive, self.dim_labels):
            dims.append(
                (
                    dim_label,
                    self.extensive_index(w, elements)
                    if ext
                    else self.intensive_index(w),
                )
            )

        if isinstance(data, xa.DataArray):
            return data.reindex(dict(dims))
        else:
            return xa.DataArray(data, dims)

    def system_index(self, data, sys: System) -> xa.DataArray:
        elements = [i for (i, a) in enumerate(sys) if self.atom_filter(a)]
        return self.index_data(data, elements)

    def system_join_index(self, ref_sys: System, other_sys: System):
        idx_map = {j: i for (i, j) in ref_sys.join_map(other_sys, join_fn=self.join_fn)}
        max_idx = ref_sys.size
        elements = []  # Maybe pre-allocate in NP if performance isn't there
        for i, a in enumerate(other_sys):
            if not self.atom_filter(a):
                continue
            try:
                elements.append(idx_map[i])
            except KeyError:
                elements.append(max_idx)
                max_idx += 1  # Just keep counting
        return elements

    def add_into(
        self, sys1: System, mat1: np.ndarray | xa.DataArray, sys2: System, mat2, coef=1
    ) -> xa.DataArray:
        """Adds data from `mat2` into `mat1`. This function mutates mat1!"""
        if not isinstance(mat1, xa.DataArray):
            mat1 = self.system_index(mat1, sys1)

        mat2 = self.index_data(mat2, self.system_join_index(sys1, sys2))
        mat2 = mat2.reindex_like(mat1, fill_value=self.type(0), copy=False)
        mat1 += coef * mat2
        return mat1
    
    def __hash__(self) -> int:
        return self.name.__hash__()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name


def empty_properties(system: System, properties=None):
    if properties is None:
        properties = MASTER_PROP_LIST.values()

    P = PropertySet({})
    for p in properties:
        if p.__class__ is Property:
            if p.type is int:
                P[p] = 0
            elif p.type is float:
                P[p] = 0.0
            else:
                raise ValueError(f"Unknown how to zero property type `{p.type}`")
        elif p.__class__ is SystemMatrixProperty:
            shape = [
                w * system.size if e else w for (w, e) in zip(p.window, p.extensive)
            ]
            P[p] = p.system_index(np.zeros(shape, dtype=p.type), system)
        elif p.__class__ is MatrixProperty:
            P[p] = np.zeros(p.window, dtype=p.type)
        else:
            raise ValueError(f"Unknow property type`{p.type}`")
    return P


@dataclass
class SystemRecord(Record):
    system: Optional[System] = None  # Default appeased dataclass constructor

    def add_into(self, record: "SystemRecord", coef: int = 1) -> None:
        """
        Adds properties P into self. Deletes properties not in both
        """

        if record.properties is None:
            raise ValueError("Other record does not contain properties")
        outer_P = record.properties
        if self.properties is None:
            inner_P = empty_properties(self.system, outer_P.props)
            self.properties = inner_P
        else:
            inner_P = self.properties

        # Remove non-existant properties
        prop_rm = inner_P.props.difference(outer_P.props)
        for p in prop_rm:
            del inner_P[p]

        # Update property list
        inner_P.props.intersection_update(outer_P.props)

        # Accumulate!
        for p in inner_P.props:
            _coef = coef if p.use_coef else 1
            if p.__class__ in (Property, MatrixProperty):
                inner_P.values[p] += _coef * outer_P[p]
            elif isinstance(p, SystemMatrixProperty):
                inner_P.values[p] = p.add_into(
                    self.system, inner_P[p], record.system, outer_P[p], coef=_coef
                )
            else:
                raise ValueError(f"Cannot accumulate property of type `{p.__name__}")

    def swap_system(self, system: System) -> "SystemRecord":
        if self.system is system:
            return self
        # TODO: Removing check speeds things up sooooo much. But we should make it optional
        assert self.system.eq_TI(system), "Cannot swap non-equivalent systems"
        if system._saved == 0:
            system._saved == self.system._saved  # Save the DB some work
        new_record = copy(self)
        new_record.system = system

        # Re-order matrix properties for non-cannonical systems
        if (
            new_record.properties
            and (not self.system.is_canonized
            or not system.is_canonized)
        ):
            reindex = False
            for p in new_record.properties.props:
                if isinstance(p, SystemMatrixProperty):
                    reindex = True
                    break

            if reindex:
                new_record.properties = PropertySet({})
                for p in self.properties.props:
                    if isinstance(p, (SystemMatrixProperty)):
                        new_record.properties[p] = p.index_data(
                            self.properties[p],
                            p.system_join_index(self.system, system),
                        ).sortby(list(p.dim_labels))
                    else:
                        new_record.properties[p] = self.properties[p]


        return new_record

    def summarize(self, padding=2, level=0) -> str:
        rec_str = ind(padding, level, f"System Record {self.id}: \n")

        level += 1
        rec_str += ind(padding, level, f"Driver: {self.stage.name}\n")
        if self._saved:
            rec_str += ind(padding, level, f"Database ID: {self._saved}\n")
        rec_str += ind(
            padding,
            level,
            f"Created: {self.start_time.isoformat(timespec='minutes')}\n",
        )

        if isinstance(self.system, NamedSystem):
            rec_str += ind(padding, level, f"System: {self.system.name}\n")
        else:
            rec_str += ind(padding, level, f"System: {self.system}\n")
        rec_str += ind(padding, level, f"Status: {self.status.name}\n")

        if self.meta:
            rec_str += summarize("Meta", self.meta, padding=padding, level=level)

        if self.properties:
            rec_str += ind(padding, level, "Properties:\n")
            rec_str += self.properties.summarize(padding=padding, level=level + 1)
        return rec_str
