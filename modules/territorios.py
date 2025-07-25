from database.db_manager import get_connection

# 🔹 Criar novo território
def adicionar_territorio(nome, url=None, status="novo", observacoes=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO territorios (nome, url, status, observacoes)
        VALUES (?, ?, ?, ?)
    """, (nome, url, status, observacoes))
    conn.commit()
    conn.close()

# 🔹 Listar todos os territórios
def listar_territorios():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nome, url, status, observacoes
        FROM territorios
        ORDER BY nome
    """)
    resultados = cur.fetchall()
    conn.close()
    return resultados

# 🔹 Atualizar território
def atualizar_territorio(territorio_id, **kwargs):
    campos = []
    valores = []
    for chave, valor in kwargs.items():
        campos.append(f"{chave} = ?")
        valores.append(valor)
    valores.append(territorio_id)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        UPDATE territorios
        SET {', '.join(campos)}
        WHERE id = ?
    """, valores)
    conn.commit()
    conn.close()

# 🔹 Remover território
def remover_territorio(territorio_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM territorios WHERE id = ?", (territorio_id,))
    conn.commit()
    conn.close()

# 🔹 Buscar território por nome
def buscar_por_nome(parte_nome):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nome, url, status, observacoes
        FROM territorios
        WHERE nome LIKE ?
        ORDER BY nome
    """, (f"%{parte_nome}%",))
    resultados = cur.fetchall()
    conn.close()
    return resultados

# 🔹 Verificar se já existe (para evitar duplicidade)
def territorio_existe(nome):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM territorios WHERE nome = ?", (nome,))
    count = cur.fetchone()[0]
    conn.close()
    return count > 0
