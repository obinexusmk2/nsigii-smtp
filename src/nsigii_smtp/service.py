from __future__ import annotations

from datetime import timezone

from .artifacts import Artifact
from .dispatch import DispatchResult, DispatchStatus
from .message import NSIGIIMessage
from .schedule import ScheduleSpec
from .transport import SMTPTransport


class NSIGIISMTPService:
    def __init__(self, transport: SMTPTransport):
        self.transport = transport

    def send_now(self, message: NSIGIIMessage, artifacts: list[Artifact] | None = None) -> DispatchResult:
        return self.transport.send(message, artifacts)

    def schedule(
        self,
        message: NSIGIIMessage,
        schedule: ScheduleSpec,
        artifacts: list[Artifact] | None = None,
    ) -> DispatchResult:
        return DispatchResult(
            status=DispatchStatus.SCHEDULED,
            detail="Message scheduled for local-process delivery",
            recipient=message.recipient,
            subject=message.subject,
            role=message.role.value,
            scheduled_for=schedule.send_at.astimezone(timezone.utc).isoformat(),
            metadata={
                "artifacts": str(len(artifacts or [])),
                "scheduler": "local-process",
            },
        )
