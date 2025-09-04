"""Collection of small utility helpers grouped by domain."""

from .fs import ensure_dir
from .dates import parse_date, format_date, days_between
from .text import (
    compute_stats,
    read_file_text,
    search_workspace,
    slugify,
    simple_diff,
)

__all__ = [
    "ensure_dir",
    "parse_date",
    "format_date",
    "days_between",
    "compute_stats",
    "read_file_text",
    "search_workspace",
    "slugify",
    "simple_diff",
]

