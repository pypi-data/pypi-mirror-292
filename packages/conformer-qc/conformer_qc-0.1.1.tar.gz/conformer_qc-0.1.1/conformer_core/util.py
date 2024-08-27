#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
from textwrap import indent
from typing import Any, Dict, Iterable, List, Set


def ind(padding, level, s: str | None = None) -> str:
    s = str(s)
    return indent(s, " " * (padding * level))


def summarize(k, v, padding=2, level=0, prefix="") -> str:
    if k:
        rec_str = ind(padding, level, prefix + f"{k}:")
    else:
        rec_str = ind(padding, level, prefix)

    if isinstance(v, str):
        rec_str += summarize_str(v, padding=padding, level=level)
    elif isinstance(v, Dict):
        rec_str += "\n"
        rec_str += summarize_dict(v, padding=padding, level=level + 1)
    elif isinstance(v, Set):
        rec_str += "\n"
        rec_str += summarize_list(list(v), padding=padding, level=level + 1)
    elif isinstance(v, Iterable):
        rec_str += "\n"
        rec_str += summarize_list(v, padding=padding, level=level + 1)
    else:
        rec_str += f" {v}\n"
    return rec_str


def summarize_str(s: str, padding=2, level=0) -> str:
    if "\n" in s:
        return " |\n" + ind(padding, level + 1, s) + "\n"
    else:
        return " " + s + "\n"


def summarize_obj(
    obj: Any, fields: List[str], labels: List[str] = None, padding=2, level=0
) -> str:
    rec_str = ""

    if labels is None:
        labels = fields
    else:
        assert len(fields, labels)

    for f, l in zip(fields, labels):
        rec_str += summarize(l, getattr(obj, f), padding=2, level=level)
    return rec_str


def summarize_dict(d: Dict, padding=2, level=0) -> str:
    rec_str = ""
    keys = sorted(d.keys())
    for k in keys:
        v = d[k]
        rec_str += summarize(k, v, padding=padding, level=level)
    return rec_str


def summarize_list(_list: List, padding=2, level=0) -> str:
    rec_str = ""
    if len(_list) > 10:
        for i in _list[0:3]:
            rec_str += summarize(None, i, padding=padding, level=level, prefix="-")
        rec_str += ind(padding, level, f"... (+ {len(_list) - 6} more items)\n")
        for i in _list[-4:]:
            rec_str += summarize(None, i, padding=padding, level=level, prefix="-")
    else:
        for i in _list:
            rec_str += summarize(None, i, padding=padding, level=level, prefix="-")
    return rec_str
