from datetime import date

from shared.date_utils import days_between, format_date, parse_date


def test_parse_and_format():
    d = parse_date("2023-01-15")
    assert d.year == 2023 and d.month == 1 and d.day == 15
    assert format_date(d) == "2023-01-15"


def test_days_between():
    d1 = parse_date("2023-01-01")
    d2 = parse_date("2023-01-31")
    assert days_between(d1, d2) == 30
