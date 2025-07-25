from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog
)
from modules.territorios import (
    listar_territorios, adicionar_territorio, atualizar_territorio,
    remover_territorio, buscar_por_nome, territorio_existe
)
from scraping.territorios_scraper import buscar_territorios
from gui.notificacoes import sucesso, erro, aviso

""" 
- adicionar toast_notification
- adicionar logger
- adicionar Barra de Status
- adicionar notificações
"""

class TerritoriosView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciar Territórios")
        self.setMinimumWidth(800)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 🔍 Campo de busca
        busca_layout = QHBoxLayout()
        self.busca_input = QLineEdit()
        self.busca_input.setPlaceholderText("Buscar por nome...")
        self.btn_buscar = QPushButton("Buscar")
        self.btn_buscar.clicked.connect(self.buscar_territorios)
        busca_layout.addWidget(QLabel("Filtro:"))
        busca_layout.addWidget(self.busca_input)
        busca_layout.addWidget(self.btn_buscar)
        self.layout.addLayout(busca_layout)

        # 📋 Tabela
        self.tabela = QTableWidget()
        self.layout.addWidget(self.tabela)

        # ➕➖ Botões
        botoes_layout = QHBoxLayout()
        self.btn_adicionar = QPushButton("Adicionar")
        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_remover = QPushButton("Remover")
        self.btn_importar = QPushButton("Importar da Web")

        self.btn_adicionar.clicked.connect(self.adicionar)
        self.btn_atualizar.clicked.connect(self.atualizar)
        self.btn_remover.clicked.connect(self.remover)
        self.btn_importar.clicked.connect(self.importar)

        botoes_layout.addWidget(self.btn_adicionar)
        botoes_layout.addWidget(self.btn_atualizar)
        botoes_layout.addWidget(self.btn_remover)
        botoes_layout.addWidget(self.btn_importar)
        self.layout.addLayout(botoes_layout)

        self.carregar_todos()

    def carregar_todos(self):
        dados = listar_territorios()
        self.mostrar_tabela(dados)

    def buscar_territorios(self):
        termo = self.busca_input.text().strip()
        if termo:
            dados = buscar_por_nome(termo)
        else:
            dados = listar_territorios()
        self.mostrar_tabela(dados)

    def mostrar_tabela(self, dados):
        self.tabela.clear()
        colunas = ["ID", "Nome", "URL", "Status", "Observações"]
        self.tabela.setColumnCount(len(colunas))
        self.tabela.setHorizontalHeaderLabels(colunas)
        self.tabela.setRowCount(len(dados))

        for i, linha in enumerate(dados):
            for j, valor in enumerate(linha):
                self.tabela.setItem(i, j, QTableWidgetItem(str(valor)))

    def get_linha_selecionada(self):
        linha = self.tabela.currentRow()
        if linha < 0:
            QMessageBox.warning(self, "Aviso", "Selecione uma linha.")
            return None
        return linha

    def adicionar(self):
        nome, ok = QInputDialog.getText(self, "Novo Território", "Nome:")
        if ok and nome.strip():
            if territorio_existe(nome.strip()):
                QMessageBox.warning(self, "Erro", "Território já existe.")
                return
            adicionar_territorio(nome.strip())
            self.carregar_todos()

    def atualizar(self):
        linha = self.get_linha_selecionada()
        if linha is None:
            return
        id_ = int(self.tabela.item(linha, 0).text())
        nome = self.tabela.item(linha, 1).text()
        url = self.tabela.item(linha, 2).text()
        status = self.tabela.item(linha, 3).text()
        obs = self.tabela.item(linha, 4).text()
        atualizar_territorio(id_, nome=nome, url=url, status=status, observacoes=obs)
        QMessageBox.information(self, "Atualizado", "Território atualizado com sucesso.")

    def remover(self):
        linha = self.get_linha_selecionada()
        if linha is None:
            return
        id_ = int(self.tabela.item(linha, 0).text())
        nome = self.tabela.item(linha, 1).text()
        confirma = QMessageBox.question(self, "Confirmar", f"Deseja remover '{nome}'?")
        if confirma == QMessageBox.Yes:
            remover_territorio(id_)
            self.carregar_todos()

    def importar(self):
        territorios = buscar_territorios()
        novos = 0
        for t in territorios:
            if not territorio_existe(t["nome"]):
                adicionar_territorio(t["nome"], url=t["url"])
                novos += 1
        QMessageBox.information(self, "Importação", f"{novos} territórios novos adicionados.")
        self.carregar_todos()
