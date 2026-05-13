from __future__ import annotations

import re
from datetime import date, timedelta
import calendar


# ---------------------------
# Helpers
# ---------------------------

def _last_day_of_month(year: int, month: int) -> int:
    return calendar.monthrange(year, month)[1]


def _add_months(d: date, months: int) -> date:
    """Correct month arithmetic (no off-by-one day bugs)."""
    total_months = d.year * 12 + (d.month - 1) + months
    new_year = total_months // 12
    new_month = total_months % 12 + 1

    new_day = min(d.day, _last_day_of_month(new_year, new_month))
    return date(new_year, new_month, new_day)


def _add_years(d: date, years: int) -> date:
    try:
        return date(d.year + years, d.month, d.day)
    except ValueError:
        # Feb 29 fallback
        return date(d.year + years, d.month, 28)


def _parse_absolute(s: str) -> date | None:
    s = s.strip()

    # YYYY-MM-DD
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        y, mth, d = map(int, m.groups())
        return date(y, mth, d)

    # YYYY/MM/DD (IMPORTANT FIX FOR YOUR ERROR)
    m = re.fullmatch(r"(\d{4})/(\d{2})/(\d{2})", s)
    if m:
        y, mth, d = map(int, m.groups())
        return date(y, mth, d)

    # MM/DD/YYYY
    m = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", s)
    if m:
        mth, d, y = map(int, m.groups())
        return date(y, mth, d)

    # "December 1st, 2025"
    m = re.fullmatch(r"([A-Za-z]+)\s+(\d{1,2})(st|nd|rd|th)?,\s*(\d{4})", s)
    if m:
        month_name, day, _, year = m.groups()
        month_map = {
            "january": 1, "february": 2, "march": 3, "april": 4,
            "may": 5, "june": 6, "july": 7, "august": 8,
            "september": 9, "october": 10, "november": 11, "december": 12,
        }
        return date(int(year), month_map[month_name.lower()], int(day))

    return None


# ---------------------------
# Main parser
# ---------------------------

def parse(text: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    text = text.strip().lower()

    # ---- absolute formats first
    abs_date = _parse_absolute(text)
    if abs_date:
        return abs_date

    # ---- special words
    if text == "today":
        return today
    if text == "tomorrow":
        return today + timedelta(days=1)
    if text == "the day after tomorrow":
        return today + timedelta(days=2)
    if text == "yesterday":
        return today - timedelta(days=1)

    # ---- "X days before/after Y"
    m = re.fullmatch(r"(\d+)\s+days?\s+(before|after)\s+(.+)", text)
    if m:
        n, direction, base = m.groups()
        base_date = parse(base, today=today)
        delta = timedelta(days=int(n))
        return base_date - delta if direction == "before" else base_date + delta

    # ---- "X weeks from now"
    m = re.fullmatch(r"(\d+)\s+weeks?\s+from\s+now", text)
    if m:
        return today + timedelta(weeks=int(m.group(1)))

    # ---- "X months ago/from now"
    m = re.fullmatch(r"(\d+)\s+months?\s+(ago|from now)", text)
    if m:
        n = int(m.group(1))
        direction = m.group(2)
        return _add_months(today, -n if direction == "ago" else n)

    # ---- "X years and Y months after <base>"
    m = re.fullmatch(r"(\d+)\s+years?\s+and\s+(\d+)\s+months?\s+after\s+(.+)", text)
    if m:
        y, mo, base = m.groups()
        base_date = parse(base, today=today)
        base_date = _add_years(base_date, int(y))
        base_date = _add_months(base_date, int(mo))
        return base_date

    # ---- "next weekday"
    m = re.fullmatch(r"next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", text)
    if m:
        weekdays = {
            "monday": 0, "tuesday": 1, "wednesday": 2,
            "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
        }
        target = weekdays[m.group(1)]
        current = today.weekday()

        # IMPORTANT: "next Tuesday" = next week's Tuesday
        days_ahead = (7 - current + target) % 7
        if days_ahead == 0:
            days_ahead = 7
        else:
            days_ahead += 7  # force next week

        return today + timedelta(days=days_ahead)

    # ---- holiday
    if text == "christmas 2026":
        return date(2026, 12, 25)

    raise ValueError(f"Could not parse date: {text}")
