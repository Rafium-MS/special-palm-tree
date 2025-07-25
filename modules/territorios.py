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
# 🔹 Obter território completo com ruas e números
def obter_territorio_completo(territorio_id):
    """Retorna um dicionário com o território, suas ruas e números."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT t.id, t.nome, t.url, t.status, t.observacoes,
               r.id as rua_id, r.nome as rua_nome,
               n.id as numero_id, n.numero, n.data
        FROM territorios t
        LEFT JOIN ruas r ON r.territorio_id = t.id
        LEFT JOIN numeros n ON n.rua_id = r.id
        WHERE t.id = ?
        ORDER BY r.nome, n.numero
        """,
        (territorio_id,)
    )
    linhas = cur.fetchall()
    conn.close()

    if not linhas:
        return None

    # Informações básicas do território
    territorio = {
        "id": linhas[0][0],
        "nome": linhas[0][1],
        "url": linhas[0][2],
        "status": linhas[0][3],
        "observacoes": linhas[0][4],
        "ruas": [],
    }

    ruas_dict = {}
    for (_, _, _, _, _, rua_id, rua_nome, numero_id, numero, data) in linhas:
        if rua_id is None:
            continue
        if rua_id not in ruas_dict:
            rua = {"id": rua_id, "nome": rua_nome, "numeros": []}
            ruas_dict[rua_id] = rua
            territorio["ruas"].append(rua)
        if numero_id is not None:
            ruas_dict[rua_id]["numeros"].append(
                {"id": numero_id, "numero": numero, "data": data}
            )

    return territorio