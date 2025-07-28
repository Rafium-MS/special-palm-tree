from database.db_manager import get_connection
ALLOWED_STATUS = {"novo", "aguardando", "em uso"}
MAX_NOME_LENGTH = 100
MAX_OBSERVACOES_LENGTH = 255


def validate_territorio(nome=None, status=None, observacoes=None):
    """Valida dados de um território.

    Parâmetros são opcionais para permitir validações parciais.
    """
    if nome is not None:
        if not str(nome).strip():
            raise ValueError("Nome não pode ser vazio")
        if len(nome) > MAX_NOME_LENGTH:
            raise ValueError("Nome excede limite de caracteres")

    if status is not None and status not in ALLOWED_STATUS:
        raise ValueError("Status inválido")

    if observacoes is not None and len(observacoes) > MAX_OBSERVACOES_LENGTH:
        raise ValueError("Observações excedem limite de caracteres")

# 🔹 Criar novo território
def adicionar_territorio(nome, url=None, status="novo", observacoes=None):
    validate_territorio(nome, status, observacoes)

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
ALLOWED_FIELDS = {"nome", "url", "status", "observacoes"}
def atualizar_territorio(territorio_id, **kwargs):
    """Atualiza um território permitindo apenas campos conhecidos."""
    validate_territorio(
        kwargs.get("nome"), kwargs.get("status"), kwargs.get("observacoes")
    )
    campos = []
    valores = {}
    for chave, valor in kwargs.items():
        if chave in ALLOWED_FIELDS:
            campos.append(f"{chave} = :{chave}")
            valores[chave] = valor

    if not campos:
        return  # nada para atualizar

    valores["id"] = territorio_id

    conn = get_connection()
    cur = conn.cursor()
    sql = f"UPDATE territorios SET {', '.join(campos)} WHERE id = :id"
    cur.execute(sql, valores)
    conn.commit()
    conn.close()

# 🔹 Remover território
def remover_territorio(territorio_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM territorios WHERE id = ?", (territorio_id,))
    conn.commit()
    conn.close()
# 🔹 Remover território com todas as ruas e números
def remover_completo(territorio_id):
    """Remove o território e todos os registros vinculados a ele."""
    conn = get_connection()
    cur = conn.cursor()
    # Exclui números associados às ruas do território
    cur.execute(
        "DELETE FROM numeros WHERE rua_id IN (SELECT id FROM ruas WHERE territorio_id = ?)",
        (territorio_id,),
    )
    # Exclui as ruas do território
    cur.execute("DELETE FROM ruas WHERE territorio_id = ?", (territorio_id,))
    # Por fim, remove o próprio território
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



# 🔢 Agrupar números por proximidade
def agrupar_por_proximidade(rua_id, passo=10):
    """Retorna listas de números agrupados por intervalos.

    Cada grupo é representado como uma tupla ("<inicio>-<fim>", [numeros]).
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT numero FROM numeros WHERE rua_id = ? ORDER BY CAST(numero AS INTEGER)",
        (rua_id,),
    )
    rows = cur.fetchall()
    conn.close()

    numeros = [int(r[0]) for r in rows if str(r[0]).isdigit()]
    if not numeros:
        return []

    inicio = ((min(numeros) - 1) // passo) * passo + 1
    fim = ((max(numeros) - 1) // passo + 1) * passo

    grupos = []
    for i in range(inicio, fim + 1, passo):
        limite = i + passo - 1
        nums = [n for n in numeros if i <= n <= limite]
        if nums:
            grupos.append((f"{i}-{limite}", nums))
    return grupos