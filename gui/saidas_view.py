from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QDateEdit, QCheckBox, QComboBox
)
from PyQt5.QtCore import QDate
from modules.saidas import listar_saidas, criar_saida, atualizar_saida, remover_saida
from datetime import datetime
from gui.notificacoes import sucesso, erro, aviso


class SaidasView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciar Saídas de Campo")
        self.setMinimumWidth(700)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 🧾 Formulário
        form_layout = QHBoxLayout()
        self.data_edit = QDateEdit()
        self.data_edit.setDate(QDate.currentDate())
        self.data_edit.setCalendarPopup(True)

        self.grupo_input = QLineEdit()
        self.dirigente_input = QLineEdit()
        self.dirigente_fixo = QCheckBox("Dirigente Fixo")

        form_layout.addWidget(QLabel("Data:"))
        form_layout.addWidget(self.data_edit)
        form_layout.addWidget(QLabel("Grupo:"))
        form_layout.addWidget(self.grupo_input)
        form_layout.addWidget(QLabel("Dirigente:"))
        form_layout.addWidget(self.dirigente_input)
        form_layout.addWidget(self.dirigente_fixo)

        self.layout.addLayout(form_layout)

        # Botões
        botoes_layout = QHBoxLayout()
        self.btn_adicionar = QPushButton("Adicionar")
        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_remover = QPushButton("Remover")

        self.btn_adicionar.clicked.connect(self.adicionar)
        self.btn_atualizar.clicked.connect(self.atualizar)
        self.btn_remover.clicked.connect(self.remover)

        botoes_layout.addWidget(self.btn_adicionar)
        botoes_layout.addWidget(self.btn_atualizar)
        botoes_layout.addWidget(self.btn_remover)
        self.layout.addLayout(botoes_layout)

        # Tabela
        self.tabela = QTableWidget()
        self.layout.addWidget(self.tabela)

        self.carregar_tabela()

    def carregar_tabela(self):
        dados = listar_saidas()
        colunas = ["ID", "Data", "Grupo", "Dirigente", "Fixo"]
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
        data = self.data_edit.date().toString("yyyy-MM-dd")
        grupo = self.grupo_input.text().strip()
        dirigente = self.dirigente_input.text().strip()
        fixo = self.dirigente_fixo.isChecked()

        if not grupo:
            QMessageBox.warning(self, "Erro", "Informe o grupo.")
            return

        criar_saida(data, grupo, dirigente, fixo)
        self.carregar_tabela()

    def atualizar(self):
        linha = self.get_linha_selecionada()
        if linha is None:
            return

        id_ = int(self.tabela.item(linha, 0).text())
        data = self.tabela.item(linha, 1).text()
        grupo = self.tabela.item(linha, 2).text()
        dirigente = self.tabela.item(linha, 3).text()
        fixo = self.tabela.item(linha, 4).text().lower() in ("1", "true", "sim")

        atualizar_saida(id_, data=data, grupo=grupo, dirigente=dirigente, dirigente_fixo=fixo)
        QMessageBox.information(self, "Atualizado", "Saída atualizada com sucesso.")
        self.carregar_tabela()

    def remover(self):
        linha = self.get_linha_selecionada()
        if linha is None:
            return
        id_ = int(self.tabela.item(linha, 0).text())
        confirma = QMessageBox.question(self, "Confirmar", f"Remover saída ID {id_}?")
        if confirma == QMessageBox.Yes:
            remover_saida(id_)
            self.carregar_tabela()
