from database.db_manager import get_connection
from datetime import datetime, timedelta

# 🔹 Criar nova designação
def criar_designacao(territorio_id, saida_id, data_inicio, data_fim, status="pendente"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO designacoes (territorio_id, saida_id, data_inicio, data_fim, status)
        VALUES (?, ?, ?, ?, ?)
    """, (territorio_id, saida_id, data_inicio, data_fim, status))
    conn.commit()
    conn.close()


# 🔹 Listar todas as designações (com nomes legíveis)
def listar_designacoes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT d.id, t.nome AS territorio, s.grupo, s.data, d.data_inicio, d.data_fim, d.status
        FROM designacoes d
        JOIN territorios t ON d.territorio_id = t.id
        JOIN saidas_campo s ON d.saida_id = s.id
        ORDER BY d.data_inicio DESC
    """)
    resultados = cur.fetchall()
    conn.close()
    return resultados


# 🔹 Atualizar designação
def atualizar_designacao(designacao_id, **kwargs):
    campos = []
    valores = []
    for chave, valor in kwargs.items():
        campos.append(f"{chave} = ?")
        valores.append(valor)
    valores.append(designacao_id)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        UPDATE designacoes
        SET {', '.join(campos)}
        WHERE id = ?
    """, valores)
    conn.commit()
    conn.close()


# 🔹 Remover designação
def remover_designacao(designacao_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM designacoes WHERE id = ?", (designacao_id,))
    conn.commit()
    conn.close()


# 🔹 Buscar designações por grupo
def buscar_por_grupo(grupo):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT d.id, t.nome, s.grupo, s.data, d.data_inicio, d.data_fim, d.status
        FROM designacoes d
        JOIN territorios t ON d.territorio_id = t.id
        JOIN saidas_campo s ON d.saida_id = s.id
        WHERE s.grupo LIKE ?
        ORDER BY d.data_inicio DESC
    """, (f"%{grupo}%",))
    resultados = cur.fetchall()
    conn.close()
    return resultados

def numero_recente(rua_id, numero, meses=3):
    """Verifica se o número foi designado nos últimos X meses."""
    conn = get_connection()
    cur = conn.cursor()

    limite = datetime.now() - timedelta(days=30*meses)
    limite_str = limite.strftime("%Y-%m-%d")

    cur.execute("""
        SELECT COUNT(*)
        FROM numeros
        WHERE rua_id = ?
        AND numero = ?
        AND DATE(data_coleta) >= DATE(?)
    """, (rua_id, numero, limite_str))

    resultado = cur.fetchone()[0]
    conn.close()

    return resultado > 0  # True se foi usado recentemente