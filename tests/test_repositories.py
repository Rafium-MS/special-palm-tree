import importlib
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.models import Character
from infra.repositories import CharacterRepository


def test_character_repo_create_and_list(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_WORKSPACE", str(tmp_path))
    import config
    import infra.db as _db

    importlib.reload(config)
    importlib.reload(_db)

    with _db.transaction() as conn:
        repo = CharacterRepository(conn)
        char_id = repo.create(Character(name="Eve", birth_year=-20))

    with _db.transaction() as conn:
        repo = CharacterRepository(conn)
        character = repo.find(char_id)
        assert character is not None and character.name == "Eve"
        assert any(c.name == "Eve" for c in repo.list())

