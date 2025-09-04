"""World domain model."""

from __future__ import annotations

from typing import Optional

from .base import BaseEntity


class World(BaseEntity):
    description: Optional[str] = None


__all__ = ["World"]

