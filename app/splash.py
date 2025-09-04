"""Splash screen utilities."""

from __future__ import annotations

from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QSplashScreen


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


__all__ = ["maybe_show_splash"]

