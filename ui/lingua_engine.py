# lingua_engine.py
from __future__ import annotations
import re
from typing import Iterable, List, Dict
# Import models using a relative import so this module works regardless of how
# the package is executed.  Using an absolute import expects `lingua_models`
# to be on `sys.path` and raises `ModuleNotFoundError` when running the package
# directly.
from .lingua_models import Rule

def apply_rules(text: str, rules: Iterable[Rule]) -> str:
    out = text
    for r in rules:    # já em ordem de prioridade
        try:
            out = re.sub(r.pattern, r.replacement, out)
        except re.error:
            continue
    return out

def tokenize(text: str) -> List[str]:
    return re.findall(r"\\w+|[^\\w\\s]", text, flags=re.UNICODE)

def detokenize(tokens: List[str]) -> str:
    s = " ".join(tokens)
    s = re.sub(r"\\s+([,.!?;:])", r"\\1", s)
    s = re.sub(r"\\(\\s+", "(", s)
    s = re.sub(r"\\s+\\)", ")", s)
    return s

def translate(tokens: List[str], lexicon_map: Dict[str, str]) -> List[str]:
    out = []
    for t in tokens:
        low = t.lower()
        if low.isalpha() and low in lexicon_map:
            val = lexicon_map[low]
            if t.istitle():   val = val[:1].upper() + val[1:]
            elif t.isupper(): val = val.upper()
            out.append(val)
        else:
            out.append(t)
    return out
