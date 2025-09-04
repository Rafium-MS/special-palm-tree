import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.models import Character, TimelineEvent
from core.services import validate_event_characters


def test_validate_event_characters_allows_valid_event() -> None:
    char = Character(name="Alice", birth_year=-10)
    event = TimelineEvent(id="e1", title="Meeting", year=0, character_ids=["c1"])
    validate_event_characters(event, {"c1": char})


def test_validate_event_characters_raises_for_early_event() -> None:
    char = Character(name="Bob", birth_year=10)
    event = TimelineEvent(id="e1", title="Birth", year=0, character_ids=["c1"])
    with pytest.raises(ValueError):
        validate_event_characters(event, {"c1": char})
