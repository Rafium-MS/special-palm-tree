from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from modules.sugestoes import (
    listar_sugestoes, gerar_sugestoes_automaticas,
    remover_sugestao
)

class SugestoesView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sugestões de Territórios")
        self.setMinimumWidth(600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        botoes = QHBoxLayout()
        self.btn_gerar = QPushButton("Gerar Automáticas")
        self.btn_remover = QPushButton("Remover")
        self.btn_atualizar = QPushButton("Atualizar")

        self.btn_gerar.clicked.connect(self.gerar)
        self.btn_remover.clicked.connect(self.remover)
        self.btn_atualizar.clicked.connect(self.carregar)

        botoes.addWidget(self.btn_gerar)
        botoes.addWidget(self.btn_remover)
        botoes.addWidget(self.btn_atualizar)
        self.layout.addLayout(botoes)

        self.tabela = QTableWidget()
        self.layout.addWidget(self.tabela)

        self.carregar()

    def carregar(self):
        dados = listar_sugestoes()
        colunas = ["ID", "Território", "Motivo", "Nota"]
        self.tabela.setColumnCount(len(colunas))
        self.tabela.setHorizontalHeaderLabels(colunas)
        self.tabela.setRowCount(len(dados))
        for i, linha in enumerate(dados):
            for j, valor in enumerate(linha):
                self.tabela.setItem(i, j, QTableWidgetItem(str(valor)))

    def get_linha(self):
        linha = self.tabela.currentRow()
        if linha < 0:
            QMessageBox.warning(self, "Aviso", "Selecione uma sugestão.")
            return None
        return linha

    def gerar(self):
        gerar_sugestoes_automaticas()
        self.carregar()

    def remover(self):
        linha = self.get_linha()
        if linha is None:
            return
        id_ = int(self.tabela.item(linha, 0).text())
        if QMessageBox.question(self, "Confirmar", "Remover sugestão?") == QMessageBox.Yes:
            remover_sugestao(id_)
            self.carregar()