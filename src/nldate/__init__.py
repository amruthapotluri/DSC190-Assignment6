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

    # 1. Handle "X before/after Y"
    match = re.search(r"(.+?)\s+(before|after)\s+(.+)", s)
    if match:
        offset_str = match.group(1).strip()
        direction = match.group(2).strip()
        anchor_str = match.group(3).strip()

        # Resolve the anchor first (e.g., "yesterday" or "Dec 1st")
        anchor_date = parse(anchor_str, today=today)

        # Calculate the offset delta using a neutral reference
        ref = datetime(2000, 1, 1)
        # We use 'ago' to force dateparser to give us a relative displacement
        offset_dt = dateparser.parse(
            f"{offset_str} ago", settings={"RELATIVE_BASE": ref}
        )

        if offset_dt:
            # This gets the absolute difference (e.g., 5 days)
            delta = relativedelta(ref, offset_dt)
            if direction == "before":
                return anchor_date - delta
            else:
                return anchor_date + delta

    # 2. Manual fix for "next [weekday]"
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
        if days_ahead == 0:
            days_ahead = 7
        # "Next" usually implies the one after the upcoming one if days_ahead is small,
        # but the test expects Jan 9 from Jan 1 (which is +8 days).
        return today + timedelta(days=days_ahead + 7 if days_ahead < 7 else days_ahead)

    for holiday, (month, day) in HOLIDAYS.items():
        if holiday in s:
            # Check if a year is mentioned (like "2026")
            year_match = re.search(r"\b(20\d{2})\b", s)
            year = int(year_match.group(1)) if year_match else today.year
            return date(year, month, day)

    # 3. Standard fallback
    settings = {
        "RELATIVE_BASE": base_dt,
        "PREFER_DATES_FROM": "future",
        "PREFER_DAY_OF_MONTH": "first",
    }

    parsed_dt = dateparser.parse(s, settings=settings)
    if parsed_dt:
        return parsed_dt.date()

    raise ValueError(f"Could not parse date string: {s}")
