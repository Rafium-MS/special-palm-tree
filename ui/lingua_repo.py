# lingua_repo.py
from __future__ import annotations
import sqlite3
from typing import List
# Import models using a relative import so that this module can be
# loaded regardless of how the package is executed.  Previously the
# code relied on the top-level `lingua_models` name being available on
# `sys.path`, which isn't the case when running the project as a
# package (e.g. `python -m ui.editor`).  Using a relative import ensures
# the models are resolved from within the `ui` package itself and fixes
# `ModuleNotFoundError: No module named 'lingua_models'` raised when
# launching the application.
from .lingua_models import (
    Language,
    Lexeme,
    WordForm,
    Rule,
    LexiconMap,
    to_json,
    from_json,
)

SCHEMA_SQL = """(cole o SQL acima)"""

def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    conn.commit()

# Languages
def add_language(conn, lang: Language) -> int:
    cur = conn.execute(
        """INSERT INTO languages
           (name, code, description, script, phonology_json, orthography_json, morphology_json, syntax_json)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (lang.name, lang.code, lang.description, lang.script,
         to_json(lang.phonology), to_json(lang.orthography), to_json(lang.morphology), to_json(lang.syntax))
    )
    conn.commit()
    return cur.lastrowid

def list_languages(conn) -> List[Language]:
    cur = conn.execute("SELECT * FROM languages ORDER BY name ASC")
    out = []
    for r in cur.fetchall():
        out.append(Language(
            id=r[0], name=r[1], code=r[2], description=r[3], script=r[4],
            phonology=from_json(r[5]), orthography=from_json(r[6]),
            morphology=from_json(r[7]), syntax=from_json(r[8])
        ))
    return out

# Lexicon
def add_lexeme(conn, lx: Lexeme) -> int:
    cur = conn.execute(
        "INSERT INTO lexemes(language_id, lemma, pos, gloss, ipa, tags) VALUES (?, ?, ?, ?, ?, ?)",
        (lx.language_id, lx.lemma, lx.pos, lx.gloss, lx.ipa, lx.tags)
    )
    conn.commit()
    return cur.lastrowid

def list_lexemes(conn, language_id: int) -> List[Lexeme]:
    cur = conn.execute(
        "SELECT id, language_id, lemma, pos, gloss, ipa, tags FROM lexemes WHERE language_id=? ORDER BY lemma",
        (language_id,)
    )
    return [Lexeme(*row) for row in cur.fetchall()]

def add_word_form(conn, wf: WordForm) -> int:
    cur = conn.execute(
        "INSERT INTO word_forms(lexeme_id, form, features_json) VALUES (?, ?, ?)",
        (wf.lexeme_id, wf.form, to_json(wf.features))
    )
    conn.commit()
    return cur.lastrowid

# Rules
def add_rule(conn, rl: Rule) -> int:
    cur = conn.execute(
        """INSERT INTO rules(language_id, name, scope, pattern, replacement, environment, priority, enabled)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (rl.language_id, rl.name, rl.scope, rl.pattern, rl.replacement, rl.environment, rl.priority, int(rl.enabled))
    )
    conn.commit()
    return cur.lastrowid

def list_rules(conn, language_id: int, scope: str | None = None, only_enabled: bool = True) -> List[Rule]:
    q = "SELECT id, language_id, name, scope, pattern, replacement, environment, priority, enabled FROM rules WHERE language_id=?"
    params = [language_id]
    if scope: q += " AND scope=?"; params.append(scope)
    if only_enabled: q += " AND enabled=1"
    q += " ORDER BY priority ASC"
    rows = conn.execute(q, tuple(params)).fetchall()
    return [
        Rule(id=r[0], language_id=r[1], name=r[2], scope=r[3], pattern=r[4],
             replacement=r[5], environment=r[6], priority=r[7], enabled=bool(r[8]))
        for r in rows
    ]

# Lexicon map (translator)
def add_lexicon_map(conn, m: LexiconMap) -> int:
    cur = conn.execute(
        "INSERT INTO lexicon_map(language_id, source, target, notes) VALUES (?, ?, ?, ?)",
        (m.language_id, m.source, m.target, m.notes)
    )
    conn.commit()
    return cur.lastrowid

def list_lexicon_map(conn, language_id: int) -> dict[str, str]:
    cur = conn.execute("SELECT source, target FROM lexicon_map WHERE language_id=?", (language_id,))
    return {src.lower(): tgt for (src, tgt) in cur.fetchall()}
