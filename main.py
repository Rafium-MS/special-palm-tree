import sys
from PyQt5.QtWidgets import QApplication

from constants import DEFAULT_WORKSPACE
from utils import ensure_dir, load_config
from theme import apply_theme
from editor import EditorWindow


def main():
    ensure_dir(DEFAULT_WORKSPACE)
    app = QApplication(sys.argv)
    cfg = load_config()
    apply_theme(cfg.get("theme", "light"))
    w = EditorWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
