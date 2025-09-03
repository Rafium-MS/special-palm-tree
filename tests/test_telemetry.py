import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from infra.telemetry import Telemetry


def test_telemetry_tracks_events(tmp_path) -> None:
    path = tmp_path / "telemetry.json"
    t = Telemetry(path, enabled=True)
    t.track("start", {"val": 1})
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["events"][0]["name"] == "start"
    assert data["events"][0]["payload"] == {"val": 1}


def test_telemetry_disabled(tmp_path) -> None:
    path = tmp_path / "telemetry.json"
    t = Telemetry(path, enabled=False)
    t.track("start")
    assert not path.exists()
