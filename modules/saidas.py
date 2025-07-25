from database.db_manager import get_connection

def criar_saida(data, grupo, dirigente=None, dirigente_fixo=False):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO saidas_campo (data, grupo, dirigente, dirigente_fixo)
        VALUES (?, ?, ?, ?)
    """, (data, grupo, dirigente, int(dirigente_fixo)))
    conn.commit()
    conn.close()


def listar_saidas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, data, grupo, dirigente, dirigente_fixo
        FROM saidas_campo
        ORDER BY data DESC
    """)
    resultados = cur.fetchall()
    conn.close()
    return resultados


def atualizar_saida(saida_id, **kwargs):
    """
    Atualiza uma saída de campo com base nos campos passados como kwargs.
    Exemplo: atualizar_saida(1, grupo="Grupo 2", dirigente_fixo=True)
    """
    campos = []
    valores = []
    for chave, valor in kwargs.items():
        campos.append(f"{chave} = ?")
        if chave == "dirigente_fixo":
            valores.append(int(bool(valor)))
        else:
            valores.append(valor)
    valores.append(saida_id)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        UPDATE saidas_campo
        SET {', '.join(campos)}
        WHERE id = ?
    """, valores)
    conn.commit()
    conn.close()


def remover_saida(saida_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM saidas_campo WHERE id = ?", (saida_id,))
    conn.commit()
    conn.close()
