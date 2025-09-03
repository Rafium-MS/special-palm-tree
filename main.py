import getpass
import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen

from config import settings
from shared.fs_utils import ensure_dir
from shared.i18n import t
from shared.logging import get_logger
from shared.utils import load_config
from ui.editor import EditorWindow
from ui.theme import apply_theme, load_theme

logger = get_logger(__name__)


def handle_exception(exc_type, exc, tb):
    """Global exception handler that displays a dialog."""
    logger.exception("Unhandled error", exc_info=(exc_type, exc, tb))
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle(t("error.title"))
    msg.setText(t("error.unexpected"))
    msg.setInformativeText(str(exc))
    msg.exec_()


def detect_recent_workspace() -> Path:
    """Return the most recently used workspace."""
    cfg = load_config()
    workspace = Path(cfg.get("workspace", str(settings.workspace)))
    ensure_dir(workspace)
    settings.workspace = workspace
    return workspace


def maybe_show_splash(workspace: Path, app: QApplication) -> QSplashScreen | None:
    """Show a lightweight splash screen when loading large projects."""
    try:
        file_count = sum(1 for _ in workspace.rglob("*") if _.is_file())
    except Exception:
        file_count = 0
    if file_count > 200:  # heuristic for large projects
        splash = QSplashScreen(QPixmap(400, 300))
        splash.showMessage(
            "Carregando projeto...", Qt.AlignBottom | Qt.AlignCenter, Qt.white
        )
        splash.show()
        app.processEvents()
        return splash
    return None


def get_main_window(module: str):
    module = module.lower()
    if module == "timeline":
        from ui.linha_do_tempo import MainWindow as TimelineWindow

        return TimelineWindow()
    if module in {"universo", "universe"}:
        from ui.cidades_planetas import MainWindow as UniverseWindow

        return UniverseWindow()
    return EditorWindow()


def main():
    ensure_dir(settings.workspace)
    app = QApplication(sys.argv)
    sys.excepthook = handle_exception

    module = sys.argv[1].lower() if len(sys.argv) > 1 else "editor"
    workspace = detect_recent_workspace()
    user_id = getpass.getuser()
    theme = load_theme(workspace.name, user_id)
    apply_theme(theme, workspace.name, user_id)
    splash = maybe_show_splash(workspace, app) if module == "editor" else None

    w = get_main_window(module)
    w.show()
    if splash:
        splash.finish(w)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
