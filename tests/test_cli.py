from datetime import datetime, timedelta, timezone
import json

import pytest

from nsigii_smtp import DispatchResult, DispatchStatus
from nsigii_smtp.cli import main


class FakeService:
    def send_now(self, message, artifacts=None):
        return DispatchResult(
            status=DispatchStatus.SENT,
            detail="ok",
            recipient=message.recipient,
            subject=message.subject,
            role=message.role.value,
        )

    def schedule(self, message, schedule, artifacts=None):
        return DispatchResult(
            status=DispatchStatus.SCHEDULED,
            detail="scheduled",
            recipient=message.recipient,
            subject=message.subject,
            role=message.role.value,
            scheduled_for=schedule.send_at.isoformat(),
        )


def test_cli_send_outputs_json(monkeypatch, capsys):
    monkeypatch.setattr("nsigii_smtp.cli.NSIGIISMTPService", lambda transport: FakeService())
    monkeypatch.setattr("nsigii_smtp.cli.SMTPTransport", lambda settings: object())
    monkeypatch.setattr("nsigii_smtp.cli.SMTPSettings.from_env", lambda: object())
    rc = main(
        [
            "send",
            "--from", "sender@example.org",
            "--to", "aid@example.org",
            "--subject", "Need aid",
            "--body", "Urgent need",
            "--need", "food",
        ]
    )
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["status"] == "sent"


def test_cli_schedule_invalid_datetime(monkeypatch):
    monkeypatch.setattr("nsigii_smtp.cli.SMTPSettings.from_env", lambda: object())
    with pytest.raises(SystemExit):
        main(
            [
                "schedule",
                "--from", "sender@example.org",
                "--to", "aid@example.org",
                "--subject", "Need aid",
                "--body", "Urgent need",
                "--need", "food",
                "--send-at", "tomorrow",
            ]
        )


def test_cli_send_missing_smtp_config_exits_cleanly(capsys):
    with pytest.raises(SystemExit):
        main(
            [
                "send",
                "--from", "sender@example.org",
                "--to", "aid@example.org",
                "--subject", "Need aid",
                "--body", "Urgent need",
                "--need", "food",
            ]
        )
    err = capsys.readouterr().err
    assert "NSIGII_SMTP_HOST is required" in err


def test_cli_rejects_literal_caret_argument(monkeypatch, capsys):
    monkeypatch.setattr("nsigii_smtp.cli.SMTPSettings.from_env", lambda: object())
    with pytest.raises(SystemExit):
        main(
            [
                "send",
                "^",
                "--from", "sender@example.org",
                "--to", "aid@example.org",
                "--subject", "Need aid",
                "--body", "Urgent need",
                "--need", "food",
            ]
        )
    err = capsys.readouterr().err
    assert "unexpected '^' argument" in err


def test_cli_schedule_outputs_json(monkeypatch, capsys):
    monkeypatch.setattr("nsigii_smtp.cli.NSIGIISMTPService", lambda transport: FakeService())
    monkeypatch.setattr("nsigii_smtp.cli.SMTPTransport", lambda settings: object())
    monkeypatch.setattr("nsigii_smtp.cli.SMTPSettings.from_env", lambda: object())
    future = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    rc = main(
        [
            "schedule",
            "--from", "sender@example.org",
            "--to", "aid@example.org",
            "--subject", "Need aid",
            "--body", "Urgent need",
            "--need", "food",
            "--send-at", future,
        ]
    )
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["status"] == "scheduled"
