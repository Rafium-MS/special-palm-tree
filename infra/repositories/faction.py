from __future__ import annotations

import sqlite3

from core import models


class FactionRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, faction: models.Faction) -> int:
        cur = self.conn.execute(
            "INSERT INTO factions (name, description) VALUES (?, ?)",
            (faction.name, faction.description),
        )
        return cur.lastrowid

    def find(self, faction_id: int) -> models.Faction | None:
        cur = self.conn.execute(
            "SELECT name, description FROM factions WHERE id = ?",
            (faction_id,),
        )
        row = cur.fetchone()
        if row:
            return models.Faction(name=row["name"], description=row["description"])
        return None

    def list(self) -> list[models.Faction]:
        cur = self.conn.execute("SELECT name, description FROM factions")
        return [
            models.Faction(name=row["name"], description=row["description"])
            for row in cur.fetchall()
        ]
