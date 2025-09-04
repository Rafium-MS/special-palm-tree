"""Location domain model."""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from .base import BaseEntity


class Location(BaseEntity):
    population: int = Field(ge=0)
    region: Optional[str] = None


__all__ = ["Location"]

