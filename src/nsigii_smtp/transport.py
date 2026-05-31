from __future__ import annotations

from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import make_msgid
import os
import smtplib
import ssl

from .artifacts import Artifact
from .dispatch import DispatchResult, DispatchStatus
from .message import NSIGIIMessage


@dataclass(slots=True)
class SMTPSettings:
    host: str
    port: int = 587
    username: str | None = None
    password: str | None = None
    use_tls: bool = True

    @classmethod
    def from_env(cls) -> "SMTPSettings":
        host = os.environ.get("NSIGII_SMTP_HOST")
        if not host:
            raise ValueError("NSIGII_SMTP_HOST is required")
        port = int(os.environ.get("NSIGII_SMTP_PORT", "587"))
        username = os.environ.get("NSIGII_SMTP_USERNAME")
        password = os.environ.get("NSIGII_SMTP_PASSWORD")
        use_tls = os.environ.get("NSIGII_SMTP_USE_TLS", "true").lower() != "false"
        return cls(host=host, port=port, username=username, password=password, use_tls=use_tls)


class SMTPTransport:
    def __init__(self, settings: SMTPSettings):
        self.settings = settings

    def build_email(self, message: NSIGIIMessage, artifacts: list[Artifact] | None = None) -> EmailMessage:
        email = EmailMessage()
        email["From"] = message.sender
        email["To"] = message.recipient
        email["Subject"] = message.subject
        email["X-NSIGII-State"] = message.state.value
        email["X-NSIGII-Role"] = message.role.value
        email["Message-ID"] = message.message_id or make_msgid(domain="nsigii.local")
        email.set_content(message.body)
        for key, value in message.audit_metadata.items():
            email[f"X-NSIGII-Audit-{key}"] = value
        for artifact in artifacts or []:
            maintype, subtype = artifact.mime_type.split("/", maxsplit=1)
            email.add_attachment(
                artifact.content,
                maintype=maintype,
                subtype=subtype,
                filename=artifact.filename,
            )
        return email

    def send(self, message: NSIGIIMessage, artifacts: list[Artifact] | None = None) -> DispatchResult:
        email = self.build_email(message, artifacts)
        context = ssl.create_default_context()
        try:
            with smtplib.SMTP(self.settings.host, self.settings.port) as client:
                if self.settings.use_tls:
                    client.starttls(context=context)
                if self.settings.username and self.settings.password:
                    client.login(self.settings.username, self.settings.password)
                client.send_message(email)
        except smtplib.SMTPAuthenticationError as exc:
            raise ValueError("SMTP authentication failed; check username, password, and provider app-password settings") from exc
        except smtplib.SMTPException as exc:
            raise ValueError(f"SMTP delivery failed for {self.settings.host}:{self.settings.port}: {exc}") from exc
        except OSError as exc:
            raise ValueError(
                f"Could not connect to SMTP server {self.settings.host}:{self.settings.port}; "
                "check the hostname, port, network, and whether you are using a real SMTP provider instead of a placeholder host"
            ) from exc
        return DispatchResult(
            status=DispatchStatus.SENT,
            detail="Message sent via SMTP",
            recipient=message.recipient,
            subject=message.subject,
            role=message.role.value,
            message_id=email["Message-ID"],
        )
