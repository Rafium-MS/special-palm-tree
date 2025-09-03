from __future__ import annotations

from pathlib import Path
from typing import Iterable
import zipfile

try:
    from docx import Document
except Exception:  # pragma: no cover - handled at runtime
    Document = None


def export_text(text: str, path: Path, metadata: dict | None = None) -> None:
    """Export *text* to *path* inferring format from extension.

    Supports Markdown with optional YAML frontmatter, plain text,
    HTML standalone and DOCX (requires ``python-docx``).
    """
    ext = path.suffix.lower()
    if ext == ".md":
        front = ""
        if metadata:
            fm = "\n".join(f"{k}: {v}" for k, v in metadata.items())
            front = f"---\n{fm}\n---\n\n"
        path.write_text(front + text, encoding="utf-8")
    elif ext in {".html", ".htm"}:
        body = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        body = body.replace("\n", "<br/>\n")
        html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>"
            + body
            + "</body></html>"
        )
        path.write_text(html, encoding="utf-8")
    elif ext == ".docx":
        if Document is None:
            raise RuntimeError("Biblioteca python-docx não instalada")
        doc = Document()
        style = doc.styles["Normal"]
        style.font.name = "Times New Roman"
        for line in text.splitlines():
            doc.add_paragraph(line)
        doc.save(str(path))
    else:
        path.write_text(text, encoding="utf-8")


def export_project_zip(workspace: Path, dest_zip: Path) -> None:
    """Create a ZIP archive with the contents of *workspace*."""
    with zipfile.ZipFile(dest_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for file in workspace.rglob("*"):
            zf.write(file, file.relative_to(workspace))


def import_batch(src: Path, dest_workspace: Path) -> None:
    """Import .md/.txt files from *src* into *dest_workspace*.

    Directory hierarchy is mapped to book/chapter/scene structure.
    """
    for book_dir in src.iterdir():
        if not book_dir.is_dir():
            continue
        dest_book = dest_workspace / book_dir.name
        dest_book.mkdir(parents=True, exist_ok=True)
        for chap_dir in book_dir.iterdir():
            if not chap_dir.is_dir():
                continue
            dest_chap = dest_book / chap_dir.name
            dest_chap.mkdir(parents=True, exist_ok=True)
            for file in chap_dir.iterdir():
                if file.suffix.lower() not in {".md", ".txt"}:
                    continue
                target = dest_chap / file.name
                target.write_text(file.read_text(encoding="utf-8"), encoding="utf-8")


def export_modules(workspace: Path, modules: Iterable[str], dest_zip: Path) -> None:
    """Export selected *modules* from *workspace* into *dest_zip*.

    *modules* should be directory names relative to *workspace*.
    """
    with zipfile.ZipFile(dest_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for mod in modules:
            mod_path = workspace / mod
            if not mod_path.exists():
                continue
            for file in mod_path.rglob("*"):
                zf.write(file, file.relative_to(workspace))
