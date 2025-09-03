import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.coherence import CharacterOverlap, generate_report
from core.models import Faction, TimelineEvent


def test_generate_report_detects_inconsistencies() -> None:
    events = [
        TimelineEvent(
            id="e1", title="Battle", year=10, character_ids=["c1"], location_ids=["l1"]
        ),
        TimelineEvent(
            id="e1",
            title="Battle duplicate",
            year=12,
            character_ids=["c1"],
            location_ids=["l1"],
        ),
        TimelineEvent(
            id="e2", title="Trip1", year=15, character_ids=["c1"], location_ids=["l1"]
        ),
        TimelineEvent(
            id="e3", title="Trip2", year=15, character_ids=["c1"], location_ids=["l2"]
        ),
    ]
    factions = [Faction(name="A"), Faction(name="A"), Faction(name="B")]

    report = generate_report(events, factions)

    assert report.conflicting_dates == ["e1"]
    assert CharacterOverlap("c1", 15, ["l1", "l2"]) in report.character_overlaps
    assert report.duplicate_factions == ["A"]
