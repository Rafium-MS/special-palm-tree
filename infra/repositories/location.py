from __future__ import annotations

import sqlite3

from core import models


class LocationRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, location: models.Location) -> int:
        cur = self.conn.execute(
            "INSERT INTO locations (name, population, region) VALUES (?, ?, ?)",
            (location.name, location.population, location.region),
        )
        return cur.lastrowid

    def find(self, location_id: int) -> models.Location | None:
        cur = self.conn.execute(
            "SELECT name, population, region FROM locations WHERE id = ?",
            (location_id,),
        )
        row = cur.fetchone()
        if row:
            return models.Location(
                name=row["name"],
                population=row["population"],
                region=row["region"],
            )
        return None

    def list(self) -> list[models.Location]:
        cur = self.conn.execute(
            "SELECT name, population, region FROM locations"
        )
        return [
            models.Location(
                name=row["name"],
                population=row["population"],
                region=row["region"],
            )
            for row in cur.fetchall()
        ]
