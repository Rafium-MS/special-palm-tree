# Sistema de Designação de Territórios

Este repositório contém uma aplicação em Python para administração de territórios e designações de pregação. A interface foi desenvolvida com **PyQt5** e os dados são armazenados em um banco **SQLite**.

## Estrutura principal

- **database/** &ndash; funções de acesso ao banco de dados (`db_manager.py`).
- **modules/** &ndash; operações de negócio (territórios, ruas, números, saídas, designações, relatórios e sugestões).
- **gui/** &ndash; telas da aplicação em PyQt5.
- **scraping/** &ndash; scripts que coletam dados de territórios na web.
- **tests/** &ndash; arquivos de teste e exemplos de uso das funções.
- **main.py** &ndash; ponto de entrada da interface gráfica.

## Instalação

1. Crie um ambiente virtual (opcional):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   pip install PyQt5 schedule
   ```
3. Inicialize o banco de dados:
   ```bash
   python -m database.db_manager
   ```

## Utilização

- **Executar a interface gráfica**:
  ```bash
  python main.py
  ```
    Os arquivos SVG exibidos pela interface são procurados na pasta `mapas` do
  diretório raiz do projeto.
- 
- **Rodar o scraper manualmente**:
  ```bash
  python -m scraping.territorios_scraper
  ```
- **Executar os testes**:
  ```bash
  pytest
  ```

- **Atualizar um território via código**:
  ```python
  from modules.territorios import atualizar_territorio
  atualizar_territorio(1, nome="Novo Nome")
  ```
  Apenas os campos `nome`, `url`, `status` e `observacoes` podem ser alterados.

As funções de cada módulo estão comentadas no próprio código e podem ser utilizadas separadamente.
O módulo **territorios** inclui `remover_completo(id)` para excluir um território junto com ruas e números relacionados.
