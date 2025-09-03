import json
from pathlib import Path

from PyQt5.QtWidgets import QApplication

from config import settings

_TOKENS_PATH = Path(__file__).with_name("tokens.json")
with _TOKENS_PATH.open("r", encoding="utf-8") as fh:
    TOKENS = json.load(fh)


def _build_stylesheet(palette: dict) -> str:
    typography = TOKENS.get("typography", {})
    spacing = TOKENS.get("spacing", {})
    padding = spacing.get("padding", "4px 8px")
    button_height = spacing.get("button_height", "24px")
    font_size = typography.get("base_size", "14px")
    font_family = typography.get("font_family", "sans-serif")

    return f"""
    QWidget {{ font-size: {font_size}; font-family: {font_family}; }}
    QMainWindow {{ background: {palette['bg']}; color: {palette['text']}; }}
    QToolBar {{ background: {palette['panel']}; border: 0; }}
    QTreeView {{ background: {palette['panel']}; color: {palette['text']}; border-right: 1px solid {palette['border']}; }}
    QPlainTextEdit {{ background: {palette['panel']}; color: {palette['text']}; selection-background-color: {palette['accent']}; }}
    QStatusBar {{ background: {palette['panel']}; color: {palette['text']}; border-top: 1px solid {palette['border']}; }}
    QLineEdit, QPushButton {{ background: {palette['panel']}; color: {palette['text']}; border: 1px solid {palette['border']}; padding: {padding}; min-height: {button_height}; }}
    QPushButton:hover {{ border-color: {palette['accent']}; }}
    QMenu {{ background: {palette['panel']}; color: {palette['text']}; border: 1px solid {palette['border']}; }}
    *:focus {{ outline: 2px solid {palette['accent']}; }}
    """


def as_css_variables(theme: str) -> str:
    """Return CSS variable declarations for *theme*."""

    palette = TOKENS["themes"].get(theme, TOKENS["themes"]["light"])
    lines = [f"--{key}: {value};" for key, value in palette.items()]
    return ":root{\n    " + "\n    ".join(lines) + "\n}"


def apply_theme(theme: str) -> None:
    """Apply *theme* to the current QApplication and persist selection."""

    palette = TOKENS["themes"].get(theme, TOKENS["themes"]["light"])
    settings.save_theme(theme)
    app = QApplication.instance()
    if app:
        app.setStyleSheet(_build_stylesheet(palette))
