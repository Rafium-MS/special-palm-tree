from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFileDialog
from PyQt5.QtSvg import QSvgWidget
import os

class MapaCompletoView(QWidget):
    def __init__(self, caminho_mapa="mapas/Mapa_Completo.svg"):
        super().__init__()
        self.setWindowTitle("Mapa Completo de Territórios")
        self.setMinimumSize(1000, 800)

        layout = QVBoxLayout(self)
        self.svg_widget = QSvgWidget()
        self.svg_widget.setMinimumSize(960, 720)

        # 🗺️ Carrega o arquivo
        if os.path.exists(caminho_mapa):
            self.svg_widget.load(caminho_mapa)
        else:
            aviso = QLabel(f"Arquivo '{caminho_mapa}' não encontrado.")
            aviso.setStyleSheet("color: red; font-weight: bold;")
            layout.addWidget(aviso)

        layout.addWidget(self.svg_widget)

        # Rodapé com botão opcional para abrir outro SVG
        botoes = QHBoxLayout()
        self.btn_abrir = QPushButton("Abrir outro arquivo")
        self.btn_abrir.clicked.connect(self.abrir_svg)

        botoes.addStretch()
        botoes.addWidget(self.btn_abrir)
        layout.addLayout(botoes)

    def abrir_svg(self):
        caminho, _ = QFileDialog.getOpenFileName(self, "Selecionar Mapa SVG", "", "Arquivos SVG (*.svg)")
        if caminho:
            self.svg_widget.load(caminho)
