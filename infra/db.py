"""SQLite database helpers with migrations, seeding and backups."""
from __future__ import annotations

import atexit
import sqlite3
from datetime import datetime
from pathlib import Path

from config import settings

BASE_DIR = settings.workspace
DB_PATH = BASE_DIR / "app.db"
MIGRATIONS_DIR = Path(__file__).resolve().parent / "migrations"
BACKUP_DIR = BASE_DIR / "backups"


def connect(seed: bool = False) -> sqlite3.Connection:
    """Return a SQLite connection ensuring migrations are applied.

    If *seed* is ``True`` demo data will be inserted when the database is
    empty.
    """
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    _run_migrations(conn)
    if seed:
        seed_demo(conn)
    return conn


def _run_migrations(conn: sqlite3.Connection) -> None:
    """Apply all SQL migrations that have not yet been executed."""
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_migrations (id TEXT PRIMARY KEY)"
    )
    applied = {
        row["id"] for row in conn.execute("SELECT id FROM schema_migrations")
    }
    for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
        mig_id = path.stem
        if mig_id in applied:
            continue
        conn.executescript(path.read_text(encoding="utf-8"))
        conn.execute(
            "INSERT INTO schema_migrations (id) VALUES (?)", (mig_id,)
        )
        conn.commit()


def seed_demo(conn: sqlite3.Connection) -> None:
    """Insert demo data into empty tables."""
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM worlds")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO worlds (name, description) VALUES (?, ?)",
            ("Demo World", "Example world"),
        )

    cur.execute("SELECT COUNT(*) FROM locations")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO locations (name, population, region) VALUES (?, ?, ?)",
            ("Springfield", 0, None),
        )

    cur.execute("SELECT COUNT(*) FROM factions")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO factions (name, description) VALUES (?, ?)",
            ("Guild", "Local guild"),
        )

    cur.execute("SELECT COUNT(*) FROM characters")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO characters (name, age, location, faction) VALUES (?, ?, ?, ?)",
            ("Alice", 30, "Springfield", "Guild"),
        )

    cur.execute("SELECT COUNT(*) FROM economy_profiles")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO economy_profiles (name, gdp, notes) VALUES (?, ?, ?)",
            ("Default", 1000.0, "Example profile"),
        )

    cur.execute("SELECT COUNT(*) FROM timeline_events")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO timeline_events (description, year, location, factions) VALUES (?, ?, ?, ?)",
            ("Founding", 0, "Springfield", "Guild"),
        )

    conn.commit()


def _backup() -> None:
    """Create a timestamped backup of the database file."""
    if not DB_PATH.exists():
        return
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = BACKUP_DIR / f"app-{ts}.db"
    dest.write_bytes(DB_PATH.read_bytes())


atexit.register(_backup)
