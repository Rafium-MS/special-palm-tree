import json
from typing import Any, Dict

from .constants import CONFIG_FILE


def load_config() -> Dict[str, Any]:
    """Load configuration from CONFIG_FILE ensuring default structure."""
    if CONFIG_FILE.exists():
        try:
            cfg: Dict[str, Any] = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            cfg = {}
    else:
        cfg = {}

    ui = cfg.setdefault("ui", {})
    ui.setdefault("theme", "light")
    cfg.setdefault("last_project", "")
    cfg.setdefault("projects", {})
    return cfg


def get_project_config(cfg: Dict[str, Any], project_id: str) -> Dict[str, Any]:
    """Return configuration dictionary for *project_id* ensuring defaults."""
    projects = cfg.setdefault("projects", {})
    project = projects.setdefault(project_id, {})
    project.setdefault("favorites", [])
    project.setdefault("tags", {})
    project.setdefault("shortcuts", {})
    project.setdefault("line_spacing", 1.0)
    project.setdefault("daily_word_goal", 0)
    project.setdefault("open_panels", [])
    project.setdefault("editor_width", 0)
    project.setdefault("last_session", {})
    project.setdefault("autosave_interval", 0)
    project.setdefault("autosave_dir", "")
    project.setdefault("font_family", "")
    project.setdefault("font_size", 0)
    return project


def save_config(cfg: Dict[str, Any]) -> None:
    """Persist *cfg* to CONFIG_FILE."""
    try:
        CONFIG_FILE.write_text(
            json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except Exception:
        pass
