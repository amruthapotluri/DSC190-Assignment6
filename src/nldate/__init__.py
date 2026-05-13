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

    # 1. Handle Holidays manually
    for holiday, (month, day) in HOLIDAYS.items():
        if holiday in s:
            year_match = re.search(r"\b(20\d{2})\b", s)
            year = int(year_match.group(1)) if year_match else today.year
            return date(year, month, day)

    # 2. Handle "X before/after Y"
    match = re.search(r"(.+?)\s+\b(before|after)\b\s+(.+)", s)
    if match:
        offset_str = match.group(1).strip()
        direction = match.group(2).strip()
        anchor_str = match.group(3).strip()

        # Recursive call to resolve the anchor (e.g., "yesterday")
        anchor_date = parse(anchor_str, today=today)

        # Calculate the offset delta using a neutral reference date
        ref = datetime(2000, 1, 1)
        offset_dt = dateparser.parse(
            f"{offset_str} ago", settings={"RELATIVE_BASE": ref}
        )

        if offset_dt:
            delta = relativedelta(ref, offset_dt)
            if direction == "before":
                return anchor_date - delta
            return anchor_date + delta

    # 3. Manual fix for "next [weekday]" to ensure it hits the following week
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
        current_wd = today.weekday()
        # Calculate days until that weekday (0-6) and add 7 to force next week
        days_ahead = (target_wd - current_wd) % 7
        return today + timedelta(days=days_ahead + 7)

    # 4. Standard fallback using dateparser
    settings = {
        "RELATIVE_BASE": base_dt,
        "PREFER_DATES_FROM": "future",
        "PREFER_DAY_OF_MONTH": "first",
    }

    parsed_dt = dateparser.parse(s, settings=settings)
    if parsed_dt:
        return parsed_dt.date()

    raise ValueError(f"Could not parse date string: {s}")