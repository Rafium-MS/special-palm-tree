import json

from .constants import CONFIG_FILE


def load_config():
    if CONFIG_FILE.exists():
        try:
            cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            cfg = {}
    else:
        cfg = {}

    cfg.setdefault("daily_word_goal", 0)
    cfg.setdefault("theme", "light")
    cfg.setdefault("line_spacing", 1.0)
    return cfg


def save_config(cfg: dict):
    try:
        CONFIG_FILE.write_text(
            json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    except Exception:
        pass
