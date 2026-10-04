"""Asia/Kolkata production-date and shift helpers.

Shift C starts at 22:00 and ends at 06:00 the next calendar day, but all
records remain attached to the production date on which Shift C started.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.core.config import get_settings

SHIFT_A_START = time(6, 0)
SHIFT_B_START = time(14, 0)
SHIFT_C_START = time(22, 0)


def app_timezone() -> ZoneInfo:
    return ZoneInfo(get_settings().timezone)


def now_local(moment: datetime | None = None) -> datetime:
    tz = app_timezone()
    if moment is None:
        return datetime.now(tz)
    if moment.tzinfo is None:
        return moment.replace(tzinfo=tz)
    return moment.astimezone(tz)


def to_utc(moment: datetime) -> datetime:
    local = now_local(moment)
    return local.astimezone(ZoneInfo("UTC"))


def current_shift_code(moment: datetime | None = None) -> str:
    local = now_local(moment)
    clock = local.time()
    if SHIFT_A_START <= clock < SHIFT_B_START:
        return "A"
    if SHIFT_B_START <= clock < SHIFT_C_START:
        return "B"
    return "C"


def current_production_date(moment: datetime | None = None) -> date:
    """Production date for the current local time, including Shift C after midnight."""
    local = now_local(moment)
    if current_shift_code(local) == "C" and local.time() < SHIFT_A_START:
        return local.date() - timedelta(days=1)
    return local.date()


def current_production_context(moment: datetime | None = None) -> tuple[date, str]:
    local = now_local(moment)
    return current_production_date(local), current_shift_code(local)
