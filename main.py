"""Entry point for the world builder application."""

import getpass
import sys

from PyQt5.QtWidgets import QApplication

from app.splash import maybe_show_splash
from app.startup import detect_recent_workspace, handle_exception
from app.window_factory import get_main_window
from config import settings
from shared.utils.fs import ensure_dir
from ui.theme import apply_theme, load_theme


def main() -> None:
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

