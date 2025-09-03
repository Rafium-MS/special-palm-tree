import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.timeline.service import Evento, TimelineService


def test_sort_events_orders_by_year_and_title():
    s = TimelineService([
        Evento(titulo="B", instante=5),
        Evento(titulo="A", instante=5),
        Evento(titulo="C", instante=1),
    ])
    s.sort_events()
    assert [e.titulo for e in s.eventos] == ["C", "A", "B"]


def test_resolve_conflicts_detects_same_id_different_year():
    ev1 = Evento(titulo="E1", instante=10, id="dup")
    ev2 = Evento(titulo="E2", instante=12, id="dup")
    s = TimelineService([ev1, ev2])
    assert s.resolve_conflicts() == ["dup"]
