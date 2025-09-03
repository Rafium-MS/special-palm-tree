from PyQt5.QtWidgets import QApplication

THEMES = {
    "light": {
        "--bg": "#ffffff",
        "--panel": "#f0f0f0",
        "--text": "#000000",
        "--accent": "#0078d4",
        "--border": "#d0d0d0",
    },
    "dark": {
        "--bg": "#131417",
        "--panel": "#1a1c22",
        "--text": "#e6e6e6",
        "--accent": "#86b7ff",
        "--border": "#2a2d36",
    },
    "sepia": {
        "--bg": "#f5efe6",
        "--panel": "#fffaf2",
        "--text": "#2b2a27",
        "--accent": "#3b6fb6",
        "--border": "#e2d7c7",
    },
}


def _build_stylesheet(palette: dict) -> str:
    return f"""
    QMainWindow {{ background: {palette['--bg']}; color: {palette['--text']}; }}
    QToolBar {{ background: {palette['--panel']}; border: 0; }}
    QTreeView {{ background: {palette['--panel']}; color: {palette['--text']}; border-right: 1px solid {palette['--border']}; }}
    QPlainTextEdit {{ background: {palette['--panel']}; color: {palette['--text']}; selection-background-color: {palette['--accent']}; }}
    QStatusBar {{ background: {palette['--panel']}; color: {palette['--text']}; border-top: 1px solid {palette['--border']}; }}
    QLineEdit, QPushButton {{ background: {palette['--panel']}; color: {palette['--text']}; border: 1px solid {palette['--border']}; padding: 4px 8px; }}
    QPushButton:hover {{ border-color: {palette['--accent']}; }}
    QMenu {{ background: {palette['--panel']}; color: {palette['--text']}; border: 1px solid {palette['--border']}; }}
    """


def apply_theme(theme: str) -> None:
    """Apply *theme* to the current QApplication."""
    palette = THEMES.get(theme, THEMES["light"])
    app = QApplication.instance()
    if app:
        app.setStyleSheet(_build_stylesheet(palette))
