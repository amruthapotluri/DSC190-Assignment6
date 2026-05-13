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
    # Added word boundaries \b to ensure we don't trip on words containing 'after'
    match = re.search(r"(.+?)\s+\b(before|after)\b\s+(.+)", s)
    if match:
        offset_str = match.group(1).strip()
        direction = match.group(2).strip()
        anchor_str = match.group(3).strip()

        anchor_date = parse(anchor_str, today=today)

        ref = datetime(2000, 1, 1)
        offset_dt = dateparser.parse(
            f"{offset_str} ago", settings={"RELATIVE_BASE": ref}
        )

        if offset_dt:
            delta = relativedelta(ref, offset_dt)
            return anchor_date - delta if direction == "before" else anchor_date + delta

    # 4. Standard fallback
    settings = {
        "RELATIVE_BASE": base_dt,
        "PREFER_DATES_FROM": "future",
        "PREFER_DAY_OF_MONTH": "first",
    }

    parsed_dt = dateparser.parse(s, settings=settings)
    if parsed_dt:
        return parsed_dt.date()

    raise ValueError(f"Could not parse date string: {s}")
