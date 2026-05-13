import re
from datetime import date, datetime, timedelta
import dateparser
from dateutil.relativedelta import relativedelta

HOLIDAYS = {
    "christmas": (12, 25),
    "halloween": (10, 31),
    "new years": (1, 1),
}


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    s = s.lower().strip()
    base_dt = datetime.combine(today, datetime.min.time())

    # 1. Handle Holidays
    for holiday, (month, day) in HOLIDAYS.items():
        if holiday in s:
            year_match = re.search(r"\b(20\d{2})\b", s)
            year = int(year_match.group(1)) if year_match else today.year
            return date(year, month, day)

    # 2. Handle "X before/after Y"
    match = re.search(r"(.+?)\s+\b(before|after)\b\s+(.+)", s)
    if match:
        offset_str, direction, anchor_str = match.groups()
        anchor_date = parse(anchor_str, today=today)
        ref = datetime(2000, 1, 1)
        offset_dt = dateparser.parse(
            f"{offset_str} ago", settings={"RELATIVE_BASE": ref}
        )
        if offset_dt:
            delta = relativedelta(ref, offset_dt)
            return anchor_date - delta if direction == "before" else anchor_date + delta

    # 3. Handle "next [weekday]"
    weekday_map = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }
    next_match = re.match(
        r"next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", s
    )
    if next_match:
        target_wd = weekday_map[next_match.group(1)]
        days_ahead = (target_wd - today.weekday()) % 7
        return today + timedelta(days=days_ahead + 7)

    # 4. Fallback
    settings = {
        "RELATIVE_BASE": base_dt,
        "PREFER_DATES_FROM": "future",
        "PREFER_DAY_OF_MONTH": "first",
    }
    parsed_dt = dateparser.parse(s, settings=settings)
    if parsed_dt:
        return parsed_dt.date()

    raise ValueError(f"Could not parse date string: {s}")
