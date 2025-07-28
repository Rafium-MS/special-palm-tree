import requests
from bs4 import BeautifulSoup
from database.db_manager import get_connection
from utils.logger import log
import schedule
import time
from threading import Thread

# 📥 Buscar todos os territórios e seus links
def buscar_territorios():
    url = "https://territorios.congregacao-leste-scs.com.br/territorios"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    territorios = []
    for linha in soup.find_all("tr"):
        colunas = linha.find_all("td")
        if colunas:
            nome = colunas[0].get_text(strip=True)
            link_tag = colunas[0].find("a")
            link = link_tag["href"] if link_tag else None
            territorios.append({"nome": nome, "url": link})
    return territorios

# 📥 Buscar as ruas de um território
def buscar_ruas(territorio_url):
    response = requests.get(territorio_url)
    soup = BeautifulSoup(response.text, "html.parser")
    ruas = []

    for link in soup.select("a[href*='/territorios/rua/']"):
        nome = link.text.strip()
        url = link["href"]
        ruas.append({"nome": nome, "url": url})
    return ruas

# 📥 Buscar os números da rua
def buscar_numeros(url_rua):
    response = requests.get(url_rua)
    soup = BeautifulSoup(response.text, "html.parser")
    resultados = []

    for linha in soup.find_all("tr"):
        cols = linha.find_all("td")
        if cols:
            numero = cols[0].get_text(strip=True)
            tipo = cols[1].get_text(strip=True) if len(cols) > 1 else ""
            status = cols[2].get_text(strip=True) if len(cols) > 2 else ""
            data = cols[3].get_text(strip=True) if len(cols) > 3 else ""
            resultados.append({
                "numero": numero,
                "tipo": tipo,
                "status": status,
                "data": data
            })
    return resultados

# 💾 Salvar todos os dados no banco
def salvar_no_banco(territorios):
    conn = get_connection()
    cur = conn.cursor()
    novos = 0

    for t in territorios:
        cur.execute("SELECT id FROM territorios WHERE nome = ?", (t['nome'],))
        row = cur.fetchone()
        if row:
            territorio_id = row[0]
        else:
            cur.execute("INSERT INTO territorios (nome, url) VALUES (?, ?)", (t['nome'], t['url']))
            territorio_id = cur.lastrowid
            novos += 1
            log(f"Novo território inserido: {t['nome']}")

        if t['url']:
            try:
                ruas = buscar_ruas(t['url'])
                for r in ruas:
                    cur.execute("SELECT id FROM ruas WHERE nome = ? AND territorio_id = ?", (r['nome'], territorio_id))
                    rua_row = cur.fetchone()
                    if rua_row:
                        rua_id = rua_row[0]
                    else:
                        cur.execute("INSERT INTO ruas (nome, url, territorio_id) VALUES (?, ?, ?)", (r['nome'], r['url'], territorio_id))
                        rua_id = cur.lastrowid

                    # Buscar números de cada rua
                    numeros = buscar_numeros(r['url'])
                    for n in numeros:
                        cur.execute("""
                            INSERT INTO numeros (rua_id, numero, tipo, status, data)
                            VALUES (?, ?, ?, ?, ?)
                        """, (rua_id, n['numero'], n['tipo'], n['status'], n['data']))
            except Exception as e:
                log(f"Erro ao buscar ruas do território {t['nome']}: {str(e)}", tipo="erro")

    conn.commit()
    conn.close()
    log(f"Importação concluída. {novos} novos territórios adicionados.")

# ▶️ Execução direta
def executar_scraper():
    try:
        territorios = buscar_territorios()
        salvar_no_banco(territorios)
    except Exception as e:
        log(f"Erro na execução do scraper: {str(e)}", tipo="erro")

# 🖼️ Com feedback visual (para uso com interface)
def executar_scraper_com_interface(parent=None):
    from gui.toast_notification import ToastNotification

    def show_toast(msg, tipo="info"):
        if parent:
            toast = ToastNotification(msg, tipo, parent=parent)
            toast.show()

    try:
        show_toast("Importando territórios...", "info")
        territorios = buscar_territorios()
        salvar_no_banco(territorios)
        show_toast("Importação concluída com sucesso.", "sucesso")
    except Exception as e:
        log(f"Erro na execução do scraper: {str(e)}", tipo="erro")
        show_toast("Erro ao importar territórios!", "erro")

# 🕒 Agendamento diário automático
def agendar_execucao_diaria():
    schedule.every().day.at("17:00").do(executar_scraper)
    while True:
        schedule.run_pending()
        time.sleep(60)

# Executar agendador se chamado diretamente
if __name__ == "__main__":
    Thread(target=agendar_execucao_diaria, daemon=True).start()
    executar_scraper()
