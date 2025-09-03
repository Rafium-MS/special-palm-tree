from __future__ import annotations

import sqlite3

from core import models


class CharacterRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def create(self, character: models.Character) -> int:
        cur = self.conn.execute(
            "INSERT INTO characters (name, birth_year, location, faction) VALUES (?, ?, ?, ?)",
            (character.name, character.birth_year, character.location, character.faction),
        )
        return cur.lastrowid

    def find(self, character_id: int) -> models.Character | None:
        cur = self.conn.execute(
            "SELECT name, birth_year, location, faction FROM characters WHERE id = ?",
            (character_id,),
        )
        row = cur.fetchone()
        if row:
            return models.Character(
                name=row["name"],
                birth_year=row["birth_year"],
                location=row["location"],
                faction=row["faction"],
            )
        return None

    def list(self) -> list[models.Character]:
        cur = self.conn.execute(
            "SELECT name, birth_year, location, faction FROM characters"
        )
        return [
            models.Character(
                name=row["name"],
                birth_year=row["birth_year"],
                location=row["location"],
                faction=row["faction"],
            )
            for row in cur.fetchall()
        ]
