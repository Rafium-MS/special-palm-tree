from __future__ import annotations

import sqlite3

from core import models


class EconomyProfileRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, profile: models.EconomyProfile) -> int:
        cur = self.conn.execute(
            "INSERT INTO economy_profiles (name, gdp, notes) VALUES (?, ?, ?)",
            (profile.name, profile.gdp, profile.notes),
        )
        return cur.lastrowid

    def find(self, profile_id: int) -> models.EconomyProfile | None:
        cur = self.conn.execute(
            "SELECT name, gdp, notes FROM economy_profiles WHERE id = ?",
            (profile_id,),
        )
        row = cur.fetchone()
        if row:
            return models.EconomyProfile(
                name=row["name"], gdp=row["gdp"], notes=row["notes"]
            )
        return None

    def list(self) -> list[models.EconomyProfile]:
        cur = self.conn.execute("SELECT name, gdp, notes FROM economy_profiles")
        return [
            models.EconomyProfile(name=row["name"], gdp=row["gdp"], notes=row["notes"])
            for row in cur.fetchall()
        ]
