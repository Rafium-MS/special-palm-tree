import json
from pathlib import Path
from typing import Dict

from PyQt5.QtWidgets import QApplication

from config import settings
from shared.constants import CONFIG_FILE
from shared.theme_tokens import tokens as token_variables

_TOKENS_PATH = Path(__file__).with_name("tokens.json")
with _TOKENS_PATH.open("r", encoding="utf-8") as fh:
    TOKENS = json.load(fh)

# 🔹 Exportar os temas disponíveis
THEMES = TOKENS.get("themes", {})


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
    """Return CSS variable declarations for *theme* including shared tokens."""

    palette = TOKENS["themes"].get(theme, TOKENS["themes"]["light"])
    lines = [f"--{key}: {value};" for key, value in palette.items()]
    for name, value in token_variables().items():
        lines.append(f"{name}: {value};")
    return ":root{\n    " + "\n    ".join(lines) + "\n}"


def _save_theme_selection(project_id: str, user_id: str, theme: str) -> None:
    """Persist *theme* for a given *project_id* and *user_id*."""

    if CONFIG_FILE.exists():
        with CONFIG_FILE.open("r", encoding="utf-8") as fh:
            data: Dict[str, Dict] = json.load(fh)
    else:
        data = {}
    themes = data.setdefault("themes", {})
    project = themes.setdefault(project_id, {})
    project[user_id] = theme
    with CONFIG_FILE.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def load_theme(project_id: str, user_id: str, default: str = settings.theme) -> str:
    """Return stored theme for *project_id* and *user_id*.

    Falls back to *default* if nothing was persisted.
    """

    if CONFIG_FILE.exists():
        with CONFIG_FILE.open("r", encoding="utf-8") as fh:
            data: Dict[str, Dict] = json.load(fh)
        return data.get("themes", {}).get(project_id, {}).get(user_id, default)
    return default


def apply_theme(
    theme: str, project_id: str = "default_project", user_id: str = "default_user"
) -> None:
    """Apply *theme* to the current QApplication and persist selection."""

    palette = TOKENS["themes"].get(theme, TOKENS["themes"]["light"])
    _save_theme_selection(project_id, user_id, theme)
    app = QApplication.instance()
    if app:
        app.setStyleSheet(_build_stylesheet(palette))
