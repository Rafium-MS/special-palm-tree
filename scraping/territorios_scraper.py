import requests
from bs4 import BeautifulSoup


def buscar_territorios():
    url = "https://territorios.congregacao-leste-scs.com.br/territorios"
    response = requests.get(url)
    response.raise_for_status()  # Garante que lançará uma exceção caso ocorra erro
    soup = BeautifulSoup(response.text, "html.parser")

    territorios = []
    # Exemplo: supondo que os dados estejam organizados em linhas de uma tabela
    for linha in soup.find_all("tr"):
        colunas = linha.find_all("td")
        if colunas:
            nome = colunas[0].get_text(strip=True)
            link_tag = colunas[0].find("a")
            link = link_tag["href"] if link_tag else None
            territorios.append({
                "nome": nome,
                "url": link
            })
    return territorios

def buscar_ruas_numeros(url_rua):
    """Exemplo simplificado de raspagem de ruas e números.

    Esta função retorna uma lista de dicionários contendo o nome da rua,
    o número e a data de coleta caso estejam disponíveis na página.
    """
    response = requests.get(url_rua)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    resultados = []
    for linha in soup.find_all("tr"):
        cols = linha.find_all("td")
        if cols:
            rua = cols[0].get_text(strip=True)
            numero = cols[1].get_text(strip=True) if len(cols) > 1 else None
            data = cols[2].get_text(strip=True) if len(cols) > 2 else    None
            resultados.append({"rua": rua, "numero": numero, "data": data})

    return resultados