import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
from database.db_manager import get_connection
import pandas as pd
from database.db_manager import get_connection

# 🔹 Gerar relatório de designações por mês e ano
def gerar_relatorio_mensal(mes, ano):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT s.grupo, t.nome AS territorio, d.data_inicio, d.data_fim, d.status
        FROM designacoes d
        JOIN saidas_campo s ON d.saida_id = s.id
        JOIN territorios t ON d.territorio_id = t.id
        WHERE strftime('%m', d.data_inicio) = ? AND strftime('%Y', d.data_inicio) = ?
        ORDER BY s.grupo, d.data_inicio
    """, (f"{int(mes):02d}", str(ano)))

    dados = cur.fetchall()
    conn.close()

    colunas = ["Grupo", "Território", "Início", "Fim", "Status"]
    df = pd.DataFrame(dados, columns=colunas)
    return df

# 🔹 Exportar relatório mensal para Excel
def exportar_relatorio_excel(mes, ano, caminho_arquivo=None):
    df = gerar_relatorio_mensal(mes, ano)
    if df.empty:
        print("Nenhuma designação encontrada para esse período.")
        return None

    if not caminho_arquivo:
        caminho_arquivo = f"relatorio_{ano}_{int(mes):02d}.xlsx"

    df.to_excel(caminho_arquivo, index=False)
    print(f"Relatório exportado para {caminho_arquivo}")
    return caminho_arquivo

# 🔹 Relatório por território (histórico completo de designações)
def relatorio_por_territorio(territorio_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT t.nome AS territorio, s.grupo, d.data_inicio, d.data_fim, d.status
        FROM designacoes d
        JOIN saidas_campo s ON d.saida_id = s.id
        JOIN territorios t ON d.territorio_id = t.id
        WHERE t.id = ?
        ORDER BY d.data_inicio DESC
    """, (territorio_id,))

    dados = cur.fetchall()
    conn.close()

    colunas = ["Território", "Grupo", "Início", "Fim", "Status"]
    df = pd.DataFrame(dados, columns=colunas)
    return df


def cabecalho_rodape(canvas_obj, doc, mes, ano, logo_path="assets/logo.png"):
    canvas_obj.saveState()

    largura, altura = A4

    # Cabeçalho com logo
    if os.path.exists(logo_path):
        canvas_obj.drawImage(logo_path, x=1.5 * cm, y=altura - 3 * cm, width=3 * cm, height=3 * cm, mask='auto')

    canvas_obj.setFont("Helvetica-Bold", 12)
    canvas_obj.drawString(5.5 * cm, altura - 2 * cm, f"Relatório de Designações – {int(mes):02d}/{ano}")

    # Rodapé com data e número da página
    canvas_obj.setFont("Helvetica", 8)
    data_str = datetime.now().strftime("%d/%m/%Y %H:%M")
    canvas_obj.drawRightString(largura - 1.5 * cm, 1.5 * cm, f"Gerado em: {data_str}")
    canvas_obj.drawString(1.5 * cm, 1.5 * cm, f"Página {canvas_obj.getPageNumber()}")

    canvas_obj.restoreState()

def exportar_relatorio_pdf(mes, ano, caminho_arquivo=None, logo_path="assets/logo.png"):
    df = gerar_relatorio_mensal(mes, ano)
    if df.empty:
        print("Nenhuma designação encontrada para esse período.")
        return None

    if not caminho_arquivo:
        caminho_arquivo = f"relatorio_{ano}_{int(mes):02d}.pdf"

    doc = SimpleDocTemplate(caminho_arquivo, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=4*cm, bottomMargin=2.5*cm)

    elementos = []
    estilos = getSampleStyleSheet()

    elementos.append(Spacer(1, 12))

    # Tabela de dados
    dados = [df.columns.tolist()] + df.values.tolist()
    tabela = Table(dados, repeatRows=1)

    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
    ]))

    elementos.append(tabela)

    doc.build(
        elementos,
        onFirstPage=lambda c, d: cabecalho_rodape(c, d, mes, ano, logo_path),
        onLaterPages=lambda c, d: cabecalho_rodape(c, d, mes, ano, logo_path)
    )

    print(f"Relatório PDF gerado com sucesso: {caminho_arquivo}")
    return caminho_arquivo


def obter_historico_numeros_por_territorio(territorio_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT t.nome as territorio, r.nome as rua, n.numero, n.tipo, n.status, n.data, n.data_coleta
        FROM numeros n
        JOIN ruas r ON n.rua_id = r.id
        JOIN territorios t ON r.territorio_id = t.id
        WHERE t.id = ?
        ORDER BY r.nome, n.numero, n.data_coleta DESC
    """, (territorio_id,))

    resultados = cur.fetchall()
    conn.close()
    return resultados