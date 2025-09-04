"""Validation utilities for domain models."""

from __future__ import annotations

from typing import Dict

from core.models import Character, TimelineEvent


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


__all__ = ["validate_event_characters"]

