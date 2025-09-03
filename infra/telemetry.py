"""Simple opt-in telemetry collector.

The telemetry client stores usage metrics in a local JSON file. No data is
sent externally. Users must explicitly enable it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class Telemetry:
    """Collects usage events when ``enabled`` is true."""

    path: Path
    enabled: bool = False
    _events: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.enabled and self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                self._events = data.get("events", [])
            except Exception:
                self._events = []

    def track(self, name: str, payload: Dict[str, Any] | None = None) -> None:
        """Record an event with *name* and optional *payload*."""
        if not self.enabled:
            return
        event: Dict[str, Any] = {"name": name}
        if payload:
            event["payload"] = payload
        self._events.append(event)
        self.path.write_text(
            json.dumps({"events": self._events}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
