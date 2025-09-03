"""Repositories providing data access abstractions."""
from __future__ import annotations

import sqlite3

from core import models


class CharacterRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, character: models.Character) -> int:
        cur = self.conn.execute(
            "INSERT INTO characters (name, age, location, faction) VALUES (?, ?, ?, ?)",
            (character.name, character.age, character.location, character.faction),
        )
        self.conn.commit()
        return cur.lastrowid

    def list(self) -> list[models.Character]:
        cur = self.conn.execute(
            "SELECT name, age, location, faction FROM characters"
        )
        return [
            models.Character(
                name=row[0], age=row[1], location=row[2], faction=row[3]
            )
            for row in cur.fetchall()
        ]


class LocationRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, location: models.Location) -> int:
        cur = self.conn.execute(
            "INSERT INTO locations (name, population, region) VALUES (?, ?, ?)",
            (location.name, location.population, location.region),
        )
        self.conn.commit()
        return cur.lastrowid

    def list(self) -> list[models.Location]:
        cur = self.conn.execute(
            "SELECT name, population, region FROM locations"
        )
        return [
            models.Location(name=row[0], population=row[1], region=row[2])
            for row in cur.fetchall()
        ]


class FactionRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, faction: models.Faction) -> int:
        cur = self.conn.execute(
            "INSERT INTO factions (name, description) VALUES (?, ?)",
            (faction.name, faction.description),
        )
        self.conn.commit()
        return cur.lastrowid

    def list(self) -> list[models.Faction]:
        cur = self.conn.execute("SELECT name, description FROM factions")
        return [
            models.Faction(name=row[0], description=row[1])
            for row in cur.fetchall()
        ]


class EconomyProfileRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, profile: models.EconomyProfile) -> int:
        cur = self.conn.execute(
            "INSERT INTO economy_profiles (name, gdp, notes) VALUES (?, ?, ?)",
            (profile.name, profile.gdp, profile.notes),
        )
        self.conn.commit()
        return cur.lastrowid

    def list(self) -> list[models.EconomyProfile]:
        cur = self.conn.execute("SELECT name, gdp, notes FROM economy_profiles")
        return [
            models.EconomyProfile(name=row[0], gdp=row[1], notes=row[2])
            for row in cur.fetchall()
        ]


class TimelineEventRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, event: models.TimelineEvent) -> int:
        cur = self.conn.execute(
            "INSERT INTO timeline_events (description, year, location, factions) VALUES (?, ?, ?, ?)",
            (
                event.description,
                event.year,
                event.location,
                ",".join(event.factions_involved),
            ),
        )
        self.conn.commit()
        return cur.lastrowid

    def list(self) -> list[models.TimelineEvent]:
        cur = self.conn.execute(
            "SELECT description, year, location, factions FROM timeline_events"
        )
        return [
            models.TimelineEvent(
                description=row[0],
                year=row[1],
                location=row[2],
                factions_involved=[f for f in row[3].split(",") if f],
            )
            for row in cur.fetchall()
        ]


class WorldRepo:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, world: models.World) -> int:
        cur = self.conn.execute(
            "INSERT INTO worlds (name, description) VALUES (?, ?)",
            (world.name, world.description),
        )
        self.conn.commit()
        return cur.lastrowid

    def list(self) -> list[models.World]:
        cur = self.conn.execute("SELECT name, description FROM worlds")
        return [
            models.World(name=row[0], description=row[1])
            for row in cur.fetchall()
        ]
