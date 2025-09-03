from __future__ import annotations

import sqlite3

from core import models


class WorldRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, world: models.World) -> int:
        cur = self.conn.execute(
            "INSERT INTO worlds (name, description) VALUES (?, ?)",
            (world.name, world.description),
        )
        return cur.lastrowid

    def find(self, world_id: int) -> models.World | None:
        cur = self.conn.execute(
            "SELECT name, description FROM worlds WHERE id = ?",
            (world_id,),
        )
        row = cur.fetchone()
        if row:
            return models.World(name=row["name"], description=row["description"])
        return None

    def list(self) -> list[models.World]:
        cur = self.conn.execute("SELECT name, description FROM worlds")
        return [
            models.World(name=row["name"], description=row["description"])
            for row in cur.fetchall()
        ]
