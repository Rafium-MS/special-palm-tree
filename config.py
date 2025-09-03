from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    workspace: Path = Path(os.getenv("APP_WORKSPACE", "data"))
    language: str = os.getenv("APP_LANGUAGE", "pt-br")
    theme: str = os.getenv("APP_THEME", "light")
    debug: bool = os.getenv("APP_DEBUG", "0") == "1"


settings = Config()
