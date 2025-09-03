from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Character(BaseModel):
    name: str
    age: int = Field(ge=0)
    city: Optional[str] = None
    faction: Optional[str] = None


class City(BaseModel):
    name: str
    population: int = Field(ge=0)
    region: Optional[str] = None


class Faction(BaseModel):
    name: str
    description: Optional[str] = None
    allies: List[str] = []
    enemies: List[str] = []


class TimelineEvent(BaseModel):
    description: str
    year: int
    city: Optional[str] = None
    factions_involved: List[str] = []
