from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.timezone import current_production_context, current_production_date, current_shift_code


def test_shift_c_after_midnight_keeps_previous_production_date():
    moment = datetime(2026, 8, 29, 1, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
    production_date, shift = current_production_context(moment)
    assert shift == "C"
    assert production_date.isoformat() == "2026-08-28"
    assert current_shift_code(moment) == "C"
    assert current_production_date(moment).isoformat() == "2026-08-28"


def test_shift_c_before_midnight_uses_same_calendar_date():
    moment = datetime(2026, 8, 28, 22, 30, tzinfo=ZoneInfo("Asia/Kolkata"))
    production_date, shift = current_production_context(moment)
    assert shift == "C"
    assert production_date.isoformat() == "2026-08-28"


def test_shift_a_and_b():
    a = datetime(2026, 8, 28, 7, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
    b = datetime(2026, 8, 28, 15, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
    assert current_production_context(a) == (a.date(), "A")
    assert current_production_context(b) == (b.date(), "B")
