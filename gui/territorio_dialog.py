from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit,
    QLabel, QPushButton, QComboBox, QFileDialog
)
from PyQt5.QtSvg import QSvgWidget
import os
import re

class TerritorioDialog(QDialog):
    def __init__(self, parent=None, dados=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Território" if dados else "Novo Território")
        self.setMinimumSize(600, 500)

        self.dados = dados or {}

        layout = QVBoxLayout(self)

        # 🔤 Campos
        self.nome_input = QLineEdit(self.dados.get("nome", ""))
        self.url_input = QLineEdit(self.dados.get("url", ""))
        self.status_input = QComboBox()
        self.status_input.addItems(["novo", "em uso", "designado", "completo"])
        self.status_input.setCurrentText(self.dados.get("status", "novo"))
        self.obs_input = QTextEdit(self.dados.get("observacoes", ""))

        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Nome:"))
        form_layout.addWidget(self.nome_input)
        form_layout.addWidget(QLabel("URL:"))
        form_layout.addWidget(self.url_input)
        form_layout.addWidget(QLabel("Status:"))
        form_layout.addWidget(self.status_input)
        form_layout.addWidget(QLabel("Observações:"))
        form_layout.addWidget(self.obs_input)

        layout.addLayout(form_layout)

        # 🖼️ Preview SVG
        layout.addWidget(QLabel("Pré-visualização do Mapa:"))
        self.svg_widget = QSvgWidget()
        self.svg_widget.setMinimumHeight(200)
        layout.addWidget(self.svg_widget)

        self.nome_input.textChanged.connect(self.atualizar_svg_preview)
        self.url_input.textChanged.connect(self.atualizar_svg_preview)
        self.atualizar_svg_preview()

        # 🔘 Botões
        botoes = QHBoxLayout()
        btn_salvar = QPushButton("Salvar")
        btn_cancelar = QPushButton("Cancelar")
        btn_salvar.clicked.connect(self.accept)
        btn_cancelar.clicked.connect(self.reject)
        botoes.addStretch()
        botoes.addWidget(btn_cancelar)
        botoes.addWidget(btn_salvar)
        layout.addLayout(botoes)

    def atualizar_svg_preview(self):
        # Tenta extrair número do nome ou URL
        texto = self.nome_input.text() or self.url_input.text()
        match = re.search(r"(\d+)", texto)
        if match:
            numero = match.group(1)
            caminho = f"mapas/mini/{numero}.svg"
            if os.path.exists(caminho):
                self.svg_widget.load(caminho)
                return
        self.svg_widget.load("")  # Limpa se não encontrar

    def get_dados(self):
        return {
            "nome": self.nome_input.text().strip(),
            "url": self.url_input.text().strip(),
            "status": self.status_input.currentText(),
            "observacoes": self.obs_input.toPlainText().strip()
        }
