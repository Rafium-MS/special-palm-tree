from database.db_manager import get_connection
from datetime import datetime, timedelta

""" 
- adicionar toast_notification
- adicionar logger
- adicionar Barra de Status
- adicionar notificações
"""


# 🔹 Adicionar sugestão manual
def adicionar_sugestao(territorio_id, motivo=None, nota=0):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO sugestoes (territorio_id, motivo, nota)
        VALUES (?, ?, ?)
    """, (territorio_id, motivo, nota))
    conn.commit()
    conn.close()

# 🔹 Listar sugestões
def listar_sugestoes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.id, t.nome, s.motivo, s.nota
        FROM sugestoes s
        JOIN territorios t ON s.territorio_id = t.id
        ORDER BY s.nota DESC
    """)
    resultados = cur.fetchall()
    conn.close()
    return resultados

# 🔹 Remover sugestão
def remover_sugestao(sugestao_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sugestoes WHERE id = ?", (sugestao_id,))
    conn.commit()
    conn.close()

# 🔹 Gerar sugestões automáticas com base nas últimas designações
def gerar_sugestoes_automaticas(dias_limite=60, quantidade=10):
    """
    Sugere territórios que:
    - não foram designados nos últimos X dias
    - têm status 'novo', 'aguardando', ou nenhum
    """
    data_limite = (datetime.today() - timedelta(days=dias_limite)).strftime("%Y-%m-%d")

    conn = get_connection()
    cur = conn.cursor()

    # Seleciona territórios não designados recentemente
    cur.execute("""
        SELECT t.id, t.nome
        FROM territorios t
        LEFT JOIN (
            SELECT territorio_id, MAX(data_fim) AS ultima_data
            FROM designacoes
            GROUP BY territorio_id
        ) d ON t.id = d.territorio_id
        WHERE (
            d.ultima_data IS NULL OR d.ultima_data < ?
        ) AND (t.status IS NULL OR t.status IN ('novo', 'aguardando'))
        ORDER BY t.nome
        LIMIT ?
    """, (data_limite, quantidade))

    sugestoes = cur.fetchall()

    # Adiciona como sugestões
    for territorio_id, nome in sugestoes:
        adicionar_sugestao(territorio_id, motivo=f"Sem designação há mais de {dias_limite} dias", nota=10)

    conn.close()
    return sugestoes
