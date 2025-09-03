APP_NAME = "Editor de Textos"
from pathlib import Path

DEFAULT_WORKSPACE = Path.cwd() / "workspace"
CONFIG_FILE = Path.cwd() / ".editor_config.json"
AUTOSAVE_DIRNAME = ".autosave"
HISTORY_DIRNAME = ".history"
MAX_SNAPSHOTS = 5
SUPPORTED_TEXT_EXTS = {".txt", ".md", ".markdown", ".json", ".yaml", ".yml", ".ini", ".cfg", ".csv"}
