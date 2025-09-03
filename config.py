from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Application configuration loaded from environment variables.

    Theme preference can be overridden by a user settings file
    located in the application workspace.
    """

    workspace: Path = Path(os.getenv("APP_WORKSPACE", "data"))
    language: str = os.getenv("APP_LANGUAGE", "pt-br")
    theme: str = os.getenv("APP_THEME", "light")
    debug: bool = os.getenv("APP_DEBUG", "0") == "1"

    def load_user_settings(self) -> None:
        """Load user settings from ``settings.json`` if available."""

        path = self.workspace / "settings.json"
        if path.exists():
            with path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            self.theme = data.get("theme", self.theme)
            self.language = data.get("language", self.language)

    def save_theme(self, theme: str) -> None:
        """Persist the selected *theme* to the workspace settings file."""

        self.workspace.mkdir(parents=True, exist_ok=True)
        path = self.workspace / "settings.json"
        if path.exists():
            with path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
        else:
            data = {}
        data["theme"] = theme
        with path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh)


settings = Config()
settings.load_user_settings()
