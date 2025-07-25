from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QDateEdit, QMessageBox
)
from PyQt5.QtCore import QDate
from database.db_manager import get_connection
import os

class LogsView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logs do Sistema")
        self.setMinimumWidth(800)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 🔍 Filtros
        filtro_layout = QHBoxLayout()
        self.input_busca = QLineEdit()
        self.input_busca.setPlaceholderText("Buscar texto...")
        self.data_inicio = QDateEdit()
        self.data_inicio.setCalendarPopup(True)
        self.data_fim = QDateEdit()
        self.data_fim.setCalendarPopup(True)
        self.data_inicio.setDate(QDate.currentDate().addMonths(-1))
        self.data_fim.setDate(QDate.currentDate())

        btn_buscar = QPushButton("Filtrar")
        btn_buscar.clicked.connect(self.filtrar_logs)

        filtro_layout.addWidget(QLabel("Texto:"))
        filtro_layout.addWidget(self.input_busca)
        filtro_layout.addWidget(QLabel("De:"))
        filtro_layout.addWidget(self.data_inicio)
        filtro_layout.addWidget(QLabel("Até:"))
        filtro_layout.addWidget(self.data_fim)
        filtro_layout.addWidget(btn_buscar)
        self.layout.addLayout(filtro_layout)

        # 📋 Tabela de logs
        self.tabela = QTableWidget()
        self.layout.addWidget(self.tabela)

        # 📦 Logs de arquivo
        self.btn_ver_arquivo = QPushButton("Ver log do arquivo")
        self.btn_ver_arquivo.clicked.connect(self.abrir_log_arquivo)
        self.layout.addWidget(self.btn_ver_arquivo)

        self.carregar_logs()

    def carregar_logs(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, data_hora, acao FROM log_acoes ORDER BY data_hora DESC LIMIT 500")
        resultados = cur.fetchall()
        conn.close()

        self.tabela.clear()
        self.tabela.setColumnCount(3)
        self.tabela.setHorizontalHeaderLabels(["ID", "Data/Hora", "Ação"])
        self.tabela.setRowCount(len(resultados))

        for i, linha in enumerate(resultados):
            for j, valor in enumerate(linha):
                self.tabela.setItem(i, j, QTableWidgetItem(str(valor)))

    def filtrar_logs(self):
        texto = self.input_busca.text().strip().lower()
        inicio = self.data_inicio.date().toString("yyyy-MM-dd")
        fim = self.data_fim.date().toString("yyyy-MM-dd")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, data_hora, acao
            FROM log_acoes
            WHERE DATE(data_hora) BETWEEN ? AND ?
            AND LOWER(acao) LIKE ?
            ORDER BY data_hora DESC
        """, (inicio, fim, f"%{texto}%"))
        resultados = cur.fetchall()
        conn.close()

        self.tabela.setRowCount(len(resultados))
        for i, linha in enumerate(resultados):
            for j, valor in enumerate(linha):
                self.tabela.setItem(i, j, QTableWidgetItem(str(valor)))

    def abrir_log_arquivo(self):
        caminho = "logs/app.log"
        if not os.path.exists(caminho):
            QMessageBox.information(self, "Arquivo não encontrado", "O log de arquivo ainda não foi criado.")
            return

        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read()

        dlg = QMessageBox(self)
        dlg.setWindowTitle("Log do Arquivo")
        dlg.setText("Últimas entradas do log:")
        dlg.setDetailedText(conteudo[-5000:])  # mostra só os últimos 5.000 caracteres
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.exec_()
