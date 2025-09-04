# icons.py
from pathlib import Path
from functools import lru_cache
from PyQt5.QtGui import QIcon, QPixmap, QColor, QPainter
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtSvg import QSvgRenderer

BASE = Path(__file__).resolve().parent.parent / "assets" / "icons" / "phosphor" / "SVGs"
DEFAULT_WEIGHT = "regular"

ALIASES = {
    "save": "floppy-disk",
    "open": "folder-open",
    "search": "magnifying-glass",
    "undo": "arrow-counter-clockwise",
    "redo": "arrow-clockwise",
    "bold": "text-b",
    "italic": "text-italic",
    "underline": "text-underline",
    "h1": "text-h-one",
    "h2": "text-h-two",
    "list-bullets": "list-bullets",
    "list-numbers": "list-numbers",
    "link": "link-simple",
    "unlink": "link-break",
    "delete": "trash",
    "edit": "pencil-simple",
    "add": "plus",
    "eye": "eye",
    "eye-off": "eye-slash",
    "settings": "gear-six",
    "sun": "sun",
    "moon": "moon",
}

def _resolve_name(name: str) -> str:
    return ALIASES.get(name, name).lower()

def _find_svg(name: str, weight: str) -> Path:
    path = BASE / weight / f"{name}.svg"
    if path.exists():
        return path
    # fallback de peso
    for w in ("regular", "bold", "fill", "light", "thin", "duotone"):
        p = BASE / w / f"{name}.svg"
        if p.exists():
            return p
    return path  # pode não existir; QIcon ficará “vazio”

@lru_cache(maxsize=512)
def icon(name: str, *, weight: str = DEFAULT_WEIGHT, size: int = 20, color: str | None = None) -> QIcon:
    """
    Retorna QIcon a partir dos SVGs do Phosphor.
    - weight: thin|light|regular|bold|fill|duotone
    - size: px (quando usar “tint”)
    - color: qualquer CSS color (#RRGGBB, rgb(), etc). None = sem tint (usa o SVG original).
    """
    name = _resolve_name(name)
    svg_path = _find_svg(name, weight)
    if color is None:
        return QIcon(str(svg_path))

    # Renderiza SVG e aplica “tint” via composição (SourceIn)
    renderer = QSvgRenderer(str(svg_path))
    pm = QPixmap(QSize(size, size))
    pm.fill(Qt.transparent)
    painter = QPainter(pm)
    renderer.render(painter)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pm.rect(), QColor(color))
    painter.end()
    return QIcon(pm)
