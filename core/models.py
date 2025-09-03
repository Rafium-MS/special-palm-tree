"""Domain models for the world builder application."""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


class Character(BaseModel):
    """Representation of a character in the world."""

    name: str
    birth_year: int = Field(ge=-10_000)
    location: Optional[str] = None
    faction: Optional[str] = None

    @property
    def age(self) -> int:
        """Return the age of the character relative to year 0."""
        return -self.birth_year


class Location(BaseModel):
    name: str
    population: int = Field(ge=0)
    region: Optional[str] = None


class Faction(BaseModel):
    name: str
    description: Optional[str] = None
    allies: List[str] = Field(default_factory=list)
    enemies: List[str] = Field(default_factory=list)


class EconomyProfile(BaseModel):
    name: str
    gdp: float | None = None
    notes: Optional[str] = None


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

    @validator("scope")
    def _validate_scope(cls, value: str) -> str:
        allowed = {"local", "personagem", "mundo"}
        if value not in allowed:
            raise ValueError(f"scope must be one of {allowed}")
        return value


def validate_event_characters(
    event: TimelineEvent, characters: Dict[str, Character]
) -> None:
    """Validate that characters appear only after their birth year.

    Raises a ``ValueError`` if the event year precedes a character's birth year.
    """

    for char_id in event.character_ids:
        char = characters.get(char_id)
        if char and event.year < char.birth_year:
            raise ValueError(
                f"Character '{char.name}' appears in {event.title} before their birth"
            )


class World(BaseModel):
    name: str
    description: Optional[str] = None
