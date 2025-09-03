import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.io import export_text


def test_export_text_html_snapshot(tmp_path):
    path = tmp_path / "out.html"
    export_text("Hello & <World>\nLine2", path)
    content = path.read_text(encoding="utf-8")
    expected = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>"
        "Hello &amp; &lt;World&gt;<br/>\nLine2</body></html>"
    )
    assert content == expected

