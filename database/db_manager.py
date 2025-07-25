import sqlite3

DB_NAME = "designacao_territorios.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS territorios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        url TEXT,
        status TEXT DEFAULT 'novo',
        observacoes TEXT
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
