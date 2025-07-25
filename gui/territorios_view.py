from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QInputDialog, QMessageBox
)
from modules.territorios import (
    listar_territorios, adicionar_territorio, atualizar_territorio,
    remover_territorio, buscar_por_nome, territorio_existe
)
from scraping.territorios_scraper import buscar_territorios
from gui.toast_notification import ToastNotification
from utils.logger import log

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


    def show_toast(self, mensagem, tipo="info"):
        parent = self.window()
        if parent and hasattr(parent, "show_toast"):
            parent.show_toast(mensagem, tipo)
        else:
            toast = ToastNotification(mensagem, tipo, parent=self)
            toast.show()

    def atualizar_status(self, mensagem, tipo="info"):
        parent = self.window()
        if parent and hasattr(parent, "atualizar_status"):
            parent.atualizar_status(mensagem, tipo)

    def carregar_todos(self):
        dados = listar_territorios()
        self.mostrar_tabela(dados)
        self.show_toast("Lista de territórios carregada.", "info")
        self.atualizar_status("Territórios carregados com sucesso.")

    def buscar_territorios(self):
        termo = self.busca_input.text().strip()
        if termo:
            dados = buscar_por_nome(termo)
            log(f"Busca por '{termo}' em territórios.")
        else:
            dados = listar_territorios()
        self.mostrar_tabela(dados)
        self.show_toast("Busca concluída.", "info")
        self.atualizar_status("Busca de territórios executada.")

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
            self.show_toast("Selecione uma linha primeiro.", "aviso")
            return None
        return linha

    def adicionar(self):
        nome, ok = QInputDialog.getText(self, "Novo Território", "Nome:")
        if ok and nome.strip():
            if territorio_existe(nome.strip()):
                self.show_toast("Território já existe.", "erro")
                log(f"Tentativa de adicionar território duplicado: {nome}", "erro")
                return
            adicionar_territorio(nome.strip())
            log(f"Território adicionado: {nome}")
            self.carregar_todos()
            self.show_toast("Território adicionado com sucesso.", "sucesso")
            self.atualizar_status(f"Território '{nome}' adicionado.", "sucesso")

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
        log(f"Território atualizado: ID={id_}, Nome={nome}")
        self.show_toast("Território atualizado com sucesso.", "sucesso")
        self.atualizar_status(f"Território '{nome}' atualizado.", "sucesso")
        self.carregar_todos()

    def remover(self):
        linha = self.get_linha_selecionada()
        if linha is None:
            return
        id_ = int(self.tabela.item(linha, 0).text())
        nome = self.tabela.item(linha, 1).text()
        confirma = QMessageBox.question(self, "Confirmar", f"Deseja remover '{nome}'?")
        if confirma == QMessageBox.Yes:
            remover_territorio(id_)
            log(f"Território removido: ID={id_}, Nome={nome}")
            self.carregar_todos()
            self.show_toast(f"'{nome}' removido com sucesso.", "sucesso")
            self.atualizar_status(f"Território '{nome}' removido.", "aviso")

    def importar(self):
        territorios = buscar_territorios()
        novos = 0
        for t in territorios:
            if not territorio_existe(t["nome"]):
                adicionar_territorio(t["nome"], url=t["url"])
                novos += 1
        log(f"Importação de territórios da web: {novos} novos adicionados.")
        self.carregar_todos()
        self.show_toast(f"{novos} novos territórios adicionados.", "sucesso" if novos else "info")
        self.atualizar_status(f"Importação concluída ({novos} novos).", "info")

