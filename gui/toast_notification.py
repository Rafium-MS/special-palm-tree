from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QPoint


class ToastNotification(QWidget):
    def __init__(self, texto, tipo="info", tempo=3000, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.label = QLabel(texto)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)

        estilo = {
            "info": "background-color: #2196f3; color: white;",
            "sucesso": "background-color: #4caf50; color: white;",
            "erro": "background-color: #f44336; color: white;",
            "aviso": "background-color: #ff9800; color: white;"
        }.get(tipo, "background-color: #333; color: white;")

        self.label.setStyleSheet(f"""
            {estilo}
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 14px;
            min-width: 200px;
        """)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.adjustSize()

        # Posiciona no canto inferior da janela principal
        if parent:
            geo = parent.geometry()
            self.move(geo.left() + geo.width() - self.width() - 30, geo.top() + geo.height() - 80)

        # Animação de fade out
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.finished.connect(self.close)

        # Timer para fechar
        QTimer.singleShot(tempo, self.desaparecer)

    def desaparecer(self):
        self.animation.start()
