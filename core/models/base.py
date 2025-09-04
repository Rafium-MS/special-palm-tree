"""Base model definitions for domain entities."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class BaseEntity(BaseModel):
    """Common reusable fields for world entities."""

    name: str
    summary: str | None = None
    tags: List[str] = Field(default_factory=list)
    relations: List[str] = Field(default_factory=list)


__all__ = ["BaseEntity"]

