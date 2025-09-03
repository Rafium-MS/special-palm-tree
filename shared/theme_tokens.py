"""Design token scales for spacing, radius and z-index.

This module centralizes CSS variable values shared across themes.
"""

from __future__ import annotations

from typing import Dict

# Spacing scale --space-1..8
SPACE_SCALE: Dict[str, str] = {f"--space-{i}": f"{i * 4}px" for i in range(1, 9)}

# Border radius scale --radius-1..4
RADIUS_SCALE: Dict[str, str] = {
    "--radius-1": "2px",
    "--radius-2": "4px",
    "--radius-3": "8px",
    "--radius-4": "16px",
}

# Z-index scale --z-1..10
Z_INDEX_SCALE: Dict[str, str] = {f"--z-{i}": str(i * 10) for i in range(1, 11)}


def tokens() -> Dict[str, str]:
    """Return all token variables as a flat mapping."""

    result: Dict[str, str] = {}
    result.update(SPACE_SCALE)
    result.update(RADIUS_SCALE)
    result.update(Z_INDEX_SCALE)
    return result


__all__ = ["SPACE_SCALE", "RADIUS_SCALE", "Z_INDEX_SCALE", "tokens"]
