import importlib
import json
import sys
import types
from pathlib import Path


def test_theme_persistence(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    sys.path.append(str(Path(__file__).resolve().parents[1]))

    # Stub PyQt5 dependencies before importing theme
    qt_module = types.ModuleType("PyQt5")
    widgets_module = types.ModuleType("PyQt5.QtWidgets")

    class DummyApp:
        @staticmethod
        def instance():
            return None

    widgets_module.QApplication = DummyApp
    qt_module.QtWidgets = widgets_module
    sys.modules.setdefault("PyQt5", qt_module)
    sys.modules.setdefault("PyQt5.QtWidgets", widgets_module)

    # Reload modules so CONFIG_FILE points inside tmp_path
    from shared import constants as const

    importlib.reload(const)
    import ui.theme as theme

    importlib.reload(theme)

    theme.apply_theme("dark", project_id="proj", user_id="user")
    assert const.CONFIG_FILE.exists()
    data = json.loads(const.CONFIG_FILE.read_text(encoding="utf-8"))
    assert data["themes"]["proj"]["user"] == "dark"
    assert theme.load_theme("proj", "user") == "dark"
