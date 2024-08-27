#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import hashlib
import json
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from conformer_core.records import Record
from conformer_core.util import ind, summarize


@dataclass
class CalculationRecord(Record):
    steps: List[Tuple["str", Tuple]] = field(default=list)
    name: Optional[str] = None  # Required
    hash: Optional["hashlib._Hash"] = None

    def __init__(self, *args, **kwargs) -> None:
        name = kwargs.pop("name")
        steps = kwargs.pop("steps")
        hash = kwargs.pop("hash", None)

        # Now init the Record dataclass
        super().__init__(*args, **kwargs)

        self.steps = steps
        self.hash = self.make_hash(steps) if hash is None else hash
        self.name = self.hash.hexdigest() if name is None else name

    @staticmethod
    def make_hash(steps: List) -> "hashlib._Hash":
        hash_data = json.dumps(steps, sort_keys=True).encode("utf-8")
        hash = hashlib.new("sha1")
        hash.update(hash_data)
        return hash

    def summarize(self, padding=2, level=0) -> str:
        rec_str = ind(padding, level, f"Calculation {self.name}: \n")

        level += 1
        rec_str += ind(padding, level, f"ID: {self.id}\n")
        rec_str += ind(padding, level, f"Status: {self.status.name}\n")
        rec_str += ind(
            padding,
            level,
            f"Created: {self.start_time.isoformat(timespec='minutes')}\n",
        )

        steps = []
        for k, args in self.steps:
            if args:
                str_args = ",".join(map(str, args))
                steps.append(f"{k}({str_args})")
            else:
                steps.append(f"{k}")
        rec_str += summarize("Steps", steps, padding=padding, level=level)

        if self.meta:
            rec_str += summarize("Meta", self.meta, padding=padding, level=level + 1)

        if self.properties:
            rec_str += ind(padding, level, "Properties:\n")
            rec_str += self.properties.summarize(padding=padding, level=level + 1)
        return rec_str
