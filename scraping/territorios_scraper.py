import requests
from bs4 import BeautifulSoup
from database.db_manager import get_connection
from utils.logger import log
from datetime import datetime
import json
import time
from threading import Thread
import schedule

# 📁 Ler JSON com lista de territórios
def buscar_territorios_json(caminho="territorios_lista.json"):
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)

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

            # Padronizar data
            try:
                data_formatada = datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")
            except:
                data_formatada = None

            resultados.append({
                "numero": numero,
                "tipo": tipo,
                "status": status,
                "data": data_formatada
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

                    numeros = buscar_numeros(r['url'])
                    for n in numeros:
                        cur.execute("SELECT id FROM numeros WHERE rua_id = ? AND numero = ?", (rua_id, n['numero']))
                        if cur.fetchone():
                            continue  # evita duplicatas
                        cur.execute("""
                            INSERT INTO numeros (rua_id, numero, tipo, status, data)
                            VALUES (?, ?, ?, ?, ?)
                        """, (rua_id, n['numero'], n['tipo'], n['status'], n['data']))
                        time.sleep(0.05)  # leve delay para respeitar o servidor

                # Atualiza timestamp de atualização
                agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute("UPDATE territorios SET ultima_atualizacao = ? WHERE id = ?", (agora, territorio_id))

            except Exception as e:
                log(f"Erro ao buscar ruas do território {t['nome']}: {str(e)}", tipo="erro")

    conn.commit()
    conn.close()
    log(f"Importação concluída. {novos} novos territórios adicionados.")

# ▶️ Execução direta
def executar_scraper():
    try:
        territorios = buscar_territorios_json()
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
        territorios = buscar_territorios_json()
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
