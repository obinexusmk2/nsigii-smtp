from datetime import datetime, timezone

import pytest

from nsigii_smtp import HumanNeedPayload, NSIGIIMessage, TrilateralState


def test_human_need_payload_requires_supported_needs():
    with pytest.raises(ValueError):
        HumanNeedPayload(summary="help", needs=["pizza"])


def test_message_requires_valid_email_and_body():
    payload = HumanNeedPayload(summary="Need aid", needs=["food"])
    with pytest.raises(ValueError):
        NSIGIIMessage(
            sender="not-an-email",
            recipient="aid@example.org",
            subject="Need aid",
            body="message",
            payload=payload,
            state=TrilateralState.HERE_AND_NOW,
            created_at=datetime.now(timezone.utc),
        )
