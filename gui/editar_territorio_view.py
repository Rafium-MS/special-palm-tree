from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QLineEdit, QTextEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QMessageBox
)
from PyQt5.QtSvg import QSvgWidget
import os
import re
from modules.territorios import obter_territorio_completo
from database.db_manager import get_connection


class EditarTerritorioView(QDialog):
    def __init__(self, territorio_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edição Detalhada do Território")
        self.setMinimumSize(800, 600)
        self.territorio_id = territorio_id
        self.territorio = obter_territorio_completo(territorio_id)
        self.rua_selecionada_id = None

        self.tabs = QTabWidget(self)
        self.tab_dados = self.criar_tab_dados()
        self.tab_ruas = self.criar_tab_ruas()
        self.tab_numeros = self.criar_tab_numeros()

        self.tabs.addTab(self.tab_dados, "Dados Gerais")
        self.tabs.addTab(self.tab_ruas, "Ruas")
        self.tabs.addTab(self.tab_numeros, "Números")

        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)

    # ─────────────── 🧾 Aba 1 ─────────────── #
    def criar_tab_dados(self):
        widget = QVBoxLayout()

        self.nome_input = QLineEdit(self.territorio['nome'])
        self.url_input = QLineEdit(self.territorio['url'])
        self.status_input = QComboBox()
        self.status_input.addItems(["novo", "em uso", "designado", "completo"])
        self.status_input.setCurrentText(self.territorio['status'])
        self.obs_input = QTextEdit(self.territorio['observacoes'] or "")

        widget.addWidget(QLabel("Nome:"))
        widget.addWidget(self.nome_input)
        widget.addWidget(QLabel("URL:"))
        widget.addWidget(self.url_input)
        widget.addWidget(QLabel("Status:"))
        widget.addWidget(self.status_input)
        widget.addWidget(QLabel("Observações:"))
        widget.addWidget(self.obs_input)

        widget.addWidget(QLabel("Pré-visualização do Mapa:"))
        self.svg_widget = QSvgWidget()
        self.svg_widget.setMinimumHeight(200)
        widget.addWidget(self.svg_widget)
        self.atualizar_svg_preview()

        container = QDialog()
        container.setLayout(widget)
        return container

    def atualizar_svg_preview(self):
        nome = self.territorio['nome']
        match = re.search(r"(\d+)", nome)
        if match:
            numero = match.group(1)
            caminho = f"mapas/mini/{numero}.svg"
            if os.path.exists(caminho):
                self.svg_widget.load(caminho)

    # ─────────────── 🛤️ Aba 2 ─────────────── #
    def criar_tab_ruas(self):
        layout = QVBoxLayout()
        self.tabela_ruas = QTableWidget()
        self.tabela_ruas.setColumnCount(2)
        self.tabela_ruas.setHorizontalHeaderLabels(["ID", "Nome"])
        layout.addWidget(self.tabela_ruas)

        botoes = QHBoxLayout()
        btn_add = QPushButton("Adicionar")
        btn_edit = QPushButton("Editar")
        btn_del = QPushButton("Remover")
        botoes.addWidget(btn_add)
        botoes.addWidget(btn_edit)
        botoes.addWidget(btn_del)
        layout.addLayout(botoes)

        btn_add.clicked.connect(self.adicionar_rua)
        btn_edit.clicked.connect(self.editar_rua)
        btn_del.clicked.connect(self.remover_rua)

        self.carregar_ruas()
        container = QDialog()
        container.setLayout(layout)
        return container

    def carregar_ruas(self):
        self.tabela_ruas.setRowCount(len(self.territorio['ruas']))
        for i, rua in enumerate(self.territorio['ruas']):
            self.tabela_ruas.setItem(i, 0, QTableWidgetItem(str(rua["id"])))
            self.tabela_ruas.setItem(i, 1, QTableWidgetItem(rua["nome"]))

    def adicionar_rua(self):
        nome, ok = QLineEdit.getText(self, "Nova Rua", "Nome:")
        if ok and nome.strip():
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO ruas (nome, territorio_id) VALUES (?, ?)", (nome.strip(), self.territorio_id))
            conn.commit()
            conn.close()
            self.territorio = obter_territorio_completo(self.territorio_id)
            self.carregar_ruas()

    def editar_rua(self):
        linha = self.tabela_ruas.currentRow()
        if linha < 0:
            return
        id_rua = int(self.tabela_ruas.item(linha, 0).text())
        nome_atual = self.tabela_ruas.item(linha, 1).text()
        nome, ok = QLineEdit.getText(self, "Editar Rua", "Novo nome:", text=nome_atual)
        if ok and nome.strip():
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("UPDATE ruas SET nome = ? WHERE id = ?", (nome.strip(), id_rua))
            conn.commit()
            conn.close()
            self.territorio = obter_territorio_completo(self.territorio_id)
            self.carregar_ruas()

    def remover_rua(self):
        linha = self.tabela_ruas.currentRow()
        if linha < 0:
            return
        id_rua = int(self.tabela_ruas.item(linha, 0).text())
        confirm = QMessageBox.question(self, "Confirmar", "Deseja realmente remover esta rua?")
        if confirm == QMessageBox.Yes:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM ruas WHERE id = ?", (id_rua,))
            conn.commit()
            conn.close()
            self.territorio = obter_territorio_completo(self.territorio_id)
            self.carregar_ruas()

    # ─────────────── #️⃣ Aba 3 ─────────────── #
    def criar_tab_numeros(self):
        layout = QVBoxLayout()

        self.rua_combo = QComboBox()
        self.rua_combo.addItems([r['nome'] for r in self.territorio['ruas']])
        self.rua_combo.currentIndexChanged.connect(self.carregar_numeros)
        layout.addWidget(QLabel("Selecionar Rua:"))
        layout.addWidget(self.rua_combo)

        self.tabela_numeros = QTableWidget()
        self.tabela_numeros.setColumnCount(4)
        self.tabela_numeros.setHorizontalHeaderLabels(["ID", "Número", "Tipo", "Data"])
        layout.addWidget(self.tabela_numeros)

        botoes = QHBoxLayout()
        btn_add = QPushButton("Adicionar")
        btn_edit = QPushButton("Editar")
        btn_del = QPushButton("Remover")
        botoes.addWidget(btn_add)
        botoes.addWidget(btn_edit)
        botoes.addWidget(btn_del)
        layout.addLayout(botoes)

        btn_add.clicked.connect(self.adicionar_numero)
        btn_edit.clicked.connect(self.editar_numero)
        btn_del.clicked.connect(self.remover_numero)

        self.carregar_numeros()
        container = QDialog()
        container.setLayout(layout)
        return container

    def carregar_numeros(self):
        idx = self.rua_combo.currentIndex()
        if idx < 0:
            return
        rua = self.territorio['ruas'][idx]
        self.rua_selecionada_id = rua['id']
        numeros = rua['numeros']
        self.tabela_numeros.setRowCount(len(numeros))
        for i, n in enumerate(numeros):
            self.tabela_numeros.setItem(i, 0, QTableWidgetItem(str(n['id'])))
            self.tabela_numeros.setItem(i, 1, QTableWidgetItem(str(n['numero'])))
            self.tabela_numeros.setItem(i, 2, QTableWidgetItem(n.get('tipo', '')))
            self.tabela_numeros.setItem(i, 3, QTableWidgetItem(n.get('data', '')))

    def adicionar_numero(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO numeros (rua_id, numero, tipo, status, data) VALUES (?, ?, ?, ?, ?)",
                    (self.rua_selecionada_id, "0", "", "", ""))
        conn.commit()
        conn.close()
        self.territorio = obter_territorio_completo(self.territorio_id)
        self.carregar_numeros()

    def editar_numero(self):
        linha = self.tabela_numeros.currentRow()
        if linha < 0:
            return
        id_num = int(self.tabela_numeros.item(linha, 0).text())
        novo = self.tabela_numeros.item(linha, 1).text()
        tipo = self.tabela_numeros.item(linha, 2).text()
        data = self.tabela_numeros.item(linha, 3).text()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE numeros SET numero = ?, tipo = ?, data = ? WHERE id = ?", (novo, tipo, data, id_num))
        conn.commit()
        conn.close()
        self.territorio = obter_territorio_completo(self.territorio_id)
        self.carregar_numeros()

    def remover_numero(self):
        linha = self.tabela_numeros.currentRow()
        if linha < 0:
            return
        id_num = int(self.tabela_numeros.item(linha, 0).text())
        confirm = QMessageBox.question(self, "Confirmar", "Remover este número?")
        if confirm == QMessageBox.Yes:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM numeros WHERE id = ?", (id_num,))
            conn.commit()
            conn.close()
            self.territorio = obter_territorio_completo(self.territorio_id)
            self.carregar_numeros()
