from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(slots=True)
class ScheduleSpec:
    send_at: datetime

    def __post_init__(self) -> None:
        if self.send_at.tzinfo is None:
            raise ValueError("send_at must be timezone-aware")
        if self.send_at <= datetime.now(timezone.utc):
            raise ValueError("send_at must be in the future")

    @property
    def is_due(self) -> bool:
        return self.send_at <= datetime.now(timezone.utc)
