from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from email.utils import parseaddr

from .trilateral import TransportRole, TrilateralState, map_state_to_role

ALLOWED_NEEDS = {"food", "water", "shelter", "medical", "supplies", "other"}


def _validate_email(value: str, field_name: str) -> None:
    _, parsed = parseaddr(value)
    if "@" not in parsed:
        raise ValueError(f"{field_name} must be a valid email address")


@dataclass(slots=True)
class HumanNeedPayload:
    summary: str
    needs: list[str]
    details: str = ""
    location: str = ""
    contact_name: str = ""
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.summary.strip():
            raise ValueError("summary is required")
        if not self.needs:
            raise ValueError("at least one humanitarian need is required")
        cleaned = []
        for need in self.needs:
            value = need.strip().lower()
            if not value:
                continue
            if value not in ALLOWED_NEEDS:
                raise ValueError(f"unsupported need: {need}")
            cleaned.append(value)
        if not cleaned:
            raise ValueError("at least one valid humanitarian need is required")
        self.needs = cleaned


@dataclass(slots=True)
class NSIGIIMessage:
    sender: str
    recipient: str
    subject: str
    body: str
    payload: HumanNeedPayload
    state: TrilateralState
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message_id: str | None = None
    audit_metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_email(self.sender, "sender")
        _validate_email(self.recipient, "recipient")
        if not self.subject.strip():
            raise ValueError("subject is required")
        if not self.body.strip():
            raise ValueError("body is required")
        if self.created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")

    @property
    def role(self) -> TransportRole:
        return map_state_to_role(self.state)
