from __future__ import annotations

from typing import Dict

from config import settings

CATALOG: Dict[str, Dict[str, str]] = {
    "pt-br": {
        "error.title": "Erro",
        "error.unexpected": "Ocorreu um erro inesperado.",
    },
    "en": {
        "error.title": "Error",
        "error.unexpected": "An unexpected error occurred.",
    },
}


def t(key: str) -> str:
    """Return translated string for *key* using the configured language."""
    lang = settings.language.lower()
    catalog = CATALOG.get(lang, CATALOG["en"])
    return catalog.get(key, key)
