from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Character(BaseModel):
    name: str
    age: int = Field(ge=0)
    location: Optional[str] = None
    faction: Optional[str] = None


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
    description: str
    year: int
    location: Optional[str] = None
    factions_involved: List[str] = Field(default_factory=list)


class World(BaseModel):
    name: str
    description: Optional[str] = None
