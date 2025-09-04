"""Timeline event domain model."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class TimelineEvent(BaseModel):
    """Event registered on the timeline."""

    id: str
    title: str
    year: int
    era: Optional[str] = None
    scope: str = Field(default="local")  # local/personagem/mundo
    description: str = ""
    character_ids: List[str] = Field(default_factory=list)
    location_ids: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    @field_validator("scope")
    @classmethod
    def _validate_scope(cls, value: str) -> str:
        allowed = {"local", "personagem", "mundo"}
        if value not in allowed:
            raise ValueError(f"scope must be one of {allowed}")
        return value


__all__ = ["TimelineEvent"]

