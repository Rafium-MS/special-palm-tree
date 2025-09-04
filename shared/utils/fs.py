"""Filesystem-related utilities."""

from pathlib import Path


def ensure_dir(p: Path) -> None:
    """Create directory *p* and parents if needed."""
    p.mkdir(parents=True, exist_ok=True)


__all__ = ["ensure_dir"]

