import requests
from bs4 import BeautifulSoup
from database.db_manager import get_connection
from utils.logger import log


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


def buscar_detalhes_territorio(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    resultados = []
    for linha in soup.find_all("tr"):
        cols = linha.find_all("td")
        if cols:
            rua = cols[0].get_text(strip=True)
            numero = cols[1].get_text(strip=True) if len(cols) > 1 else ""
            tipo = cols[2].get_text(strip=True) if len(cols) > 2 else ""
            status = cols[3].get_text(strip=True) if len(cols) > 3 else ""
            data = cols[4].get_text(strip=True) if len(cols) > 4 else ""
            resultados.append({
                "rua": rua,
                "numero": numero,
                "tipo": tipo,
                "status": status,
                "data": data
            })
    return resultados


def salvar_no_banco(territorios):
    conn = get_connection()
    cur = conn.cursor()
    novos = 0

    for t in territorios:
        # Verifica se já existe o território
        cur.execute("SELECT id FROM territorios WHERE nome = ?", (t['nome'],))
        row = cur.fetchone()
        if row:
            territorio_id = row[0]
        else:
            cur.execute("INSERT INTO territorios (nome, url) VALUES (?, ?)", (t['nome'], t['url']))
            territorio_id = cur.lastrowid
            novos += 1
            log(f"Novo território inserido: {t['nome']}")

        # Busca e insere ruas
        if t['url']:
            try:
                detalhes = buscar_detalhes_territorio(t['url'])
                for r in detalhes:
                    cur.execute("""
                        INSERT INTO ruas (territorio_id, nome, numero, tipo, status, data)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (territorio_id, r['rua'], r['numero'], r['tipo'], r['status'], r['data']))
            except Exception as e:
                log(f"Erro ao buscar ruas do território {t['nome']}: {str(e)}", tipo="erro")

    conn.commit()
    conn.close()
    log(f"Importação concluída. {novos} novos territórios adicionados.")


def executar_scraper():
    try:
        territorios = buscar_territorios()
        salvar_no_banco(territorios)
    except Exception as e:
        log(f"Erro na execução do scraper: {str(e)}", tipo="erro")

def executar_scraper_com_interface(parent=None):
    from gui.toast_notification import ToastNotification  # importa localmente

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

if __name__ == "__main__":
    executar_scraper()
