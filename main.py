from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
import sys

def main():
    app = QApplication(sys.argv)
    janela = MainWindow()
    janela.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
