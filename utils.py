import json
import re
from collections import Counter
from pathlib import Path

from constants import CONFIG_FILE, DEFAULT_WORKSPACE, SUPPORTED_TEXT_EXTS


def compute_stats(text: str, wpm: int = 200, top_n: int = 5):
    """Compute word/character counts, reading time and top words."""
    words_list = re.findall(r"\b\w+\b", text.lower())
    word_count = len(words_list)
    char_count = len(text)
    reading_time = word_count / float(wpm) if wpm else 0
    freq = Counter(words_list)
    top_words = freq.most_common(top_n)
    return {
        "words": word_count,
        "characters": char_count,
        "reading_time": reading_time,
        "top_words": top_words,
    }


def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)


def load_config():
    if CONFIG_FILE.exists():
        try:
            cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception:
            cfg = {}
    else:
        cfg = {}

    cfg.setdefault("daily_word_goal", 0)
    cfg.setdefault("theme", "light")
    cfg.setdefault("line_spacing", 1.0)
    return cfg


def save_config(cfg: dict):
    try:
        CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def read_file_text(file_path: Path) -> str:
    """Read *file_path* converting known formats to plain text."""
    ext = file_path.suffix.lower()
    if ext == ".docx":
        try:
            from docx import Document
        except Exception as e:
            raise RuntimeError("Biblioteca python-docx não instalada") from e
        doc = Document(str(file_path))
        return "\n".join(p.text for p in doc.paragraphs)
    if ext == ".odt":
        try:
            from odf.opendocument import load
            from odf import text, teletype
        except Exception as e:
            raise RuntimeError("Biblioteca odfpy não instalada") from e
        doc = load(str(file_path))
        paragraphs = doc.getElementsByType(text.P)
        return "\n".join(teletype.extractText(p) for p in paragraphs)
    if ext == ".rtf":
        try:
            from striprtf.striprtf import rtf_to_text
        except Exception as e:
            raise RuntimeError("Biblioteca striprtf não instalada") from e
        raw = file_path.read_text(encoding="utf-8", errors="ignore")
        return rtf_to_text(raw)
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return file_path.read_text(encoding="latin-1")


def search_workspace(pattern: str):
    """Search all supported text files under DEFAULT_WORKSPACE for *pattern*.

    Returns a list of tuples ``(Path, line_number, line_text)``.
    ``pattern`` is matched case-insensitively as a plain substring.
    """
    results = []
    pattern_lower = pattern.lower()
    for file_path in DEFAULT_WORKSPACE.rglob("*"):
        if not file_path.is_file() or file_path.suffix.lower() not in SUPPORTED_TEXT_EXTS:
            continue
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                text = file_path.read_text(encoding="latin-1")
            except Exception:
                continue
        except Exception:
            continue
        for num, line in enumerate(text.splitlines(), 1):
            if pattern_lower in line.lower():
                results.append((file_path, num, line.strip()))
    return results
