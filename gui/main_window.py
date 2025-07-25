from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QApplication, QLabel
)
from gui.territorios_view import TerritoriosView
from gui.saidas_view import SaidasView
from gui.designacoes_view import DesignacoesView
from gui.relatorio_view import RelatorioView
from gui.toast_notification import ToastNotification


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Designação de Territórios")
        self.setMinimumSize(1000, 600)

        layout_principal = QHBoxLayout()
        self.setLayout(layout_principal)

        # 📚 Menu lateral
        menu_lateral = QVBoxLayout()
        self.btn_territorios = QPushButton("Territórios")
        self.btn_saidas = QPushButton("Saídas de Campo")
        self.btn_designacoes = QPushButton("Designações")
        self.btn_relatorios = QPushButton("Relatórios")

        for btn in [self.btn_territorios, self.btn_saidas, self.btn_designacoes, self.btn_relatorios]:
            btn.setMinimumHeight(40)
            menu_lateral.addWidget(btn)

        menu_lateral.addStretch()
        layout_principal.addLayout(menu_lateral, 1)

        # 🧱 Conteúdo dinâmico
        self.stack = QStackedWidget()
        self.view_territorios = TerritoriosView()
        self.view_saidas = SaidasView()
        self.view_designacoes = DesignacoesView()
        self.view_relatorios = RelatorioView()

        self.stack.addWidget(self.view_territorios)   # index 0
        self.stack.addWidget(self.view_saidas)        # index 1
        self.stack.addWidget(self.view_designacoes)   # index 2
        self.stack.addWidget(self.view_relatorios)    # index 3

        layout_principal.addWidget(self.stack, 4)

        # Após self.stack.addWidget(...)
        self.status_bar = QLabel("Pronto.")
        self.status_bar.setStyleSheet("padding: 6px; border-top: 1px solid #ccc; color: #333;")
        self.status_bar.setFixedHeight(30)

        # Envolver tudo em um layout vertical (principal)
        coluna = QVBoxLayout()
        coluna.addLayout(layout_principal)
        coluna.addWidget(self.status_bar)
        self.setLayout(coluna)

        # Conexões
        self.btn_territorios.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_saidas.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_designacoes.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.btn_relatorios.clicked.connect(lambda: self.stack.setCurrentIndex(3))

    def atualizar_status(self, mensagem, tipo="info"):
        cores = {
            "info": "#333",
            "sucesso": "#2e7d32",  # verde escuro
            "erro": "#b71c1c",  # vermelho
            "aviso": "#f9a825"  # amarelo
        }
        cor = cores.get(tipo, "#333")
        self.status_bar.setStyleSheet(f"padding:6px; border-top:1px solid #ccc; color:{cor};")
        self.status_bar.setText(mensagem)

    def show_toast(self, mensagem, tipo="info", tempo=3000):
        toast = ToastNotification(mensagem, tipo, tempo, parent=self)
        toast.show()