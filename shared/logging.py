from __future__ import annotations

import logging
from typing import Optional

from config import settings

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a module-level logger configured with the app settings."""
    return logging.getLogger(name)
