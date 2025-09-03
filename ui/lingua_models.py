# lingua_models.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal, Dict, Any, Optional
import json

Scope = Literal["phonology", "orthography", "morphology", "syntax"]

@dataclass
class Language:
    id: Optional[int]
    name: str
    code: str
    description: str = ""
    script: str = "latin"
    phonology: Dict[str, Any] = field(default_factory=dict)
    orthography: Dict[str, Any] = field(default_factory=dict)
    morphology: Dict[str, Any] = field(default_factory=dict)
    syntax: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Lexeme:
    id: Optional[int]
    language_id: int
    lemma: str
    pos: str           # 'N', 'V', 'ADJ', ...
    gloss: str = ""
    ipa: str = ""
    tags: str = ""

@dataclass
class WordForm:
    id: Optional[int]
    lexeme_id: int
    form: str
    features: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Rule:
    id: Optional[int]
    language_id: int
    name: str
    scope: Scope
    pattern: str
    replacement: str
    environment: str = ""
    priority: int = 100
    enabled: bool = True

@dataclass
class LexiconMap:
    id: Optional[int]
    language_id: int
    source: str
    target: str
    notes: str = ""

def to_json(d: dict) -> str: return json.dumps(d, ensure_ascii=False)
def from_json(s: str) -> dict:
    try: return json.loads(s) if s else {}
    except Exception: return {}
