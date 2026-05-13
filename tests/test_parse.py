from datetime import date
from nldate import parse

def test_absolute_date():
    assert parse("December 1st, 2025") == date(2025, 12, 1)

def test_relative_days_before():
    today = date(2025, 12, 1)
    assert parse("5 days before December 1st, 2025", today=today) == date(2025, 11, 26)

def test_relative_to_yesterday():
    today = date(2025, 5, 20)
    # "yesterday" would be 2025-05-19. 1 year and 2 months after that:
    assert parse("1 year and 2 months after yesterday", today=today) == date(2026, 7, 19)

def test_next_tuesday():
    today = date(2024, 1, 1) # This is a Monday
    assert parse("next Tuesday", today=today) == date(2024, 1, 9)

def test_tomorrow():
    today = date(2026, 5, 12)
    assert parse("tomorrow", today=today) == date(2026, 5, 13)

def test_day_after_tomorrow():
    today = date(2026, 5, 12)
    assert parse("the day after tomorrow", today=today) == date(2026, 5, 14)

def test_formal_slashes():
    # Testing standard numeric formats
    assert parse("12/25/2026") == date(2026, 12, 25)

def test_iso_format():
    # Testing ISO-style formats
    assert parse("2026-10-31") == date(2026, 10, 31)

def test_weeks_from_now():
    today = date(2026, 1, 1)
    assert parse("3 weeks from now", today=today) == date(2026, 1, 22)

def test_months_ago():
    today = date(2026, 6, 15)
    # Testing simple subtraction without the "before" keyword
    assert parse("2 months ago", today=today) == date(2026, 4, 15)

def test_specific_holiday():
    # dateparser usually handles major holidays
    assert parse("Christmas 2026") == date(2026, 12, 25)