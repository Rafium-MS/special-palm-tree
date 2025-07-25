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
