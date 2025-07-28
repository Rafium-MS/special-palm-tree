import sqlite3
import os

# Base directory of the repository (two levels above this file)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_NAME = "designacao_territorios.db"


def get_connection(path: str | None = None):
    """Return a connection to the SQLite database located at *path*.

    If *path* is not provided, the module-level ``DB_NAME`` is used. This
    allows tests to override ``DB_NAME`` dynamically. When ``path`` is a
    relative path, it is resolved relative to ``BASE_DIR``.    """
    if path is None:
        path = DB_NAME
        # Resolve relative paths to the repository base directory
        if not os.path.isabs(path):
            path = os.path.join(BASE_DIR, path)

    return sqlite3.connect(path)


def init_db(path: str = DB_NAME):
    """Initialize the database schema.

    ``path`` may be relative or absolute. Relative paths are resolved
    relative to ``BASE_DIR`` before creating the connection.
    """
    # Resolve relative path before opening the connection
    db_path = path
    if not os.path.isabs(db_path):
        db_path = os.path.join(BASE_DIR, db_path)

    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS territorios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        url TEXT,
        status TEXT DEFAULT 'novo',
        observacoes TEXT,
        ultima_atualizacao DATETIME    
        );
    """)
    cur.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_territorios_nome ON territorios(nome);"
    )
    # 🌐 Ruas pertencentes a um território
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ruas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        url TEXT,
        territorio_id INTEGER,
        FOREIGN KEY (territorio_id) REFERENCES territorios(id)
    );
    """)

    # 🔢 Números das ruas, cada um com data da última coleta
    cur.execute("""
    CREATE TABLE IF NOT EXISTS numeros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rua_id INTEGER,
        numero TEXT,
        tipo TEXT,
        status TEXT,
        data TEXT,
        data_coleta DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (rua_id) REFERENCES ruas(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS saidas_campo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data DATE NOT NULL,
        grupo TEXT NOT NULL,
        dirigente TEXT,
        dirigente_fixo BOOLEAN DEFAULT 0
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS designacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        territorio_id INTEGER NOT NULL,
        saida_id INTEGER NOT NULL,
        data_inicio DATE NOT NULL,
        data_fim DATE NOT NULL,
        status TEXT DEFAULT 'pendente',
        FOREIGN KEY (territorio_id) REFERENCES territorios(id),
        FOREIGN KEY (saida_id) REFERENCES saidas_campo(id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sugestoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        territorio_id INTEGER NOT NULL,
        motivo TEXT,
        nota INTEGER DEFAULT 0,
        FOREIGN KEY (territorio_id) REFERENCES territorios(id)
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS designacoes_otimizadas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        territorio TEXT NOT NULL,
        rua TEXT,
        numero TEXT,
        tipo TEXT,
        status TEXT,
        data_geracao DATE DEFAULT CURRENT_DATE,
        revisada BOOLEAN DEFAULT 0
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS log_acoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        acao TEXT NOT NULL,
        data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE VIEW IF NOT EXISTS relatorio_mensal_view AS
    SELECT 
        s.grupo,
        d.data_inicio,
        d.data_fim,
        t.nome AS territorio,
        d.status
    FROM designacoes d
    JOIN saidas_campo s ON d.saida_id = s.id
    JOIN territorios t ON d.territorio_id = t.id;
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Banco de dados inicializado com sucesso.")
