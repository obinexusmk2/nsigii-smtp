from datetime import datetime, timezone
import smtplib

import pytest
from nsigii_smtp import HumanNeedPayload, NSIGIIMessage, SMTPSettings, SMTPTransport, TrilateralState


class FakeSMTP:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.started_tls = False
        self.logged_in = None
        self.sent = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def starttls(self, context=None):
        self.started_tls = True

    def login(self, username, password):
        self.logged_in = (username, password)

    def send_message(self, email):
        self.sent = email


def test_transport_sends_message(monkeypatch):
    fake = FakeSMTP("smtp.example.org", 587)
    monkeypatch.setattr("smtplib.SMTP", lambda host, port: fake)
    payload = HumanNeedPayload(summary="Need aid", needs=["food", "water"])
    message = NSIGIIMessage(
        sender="sender@example.org",
        recipient="aid@example.org",
        subject="Urgent request",
        body="Need food and water",
        payload=payload,
        state=TrilateralState.HERE_AND_NOW,
        created_at=datetime.now(timezone.utc),
    )
    transport = SMTPTransport(
        SMTPSettings(
            host="smtp.example.org",
            port=587,
            username="user",
            password="pass",
        )
    )
    result = transport.send(message)
    assert result.status.value == "sent"
    assert fake.started_tls is True
    assert fake.logged_in == ("user", "pass")
    assert fake.sent["X-NSIGII-Role"] == "alpha"


def test_transport_wraps_connection_errors(monkeypatch):
    monkeypatch.setattr("smtplib.SMTP", lambda host, port: (_ for _ in ()).throw(OSError("dns failed")))
    payload = HumanNeedPayload(summary="Need aid", needs=["food"])
    message = NSIGIIMessage(
        sender="sender@example.org",
        recipient="aid@example.org",
        subject="Urgent request",
        body="Need food",
        payload=payload,
        state=TrilateralState.HERE_AND_NOW,
        created_at=datetime.now(timezone.utc),
    )
    transport = SMTPTransport(SMTPSettings(host="smtp.example.org"))
    with pytest.raises(ValueError, match="Could not connect to SMTP server"):
        transport.send(message)


def test_transport_wraps_authentication_errors(monkeypatch):
    class AuthFailSMTP(FakeSMTP):
        def login(self, username, password):
            raise smtplib.SMTPAuthenticationError(535, b"auth failed")

    monkeypatch.setattr("smtplib.SMTP", lambda host, port: AuthFailSMTP(host, port))
    payload = HumanNeedPayload(summary="Need aid", needs=["food"])
    message = NSIGIIMessage(
        sender="sender@example.org",
        recipient="aid@example.org",
        subject="Urgent request",
        body="Need food",
        payload=payload,
        state=TrilateralState.HERE_AND_NOW,
        created_at=datetime.now(timezone.utc),
    )
    transport = SMTPTransport(
        SMTPSettings(host="smtp.gmail.com", username="user", password="bad-pass")
    )
    with pytest.raises(ValueError, match="SMTP authentication failed"):
        transport.send(message)
