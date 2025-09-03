"""Utilities for generating coherence reports across world data."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, List

from .models import Faction, TimelineEvent


@dataclass
class CharacterOverlap:
    """Represents a character appearing in multiple locations in the same year."""

    character: str
    year: int
    locations: List[str]


@dataclass
class CoherenceReport:
    """Aggregated inconsistencies found in the world data."""

    conflicting_dates: List[str]
    character_overlaps: List[CharacterOverlap]
    duplicate_factions: List[str]


def generate_report(
    events: Iterable[TimelineEvent], factions: Iterable[Faction]
) -> CoherenceReport:
    """Inspect *events* and *factions* to detect common consistency issues.

    The function checks for:

    * conflicting dates: multiple events with the same identifier but different years
    * character overlaps: a character assigned to different locations in the same year
    * duplicate factions: repeated faction names
    """

    conflicting: dict[str, int] = {}
    conflicting_dates: set[str] = set()
    char_year_locs: dict[str, dict[int, set[str]]] = defaultdict(
        lambda: defaultdict(set)
    )

    for ev in events:
        prev = conflicting.get(ev.id)
        if prev is not None and prev != ev.year:
            conflicting_dates.add(ev.id)
        conflicting[ev.id] = ev.year
        for char in ev.character_ids:
            char_year_locs[char][ev.year].update(ev.location_ids)

    overlaps: List[CharacterOverlap] = []
    for char, years in char_year_locs.items():
        for year, locs in years.items():
            if len(locs) > 1:
                overlaps.append(CharacterOverlap(char, year, sorted(locs)))

    faction_names: dict[str, int] = defaultdict(int)
    duplicates: List[str] = []
    for f in factions:
        faction_names[f.name] += 1
        if faction_names[f.name] == 2:
            duplicates.append(f.name)

    return CoherenceReport(
        conflicting_dates=sorted(conflicting_dates),
        character_overlaps=overlaps,
        duplicate_factions=duplicates,
    )
