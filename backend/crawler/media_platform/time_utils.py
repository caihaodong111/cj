from datetime import date, datetime, time as dt_time
from typing import Any, Optional
from zoneinfo import ZoneInfo


CHINA_TIMEZONE = ZoneInfo("Asia/Shanghai")
_DATETIME_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y/%m/%d %H:%M:%S",
    "%Y/%m/%d %H:%M",
)
_DATE_FORMATS = (
    "%Y-%m-%d",
    "%Y/%m/%d",
)


def _ensure_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=CHINA_TIMEZONE)
    return value.astimezone(CHINA_TIMEZONE)


def _numeric_timestamp_to_millis(value: int) -> int:
    abs_value = abs(value)
    if abs_value >= 10**11:
        return value
    if abs_value >= 10**9:
        return value * 1000
    return value


def coerce_timestamp_ms(value: Any) -> Optional[int]:
    if value is None:
        return None

    if isinstance(value, datetime):
        return int(_ensure_datetime(value).timestamp() * 1000)

    if isinstance(value, date):
        dt_value = datetime.combine(value, dt_time.min, tzinfo=CHINA_TIMEZONE)
        return int(dt_value.timestamp() * 1000)

    if isinstance(value, (int, float)):
        return _numeric_timestamp_to_millis(int(value))

    raw = str(value).strip()
    if not raw:
        return None

    if raw[0] in "+-" and raw[1:].isdigit():
        return _numeric_timestamp_to_millis(int(raw))

    if raw.isdigit():
        return _numeric_timestamp_to_millis(int(raw))

    iso_candidate = raw
    if iso_candidate.endswith("Z"):
        iso_candidate = f"{iso_candidate[:-1]}+00:00"

    try:
        parsed = datetime.fromisoformat(iso_candidate)
    except ValueError:
        parsed = None

    if parsed is None:
        for fmt in _DATETIME_FORMATS:
            try:
                parsed = datetime.strptime(raw, fmt)
                break
            except ValueError:
                continue

    if parsed is None:
        for fmt in _DATE_FORMATS:
            try:
                parsed_date = datetime.strptime(raw, fmt).date()
                parsed = datetime.combine(parsed_date, dt_time.min)
                break
            except ValueError:
                continue

    if parsed is None:
        return None

    return int(_ensure_datetime(parsed).timestamp() * 1000)
