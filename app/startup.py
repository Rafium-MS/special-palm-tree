"""Application startup helpers."""

from __future__ import annotations

from pathlib import Path

from PyQt5.QtWidgets import QMessageBox

from config import settings
from shared.i18n import t
from shared.logging import get_logger
from shared.utils.fs import ensure_dir
from shared.config import config_manager

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
    cfg = config_manager.load()
    workspace = Path(cfg.last_project or str(settings.workspace))
    ensure_dir(workspace)
    settings.workspace = workspace
    return workspace


__all__ = ["handle_exception", "detect_recent_workspace"]

