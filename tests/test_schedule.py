from datetime import datetime, timedelta, timezone

import pytest

from nsigii_smtp import ScheduleSpec


def test_schedule_rejects_past_time():
    with pytest.raises(ValueError):
        ScheduleSpec(send_at=datetime.now(timezone.utc) - timedelta(minutes=1))


def test_schedule_accepts_future_time():
    spec = ScheduleSpec(send_at=datetime.now(timezone.utc) + timedelta(minutes=5))
    assert spec.send_at.tzinfo is not None
