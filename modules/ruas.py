from database.db_manager import get_connection

# 🔹 Adicionar nova rua a um território

def adicionar_rua(territorio_id, nome):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO ruas (territorio_id, nome) VALUES (?, ?)",
        (territorio_id, nome)
    )
    conn.commit()
    conn.close()


# 🔹 Listar ruas de um território

def listar_ruas(territorio_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nome FROM ruas WHERE territorio_id = ? ORDER BY nome",
        (territorio_id,)
    )
    resultados = cur.fetchall()
    conn.close()
    return resultados


# 🔹 Remover uma rua

def remover_rua(rua_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM ruas WHERE id = ?", (rua_id,))
    conn.commit()
    conn.close()