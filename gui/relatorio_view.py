from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QComboBox, QTableWidget, QTableWidgetItem, QFileDialog
)
from modules.relatorios import gerar_relatorio_mensal, exportar_relatorio_pdf, exportar_relatorio_excel
from datetime import datetime
from gui.notificacoes import sucesso, erro, aviso

""" 
- adicionar toast_notification
- adicionar logger
- adicionar Barra de Status
- adicionar notificações
"""

class RelatorioView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Relatório de Designações")
        self.setMinimumWidth(700)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Seleção de mês e ano
        selecao_layout = QHBoxLayout()
        self.combo_mes = QComboBox()
        self.combo_ano = QComboBox()
        self.combo_mes.addItems([f"{i:02d}" for i in range(1, 13)])
        ano_atual = datetime.now().year
        self.combo_ano.addItems([str(ano_atual - 1), str(ano_atual), str(ano_atual + 1)])
        self.combo_mes.setCurrentIndex(datetime.now().month - 1)
        self.combo_ano.setCurrentText(str(ano_atual))

        selecao_layout.addWidget(QLabel("Mês:"))
        selecao_layout.addWidget(self.combo_mes)
        selecao_layout.addWidget(QLabel("Ano:"))
        selecao_layout.addWidget(self.combo_ano)

        self.layout.addLayout(selecao_layout)

        # Botões
        botoes_layout = QHBoxLayout()
        self.btn_gerar = QPushButton("Gerar Relatório")
        self.btn_exportar_pdf = QPushButton("Exportar PDF")
        self.btn_exportar_excel = QPushButton("Exportar Excel")
        botoes_layout.addWidget(self.btn_gerar)
        botoes_layout.addWidget(self.btn_exportar_pdf)
        botoes_layout.addWidget(self.btn_exportar_excel)
        self.layout.addLayout(botoes_layout)

        # Tabela
        self.tabela = QTableWidget()
        self.layout.addWidget(self.tabela)

        # Conexões
        self.btn_gerar.clicked.connect(self.carregar_tabela)
        self.btn_exportar_pdf.clicked.connect(self.salvar_pdf)
        self.btn_exportar_excel.clicked.connect(self.salvar_excel)

    def get_mes_ano(self):
        return self.combo_mes.currentText(), int(self.combo_ano.currentText())

    def carregar_tabela(self):
        mes, ano = self.get_mes_ano()
        df = gerar_relatorio_mensal(mes, ano)

        self.tabela.clear()
        self.tabela.setRowCount(0)
        self.tabela.setColumnCount(len(df.columns))
        self.tabela.setHorizontalHeaderLabels(df.columns.tolist())

        for i, linha in enumerate(df.values.tolist()):
            self.tabela.insertRow(i)
            for j, valor in enumerate(linha):
                self.tabela.setItem(i, j, QTableWidgetItem(str(valor)))

    def salvar_pdf(self):
        mes, ano = self.get_mes_ano()
        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar PDF", f"relatorio_{ano}_{mes}.pdf", "PDF (*.pdf)")
        if caminho:
            exportar_relatorio_pdf(mes, ano, caminho)

    def salvar_excel(self):
        mes, ano = self.get_mes_ano()
        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar Excel", f"relatorio_{ano}_{mes}.xlsx", "Excel (*.xlsx)")
        if caminho:
            exportar_relatorio_excel(mes, ano, caminho)
