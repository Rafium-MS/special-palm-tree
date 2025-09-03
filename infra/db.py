"""Database utilities placeholder.

This module is responsible for persistence layer interactions.
"""

from __future__ import annotations

from pathlib import Path


def get_db_path(base: Path) -> Path:
    """Return the database file path under the given base directory."""
    return base / "app.db"
