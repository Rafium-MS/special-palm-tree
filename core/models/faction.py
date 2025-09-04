"""Faction domain model."""

from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from .base import BaseEntity


class Faction(BaseEntity):
    allies: List[str] = Field(default_factory=list)
    enemies: List[str] = Field(default_factory=list)
    crencas: Optional[str] = None
    ritos: List[str] = Field(default_factory=list)
    areas_influencia: List[str] = Field(default_factory=list)


__all__ = ["Faction"]

