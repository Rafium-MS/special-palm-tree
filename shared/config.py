"""Configuration management using pydantic models."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel, Field

from .constants import CONFIG_FILE


class UIConfig(BaseModel):
    theme: str = "light"


class ProjectConfig(BaseModel):
    favorites: list[str] = Field(default_factory=list)
    tags: Dict[str, list[str]] = Field(default_factory=dict)
    shortcuts: Dict[str, str] = Field(default_factory=dict)
    line_spacing: float = 1.0
    daily_word_goal: int = 0
    open_panels: list[str] = Field(default_factory=list)
    editor_width: int = 0
    last_session: Dict[str, Any] = Field(default_factory=dict)
    autosave_interval: int = 0
    autosave_dir: str = ""
    font_family: str = ""
    font_size: int = 0


class AppConfig(BaseModel):
    ui: UIConfig = UIConfig()
    last_project: str = ""
    projects: Dict[str, ProjectConfig] = Field(default_factory=dict)


class ConfigManager:
    """Load and persist application configuration."""

    def __init__(self, path: Path = CONFIG_FILE):
        self.path = path
        self._config = AppConfig()

    @property
    def config(self) -> AppConfig:
        return self._config

    def load(self) -> AppConfig:
        """Load configuration from disk, creating defaults when necessary."""
        if self.path.exists():
            try:
                self._config = AppConfig.model_validate_json(
                    self.path.read_text(encoding="utf-8")
                )
            except Exception:
                self._config = AppConfig()
        else:
            self._config = AppConfig()
        return self._config

    def save(self) -> None:
        """Persist current configuration to disk."""
        try:
            self.path.write_text(
                self._config.model_dump_json(indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception:
            pass

    def get_project(self, project_id: str) -> ProjectConfig:
        """Return configuration for ``project_id`` creating defaults if missing."""
        return self._config.projects.setdefault(project_id, ProjectConfig())


config_manager = ConfigManager()

__all__ = [
    "UIConfig",
    "ProjectConfig",
    "AppConfig",
    "ConfigManager",
    "config_manager",
]

