#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#
import enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from conformer_core.properties.core import PropertySet
from conformer_core.stages import Stage
from conformer_core.util import summarize


class RecordStatus(enum.IntEnum):
    PENDING = 0
    RUNNING = 1
    COMPLETED = 2
    FAILED = 3


@dataclass
class Record:
    """Record for Stage result"""

    stage: Stage  # The stage that created this result
    id: UUID = field(default_factory=uuid4)

    status: RecordStatus = RecordStatus.PENDING
    start_time: Optional[datetime] = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    properties: Optional[PropertySet] = None
    meta: Optional[Dict[str, Any]] = field(default_factory=dict)
    _saved: int = 0

    def summarize(self, padding=2, level=0) -> str:
        rec_str = f"Record {self.id}: \n"
        level += 1
        rec_str += " " * (padding * level) + f"Stage: {self.stage.name}\n"
        rec_str += " " * (padding * level) + f"Status: {self.status.name}\n"
        rec_str += (
            " " * (padding * level)
            + f"Created: {self.start_time.isoformat(timespec='minutes')}\n"
        )

        if self.meta:
            rec_str += summarize("Meta", self.meta)

        if self.properties:
            rec_str += " " * (padding * level) + "Properties:\n"
            rec_str += self.properties.summarize(padding=padding, level=level + 1)

        return rec_str
