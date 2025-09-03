from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional
import uuid


@dataclass
class Evento:
    """Representa um evento na linha do tempo."""

    titulo: str
    instante: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    tipo: str = "Geral"
    importancia: int = 3
    escopo: str = "local"
    descricao: str = ""
    era: str = ""
    tags: List[str] = field(default_factory=list)
    depende_de: List[str] = field(default_factory=list)
    personagens: List[str] = field(default_factory=list)
    lugares: List[str] = field(default_factory=list)


class TimelineService:
    """Serviço para manipulação de eventos de linha do tempo."""

    def __init__(self, eventos: Iterable[Evento] | None = None) -> None:
        self.eventos: List[Evento] = list(eventos or [])

    def add_event(self, evento: Evento) -> None:
        """Adiciona um evento e mantém a ordenação."""
        self.eventos.append(evento)
        self.sort_events()

    def sort_events(self) -> List[Evento]:
        """Ordena eventos por instante e título."""
        self.eventos.sort(key=lambda e: (e.instante, e.titulo))
        return self.eventos

    def resolve_conflicts(self) -> List[str]:
        """Retorna lista de IDs com datas conflitantes."""
        seen: dict[str, int] = {}
        conflicts: set[str] = set()
        for ev in self.eventos:
            prev = seen.get(ev.id)
            if prev is not None and prev != ev.instante:
                conflicts.add(ev.id)
            seen[ev.id] = ev.instante
        return sorted(conflicts)

    def filter_by(
        self,
        *,
        tipo: Optional[str] = None,
        escopo: Optional[str] = None,
        era: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[Evento]:
        """Filtra eventos por campos opcionais."""
        result = self.eventos
        if tipo is not None:
            result = [e for e in result if e.tipo == tipo]
        if escopo is not None:
            result = [e for e in result if e.escopo == escopo]
        if era is not None:
            result = [e for e in result if e.era == era]
        if tag is not None:
            result = [e for e in result if tag in e.tags]
        return result

    def quick_create(self, date: int, snippet: str) -> Evento:
        """Cria rapidamente um evento usando apenas data e trecho."""
        evento = Evento(titulo=snippet.strip(), instante=date)
        self.add_event(evento)
        return evento


# Instância global utilizada pelo editor e UI.
timeline_service = TimelineService()
