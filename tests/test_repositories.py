import importlib
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.models import Character
from infra.repositories import CharacterRepo


def test_character_repo_add_and_list(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_WORKSPACE", str(tmp_path))
    import config
    import infra.db as db

    importlib.reload(config)
    importlib.reload(db)

    conn = db.connect()
    repo = CharacterRepo(conn)
    repo.add(Character(name="Eve", birth_year=-20))

    characters = repo.list()
    assert any(c.name == "Eve" for c in characters)

