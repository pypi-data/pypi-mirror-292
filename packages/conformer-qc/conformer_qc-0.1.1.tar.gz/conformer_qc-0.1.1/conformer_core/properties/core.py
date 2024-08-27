#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from collections.abc import MutableMapping
from dataclasses import dataclass
from typing import (
    Any,
    Dict,
    Iterator,
    Set,
    Tuple,
    Type,
)

import numpy as np
import xarray as xa


@dataclass
class Property:
    """
    Defines the an agreed-upon interface for QM backends to
    extract and implement properties. QM backends are not required
    to implement all properties.
    """

    name: str
    readable_name: str
    type: Type
    unit: str
    use_coef: bool
    help: str

    def validate(self, v: Any):
        assert isinstance(v, self.type), f"{v} is not of type {self.type}"
        return v

    def to_dict(self, v: Any):
        return v

    def from_dict(self, v):
        return self.validate(self.type(v))

    def __hash__(self) -> int:
        return self.name.__hash__()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name


@dataclass
class MatrixProperty(Property):
    window: Tuple[int, ...] = tuple()
    dim_labels: Tuple[str, ...] = tuple()

    def __post_init__(self):
        if len(self.window) == 0:
            raise ValueError("window must be set.")
        if len(self.window) != len(self.dim_labels):
            if len(self.window) != len(self.dim_labels):
                raise ValueError(
                    "The length of `window` and `dim_label` must be the same length"
                )

    def validate(self, d: Any):
        if isinstance(d, list):
            d = np.array(d, dtyp=self.type)
        assert isinstance(d, (np.ndarray))
        assert d.shape == self.window
        assert d.dtype == self.type
        return d

    def to_dict(self, v: Any):
        if isinstance(v, xa.DataArray):
            v = v.data
        return dict(
            shape=v.shape,
            dtype=v.dtype.name,
            data=v.ravel().tolist(),
        )

    def from_dict(self, d):
        return self.validate(
            np.array(d["data"], dtype=self.type).reshape(tuple(d["shape"]))
        )

    def __hash__(self) -> int:
        return self.name.__hash__()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.name == other.name

# Master property list used to construct extractors and adders and validators
MASTER_PROP_LIST: Dict[str, Property] = {}


def add_property(property: Property) -> None:
    global MASTER_PROP_LIST
    # if property in MASTER_PROP_LIST and property is not MASTER_PROP_LIST[property]:
    if property.name in MASTER_PROP_LIST:
        raise ValueError(
            f"An alternative property to '{property.name}' has already been added."
        )
    MASTER_PROP_LIST[property.name] = property


def get_property(p: str) -> Property:
    if isinstance(p, str):
        return MASTER_PROP_LIST[p]
    else:
        return p


def remove_property(name: str | Property) -> None:
    if isinstance(name, str):
        del MASTER_PROP_LIST[name]
    else:
        del MASTER_PROP_LIST[name.name]


class PropertySet(MutableMapping):
    props: Set[Property]
    values: Dict[str, Any]

    def __init__(self, properties: Dict[str, Any]) -> None:
        props = set()
        values = dict()
        for _p, _v in properties.items():
            p = get_property(_p)
            v = p.validate(_v)
            props.add(p)
            values[p] = v
        self.props = props
        self.values = values

    def __getitem__(self, key: str | Type) -> Any:
        return self.values[get_property(key)]

    def __setitem__(self, key: str, val: Any) -> None:
        p = get_property(key)
        self.props.add(p)
        self.values[p] = p.validate(val)

    def __delitem__(self, key: str) -> None:
        p = get_property(key)
        del self.values[p]

    def __len__(self) -> int:
        return len(self.values)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.values})"

    def __iter__(self) -> Iterator[Tuple[Property, Any]]:
        return iter(self.values.items())

    def __contains__(self, item: Any) -> bool:
        return get_property(item) in self.props

    def to_dict(self) -> Dict[str, Any]:
        return {p.name: p.to_dict(v) for (p, v) in self.values.items()}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "PropertySet":
        properties = {}
        for k, v in d.items():
            prop = get_property(k)
            properties[prop] = prop.from_dict(v)
        return cls(properties)

    def summarize(self, padding=2, level=0) -> str:
        prop_str = ""

        if not self.values:
            return " " * (padding * level) + "NO PROPERTIES"

        max_label_width = max([len(get_property(n).readable_name) for n in self.values])

        FLOAT_FORMAT_STR = " " * (
            padding * level
        ) + "{{0:<{}s}}: {{1:< .6f}} {{2:s}}\n".format(max_label_width)
        INT_FORMAT_STR = " " * (
            padding * level
        ) + "{{0:<{}s}}: {{1:< d}} {{2:s}}\n".format(max_label_width)
        DEFAULT_FORMAT = " " * (
            padding * level
        ) + "{{0:<{}s}}: {{1:<s}} {{2:s}}\n".format(max_label_width)
        for prop_spec, v in self:
            if isinstance(v, float):
                prop_str += FLOAT_FORMAT_STR.format(
                    prop_spec.readable_name, v, prop_spec.unit
                )
            elif isinstance(v, int):
                prop_str += INT_FORMAT_STR.format(
                    prop_spec.readable_name, v, prop_spec.unit
                )
            elif isinstance(v, np.ndarray):
                shape = "x".join((str(s) for s in v.shape))
                prop_str += DEFAULT_FORMAT.format(
                    prop_spec.readable_name, f"{shape} Array", prop_spec.unit
                )
            else:
                prop_str += DEFAULT_FORMAT.format(
                    prop_spec.readable_name, str(type(v).__name__), prop_spec.unit
                )
        return prop_str
