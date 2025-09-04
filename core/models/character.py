"""Character domain model."""

from __future__ import annotations

from typing import Optional

from pydantic import Field

from .base import BaseEntity


class Character(BaseEntity):
    """Representation of a character in the world."""

    birth_year: int = Field(ge=-10_000)
    location: Optional[str] = None
    faction: Optional[str] = None

    @property
    def age(self) -> int:
        """Return the age of the character relative to year 0."""
        return -self.birth_year


__all__ = ["Character"]

