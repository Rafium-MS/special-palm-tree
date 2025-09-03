import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any

DB_FILE = Path.cwd() / "world.db"
JSON_EXPORT = Path.cwd() / "world_export.json"


def get_connection() -> sqlite3.Connection:
    """Return a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)


def init_db() -> None:
    """Create database tables if they do not exist."""
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS entity_registry(
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS governos(
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            tipo TEXT,
            nivel TEXT
        );

        CREATE TABLE IF NOT EXISTS regioes(
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            pai_id TEXT,
            FOREIGN KEY(pai_id) REFERENCES regioes(id)
        );

        CREATE TABLE IF NOT EXISTS assentamentos(
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            tipo TEXT,
            governo_id TEXT,
            regiao_id TEXT,
            independente INTEGER,
            imposto_base REAL,
            FOREIGN KEY(governo_id) REFERENCES governos(id),
            FOREIGN KEY(regiao_id) REFERENCES regioes(id)
        );

        CREATE TABLE IF NOT EXISTS relacoes_governamentais(
            id TEXT PRIMARY KEY,
            governo_a TEXT NOT NULL,
            governo_b TEXT NOT NULL,
            relacao TEXT,
            tratado TEXT,
            FOREIGN KEY(governo_a) REFERENCES governos(id),
            FOREIGN KEY(governo_b) REFERENCES governos(id)
        );

        CREATE TABLE IF NOT EXISTS ligas(
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS liga_membros(
            liga_id TEXT NOT NULL,
            governo_id TEXT NOT NULL,
            PRIMARY KEY(liga_id, governo_id),
            FOREIGN KEY(liga_id) REFERENCES ligas(id),
            FOREIGN KEY(governo_id) REFERENCES governos(id)
        );

        CREATE TABLE IF NOT EXISTS planetas(
            id TEXT PRIMARY KEY,
            nome TEXT NOT NULL,
            governo_id TEXT,
            recurso_principal TEXT,
            governo_unico INTEGER,
            FOREIGN KEY(governo_id) REFERENCES governos(id)
        );

        CREATE TABLE IF NOT EXISTS planeta_cidades(
            id TEXT PRIMARY KEY,
            planeta_id TEXT NOT NULL,
            nome TEXT NOT NULL,
            populacao INTEGER,
            papel TEXT,
            FOREIGN KEY(planeta_id) REFERENCES planetas(id)
        );

        -- Placeholder tables (kept for compatibility)
        CREATE TABLE IF NOT EXISTS personagens(
            id TEXT PRIMARY KEY,
            dados TEXT
        );

        CREATE TABLE IF NOT EXISTS economia(
            id TEXT PRIMARY KEY,
            dados TEXT
        );

        CREATE TABLE IF NOT EXISTS grupos(
            id TEXT PRIMARY KEY,
            dados TEXT
        );

        CREATE TABLE IF NOT EXISTS timeline(
            id TEXT PRIMARY KEY,
            dados TEXT
        );
        """
    )
    conn.commit()
    conn.close()


def _register_entity(entity_type: str, name: str) -> str:
    """Ensure entity with *name* has a stable UUID and return it."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM entity_registry WHERE type = ? AND name = ?",
        (entity_type, name),
    )
    row = cur.fetchone()
    if row:
        conn.close()
        return row[0]
    entity_id = str(uuid.uuid4())
    cur.execute(
        "INSERT INTO entity_registry (id, type, name) VALUES (?, ?, ?)",
        (entity_id, entity_type, name),
    )
    conn.commit()
    conn.close()
    return entity_id


def create_governo(nome: str, tipo: str | None = None, nivel: str | None = None) -> str:
    """Create a government and return its id."""
    init_db()
    gid = _register_entity("governo", nome)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO governos (id, nome, tipo, nivel) VALUES (?, ?, ?, ?)",
        (gid, nome, tipo, nivel),
    )
    conn.commit()
    conn.close()
    export_json()
    return gid


def create_assentamento(
    nome: str,
    tipo: str | None = None,
    governo_id: str | None = None,
    regiao_id: str | None = None,
    independente: bool = False,
    imposto_base: float | None = None,
) -> str:
    """Create a settlement and return its id."""
    init_db()
    sid = _register_entity("assentamento", nome)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR REPLACE INTO assentamentos
        (id, nome, tipo, governo_id, regiao_id, independente, imposto_base)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (sid, nome, tipo, governo_id, regiao_id, int(independente), imposto_base),
    )
    conn.commit()
    conn.close()
    export_json()
    return sid


def create_planeta(
    nome: str,
    governo_id: str | None = None,
    recurso_principal: str | None = None,
    governo_unico: bool = False,
) -> str:
    """Create a planet and return its id."""
    init_db()
    pid = _register_entity("planeta", nome)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR REPLACE INTO planetas
        (id, nome, governo_id, recurso_principal, governo_unico)
        VALUES (?, ?, ?, ?, ?)
        """,
        (pid, nome, governo_id, recurso_principal, int(governo_unico)),
    )
    conn.commit()
    conn.close()
    export_json()
    return pid


def export_json(file_path: Path | None = None) -> None:
    """Export all tables to a JSON file."""
    file_path = file_path or JSON_EXPORT
    conn = get_connection()
    cur = conn.cursor()
    data: dict[str, list[dict[str, Any]]] = {}
    tables = [
        "entity_registry",
        "governos",
        "regioes",
        "assentamentos",
        "relacoes_governamentais",
        "ligas",
        "liga_membros",
        "planetas",
        "planeta_cidades",
        "personagens",
        "economia",
        "grupos",
        "timeline",
    ]
    for table in tables:
        cur.execute(f"SELECT * FROM {table}")
        cols = [c[0] for c in cur.description]
        data[table] = [dict(zip(cols, row)) for row in cur.fetchall()]
    conn.close()
    file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def import_json(file_path: Path | None = None) -> None:
    """Import data from JSON file into SQLite, replacing existing rows."""
    file_path = file_path or JSON_EXPORT
    if not file_path.exists():
        return
    data = json.loads(file_path.read_text(encoding="utf-8"))
    conn = get_connection()
    cur = conn.cursor()
    for table, rows in data.items():
        if not rows:
            continue
        cols = rows[0].keys()
        placeholders = ",".join(["?" for _ in cols])
        cur.execute(f"DELETE FROM {table}")
        for row in rows:
            cur.execute(
                f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders})",
                [row[c] for c in cols],
            )
    conn.commit()
    conn.close()
