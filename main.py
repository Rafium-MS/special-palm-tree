import sys

from PyQt5.QtWidgets import QApplication, QMessageBox

from config import settings
from shared.logging import get_logger
from shared.utils import ensure_dir
from ui.editor import EditorWindow
from ui.theme import apply_theme

logger = get_logger(__name__)


def main():
    try:
        ensure_dir(settings.workspace)
        app = QApplication(sys.argv)
        apply_theme(settings.theme)
        w = EditorWindow()
        w.show()
        sys.exit(app.exec_())
    except Exception as exc:
        logger.exception("Unhandled error")
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Erro")
        msg.setText("Ocorreu um erro inesperado.")
        msg.setInformativeText(str(exc))
        msg.exec_()


if __name__ == "__main__":
    main()
