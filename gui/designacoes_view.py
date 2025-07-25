from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QDateEdit, QMessageBox
)
from PyQt5.QtCore import QDate
from modules.designacoes import (
    listar_designacoes, criar_designacao, atualizar_designacao, remover_designacao
)
from modules.territorios import listar_territorios
from modules.saidas import listar_saidas

""" 
- adicionar toast_notification
- adicionar logger

"""
class DesignacoesView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Designações de Territórios")
        self.setMinimumWidth(900)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 🔽 Seletores
        form_layout = QHBoxLayout()

        self.combo_territorio = QComboBox()
        self.combo_saida = QComboBox()
        self.data_inicio = QDateEdit()
        self.data_fim = QDateEdit()
        self.status_combo = QComboBox()

        self.data_inicio.setDate(QDate.currentDate())
        self.data_fim.setDate(QDate.currentDate())
        self.data_inicio.setCalendarPopup(True)
        self.data_fim.setCalendarPopup(True)

        self.status_combo.addItems(["pendente", "concluída", "cancelada"])

        form_layout.addWidget(QLabel("Território:"))
        form_layout.addWidget(self.combo_territorio)
        form_layout.addWidget(QLabel("Saída:"))
        form_layout.addWidget(self.combo_saida)
        form_layout.addWidget(QLabel("Início:"))
        form_layout.addWidget(self.data_inicio)
        form_layout.addWidget(QLabel("Fim:"))
        form_layout.addWidget(self.data_fim)
        form_layout.addWidget(QLabel("Status:"))
        form_layout.addWidget(self.status_combo)

        self.layout.addLayout(form_layout)

        # Botões
        botoes_layout = QHBoxLayout()
        self.btn_adicionar = QPushButton("Adicionar")
        self.btn_atualizar = QPushButton("Atualizar Status")
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

        self.id_map_territorio = {}  # nome -> id
        self.id_map_saida = {}       # descrição -> id

        self.carregar_seletores()
        self.carregar_tabela()

    def carregar_seletores(self):
        self.combo_territorio.clear()
        self.combo_saida.clear()
        self.id_map_territorio = {}
        self.id_map_saida = {}

        for id_, nome, *_ in listar_territorios():
            self.combo_territorio.addItem(nome)
            self.id_map_territorio[nome] = id_

        for id_, data, grupo, dirigente, *_ in listar_saidas():
            descricao = f"{grupo} - {data}"
            self.combo_saida.addItem(descricao)
            self.id_map_saida[descricao] = id_

    def carregar_tabela(self):
        dados = listar_designacoes()
        colunas = ["ID", "Território", "Grupo", "Data Saída", "Início", "Fim", "Status"]

        self.tabela.setColumnCount(len(colunas))
        self.tabela.setHorizontalHeaderLabels(colunas)
        self.tabela.setRowCount(len(dados))

        for i, linha in enumerate(dados):
            self.tabela.insertRow(i)
            for j, valor in enumerate(linha):
                self.tabela.setItem(i, j, QTableWidgetItem(str(valor)))

    def get_linha_selecionada(self):
        linha = self.tabela.currentRow()
        if linha < 0:
            QMessageBox.warning(self, "Aviso", "Selecione uma designação.")
            return None
        return linha

    def adicionar(self):
        nome_territorio = self.combo_territorio.currentText()
        desc_saida = self.combo_saida.currentText()

        if not nome_territorio or not desc_saida:
            QMessageBox.warning(self, "Erro", "Selecione um território e uma saída.")
            return

        territorio_id = self.id_map_territorio[nome_territorio]
        saida_id = self.id_map_saida[desc_saida]
        inicio = self.data_inicio.date().toString("yyyy-MM-dd")
        fim = self.data_fim.date().toString("yyyy-MM-dd")
        status = self.status_combo.currentText()

        criar_designacao(territorio_id, saida_id, inicio, fim, status)
        QMessageBox.information(self, "Sucesso", "Designação adicionada.")
        self.carregar_tabela()

    def atualizar(self):
        linha = self.get_linha_selecionada()
        if linha is None:
            return
        id_ = int(self.tabela.item(linha, 0).text())
        status = self.status_combo.currentText()
        atualizar_designacao(id_, status=status)
        self.carregar_tabela()

    def remover(self):
        linha = self.get_linha_selecionada()
        if linha is None:
            return
        id_ = int(self.tabela.item(linha, 0).text())
        confirma = QMessageBox.question(self, "Confirmar", f"Deseja remover a designação ID {id_}?")
        if confirma == QMessageBox.Yes:
            remover_designacao(id_)
            self.carregar_tabela()
