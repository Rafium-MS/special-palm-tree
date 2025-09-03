from __future__ import annotations

import sqlite3

from core import models


class TimelineEventRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, event: models.TimelineEvent) -> int:
        cur = self.conn.execute(
            (
                "INSERT INTO timeline_events (id, title, year, era, scope, description, characters, locations, tags) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            ),
            (
                event.id,
                event.title,
                event.year,
                event.era,
                event.scope,
                event.description,
                ",".join(event.character_ids),
                ",".join(event.location_ids),
                ",".join(event.tags),
            ),
        )
        return cur.lastrowid

    def find(self, event_id: str) -> models.TimelineEvent | None:
        cur = self.conn.execute(
            (
                "SELECT id, title, year, era, scope, description, characters, locations, tags "
                "FROM timeline_events WHERE id = ?"
            ),
            (event_id,),
        )
        row = cur.fetchone()
        if row:
            return models.TimelineEvent(
                id=row["id"],
                title=row["title"],
                year=row["year"],
                era=row["era"],
                scope=row["scope"],
                description=row["description"],
                character_ids=[c for c in row["characters"].split(",") if c],
                location_ids=[l for l in row["locations"].split(",") if l],
                tags=[t for t in row["tags"].split(",") if t],
            )
        return None

    def list(self) -> list[models.TimelineEvent]:
        cur = self.conn.execute(
            "SELECT id, title, year, era, scope, description, characters, locations, tags FROM timeline_events"
        )
        return [
            models.TimelineEvent(
                id=row["id"],
                title=row["title"],
                year=row["year"],
                era=row["era"],
                scope=row["scope"],
                description=row["description"],
                character_ids=[c for c in row["characters"].split(",") if c],
                location_ids=[l for l in row["locations"].split(",") if l],
                tags=[t for t in row["tags"].split(",") if t],
            )
            for row in cur.fetchall()
        ]
