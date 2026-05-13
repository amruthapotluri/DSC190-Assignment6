import re
from datetime import date, datetime, timedelta

import dateparser
from dateutil.relativedelta import relativedelta

HOLIDAYS = {
    "christmas": (12, 25),
    "halloween": (10, 31),
    "new years": (1, 1),
}

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    s = s.lower().strip()
    base_dt = datetime.combine(today, datetime.min.time())

    # -------------------------
    # 1. Holidays
    # -------------------------
    for holiday, (month, day) in HOLIDAYS.items():
        if holiday in s:
            year_match = re.search(r"\b(20\d{2})\b", s)
            year = int(year_match.group(1)) if year_match else today.year
            return date(year, month, day)

    # -------------------------
    # 2. "next <weekday>"
    # -------------------------
    match = re.fullmatch(
        r"next (monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
        s,
    )

    if match:
        target_weekday = WEEKDAYS[match.group(1)]
        current_weekday = today.weekday()

        # always go to NEXT week's weekday
        days_ahead = (7 - current_weekday) + target_weekday

        return today + timedelta(days=days_ahead)

    # -------------------------
    # 3. "X before/after Y"
    # -------------------------
    match = re.search(r"(.+?)\s+(before|after)\s+(.+)", s)

    if match:
        offset_str = match.group(1).strip()
        direction = match.group(2).strip()
        anchor_str = match.group(3).strip()

        anchor_date = parse(anchor_str, today=today)

        ref = datetime(2000, 1, 1)
        offset_dt = dateparser.parse(
            f"{offset_str} ago",
            settings={"RELATIVE_BASE": ref},
        )

        if offset_dt:
            delta = relativedelta(ref, offset_dt)

            if direction == "before":
                return anchor_date - delta
            else:
                return anchor_date + delta

    # -------------------------
    # 4. Fallback (dateparser)
    # -------------------------
    parsed_dt = dateparser.parse(
        s,
        settings={
            "RELATIVE_BASE": base_dt,
            "PREFER_DATES_FROM": "future",
            "PREFER_DAY_OF_MONTH": "first",
        },
    )

    if parsed_dt:
        return parsed_dt.date()

    raise ValueError(f"Could not parse date string: {s}")
