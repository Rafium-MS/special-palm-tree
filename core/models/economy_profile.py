"""Economy profile domain model."""

from __future__ import annotations

from typing import Optional

from .base import BaseEntity


class EconomyProfile(BaseEntity):
    gdp: float | None = None
    notes: Optional[str] = None


__all__ = ["EconomyProfile"]

