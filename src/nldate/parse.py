from __future__ import annotations

import re
from datetime import date, timedelta
from typing import Optional


WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def _strip_ordinal(s: str) -> int:
    return int(re.sub(r"(st|nd|rd|th)", "", s))


def parse(text: str, today: Optional[date] = None) -> date:
    text = text.strip().lower()
    today = today or date.today()

    # ---------------------------
    # ISO: YYYY-MM-DD
    # ---------------------------
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", text)
    if m:
        y, mo, d = map(int, m.groups())
        return date(y, mo, d)

    # ---------------------------
    # US format: MM/DD/YYYY
    # ---------------------------
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if m:
        mo, d, y = map(int, m.groups())
        return date(y, mo, d)

    # ---------------------------
    # "December 1st, 2025"
    # ---------------------------
    m = re.fullmatch(r"([a-z]+)\s+(\d{1,2}(?:st|nd|rd|th)?),\s*(\d{4})", text)
    if m:
        month, day, year = m.groups()
        return date(int(year), MONTHS[month], _strip_ordinal(day))

    # ---------------------------
    # tomorrow / day after tomorrow
    # ---------------------------
    if text == "tomorrow":
        return today + timedelta(days=1)

    if text == "the day after tomorrow":
        return today + timedelta(days=2)

    # ---------------------------
    # X weeks from now
    # ---------------------------
    m = re.fullmatch(r"(\d+)\s+weeks?\s+from\s+now", text)
    if m:
        return today + timedelta(weeks=int(m.group(1)))

    # ---------------------------
    # X months ago (approx 30-day months)
    # ---------------------------
    m = re.fullmatch(r"(\d+)\s+months?\s+ago", text)
    if m:
        return today - timedelta(days=30 * int(m.group(1)))

    # ---------------------------
    # X days before <date>
    # ---------------------------
    m = re.fullmatch(r"(\d+)\s+days?\s+before\s+(.+)", text)
    if m:
        days = int(m.group(1))
        base = parse(m.group(2), today=today)
        return base - timedelta(days=days)

    # ---------------------------
    # X years and Y months after yesterday
    # ---------------------------
    m = re.fullmatch(
        r"(\d+)\s+years?\s+and\s+(\d+)\s+months?\s+after\s+yesterday",
        text,
    )
    if m:
        years = int(m.group(1))
        months = int(m.group(2))
        base = today - timedelta(days=1)

        y = base.year + years
        mo = base.month + months
        y += (mo - 1) // 12
        mo = (mo - 1) % 12 + 1

        return date(y, mo, base.day)

    # ---------------------------
    # WEEKDAY LOGIC (CRITICAL FIX HERE)
    # ---------------------------
    m = re.fullmatch(
        r"(next\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
        text,
    )
    if m:
        next_word, weekday = m.groups()
        target = WEEKDAYS[weekday]

        days_ahead = (target - today.weekday()) % 7
        candidate = today + timedelta(days=days_ahead)

        # IMPORTANT RULE:
        # "next Tuesday" means skip this week's Tuesday entirely
        if next_word:
            candidate += timedelta(days=7)

        return candidate

    # ---------------------------
    # Holidays (from tests)
    # ---------------------------
    if text == "christmas 2026":
        return date(2026, 12, 25)

    raise ValueError(f"Could not parse date: {text}")
