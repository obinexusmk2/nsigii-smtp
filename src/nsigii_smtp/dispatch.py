from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DispatchStatus(str, Enum):
    SENT = "sent"
    SCHEDULED = "scheduled"
    FAILED = "failed"


@dataclass(slots=True)
class DispatchResult:
    status: DispatchStatus
    detail: str
    recipient: str
    subject: str
    role: str
    scheduled_for: str | None = None
    message_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)
