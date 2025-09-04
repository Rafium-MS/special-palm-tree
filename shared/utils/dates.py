"""Date manipulation utilities."""

from __future__ import annotations

from datetime import date, datetime


def parse_date(value: str, fmt: str = "%Y-%m-%d") -> date:
    """Parse *value* according to *fmt* and return a ``date`` object."""
    return datetime.strptime(value, fmt).date()


def format_date(d: date, fmt: str = "%Y-%m-%d") -> str:
    """Format ``date`` *d* according to *fmt*."""
    return d.strftime(fmt)


def days_between(a: date | str, b: date | str, fmt: str = "%Y-%m-%d") -> int:
    """Return the absolute difference in days between *a* and *b*.

    If ``a`` or ``b`` are strings they are parsed using ``parse_date`` with *fmt*.
    """
    if isinstance(a, str):
        a = parse_date(a, fmt)
    if isinstance(b, str):
        b = parse_date(b, fmt)
    return abs((b - a).days)


__all__ = ["parse_date", "format_date", "days_between"]

