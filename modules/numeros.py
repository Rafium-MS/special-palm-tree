from database.db_manager import get_connection

# 🔢 Adiciona número a uma rua com data opcional

def adicionar_numero(rua_id, numero, data=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO numeros (rua_id, numero, data) VALUES (?, ?, ?)",
        (rua_id, numero, data)
    )
    conn.commit()
    conn.close()


# 🔎 Lista números de uma rua

def listar_numeros(rua_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, numero, data FROM numeros WHERE rua_id = ? ORDER BY numero",
        (rua_id,)
    )
    resultados = cur.fetchall()
    conn.close()
    return resultados


# ❌ Remove número

def remover_numero(numero_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM numeros WHERE id = ?", (numero_id,))
    conn.commit()
    conn.close()