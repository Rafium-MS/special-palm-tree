from pathlib import Path

from config import settings

APP_NAME = "Editor de Textos"
DEFAULT_WORKSPACE = settings.workspace
CONFIG_FILE = Path.cwd() / ".editor_config.json"
AUTOSAVE_DIRNAME = ".autosave"
HISTORY_DIRNAME = ".history"
MAX_SNAPSHOTS = 5
SUPPORTED_TEXT_EXTS = {
    ".txt",
    ".md",
    ".markdown",
    ".json",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".csv",
}
