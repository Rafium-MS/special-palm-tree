"""Factory for choosing the main application window."""

from __future__ import annotations

from ui.editor import EditorWindow


def get_main_window(module: str):
    module = module.lower()
    if module == "timeline":
        from ui.linha_do_tempo import MainWindow as TimelineWindow

        return TimelineWindow()
    if module in {"universo", "universe"}:
        from ui.cidades_planetas import MainWindow as UniverseWindow

        return UniverseWindow()
    return EditorWindow()


__all__ = ["get_main_window"]

