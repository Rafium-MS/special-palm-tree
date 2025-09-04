"""Utility for managing routes between settlements.

Historically this module relied on :mod:`networkx` for its underlying data
structure.  To keep dependencies small we now ship a tiny bespoke graph
implementation that supports the limited feature set required.
"""

from __future__ import annotations

from typing import Dict, Iterable, Literal

RouteType = Literal["terrestre", "fluvial", "maritimo"]


class RoutesGraph:
    """Graph of routes between settlements."""

    def __init__(self) -> None:
        self._adj: Dict[str, Dict[str, Dict[str, object]]] = {}

    def add_settlement(self, name: str) -> None:
        """Ensure a settlement node exists."""
        self._adj.setdefault(name, {})

    def add_route(self, origem: str, destino: str, tipo: RouteType) -> None:
        """Add a route between two settlements."""
        if tipo not in {"terrestre", "fluvial", "maritimo"}:
            raise ValueError("tipo must be terrestre, fluvial or maritimo")
        self.add_settlement(origem)
        self.add_settlement(destino)
        data = {"tipo": tipo}
        self._adj[origem][destino] = data
        self._adj[destino][origem] = data

    def remove_route(self, origem: str, destino: str) -> None:
        self._adj.get(origem, {}).pop(destino, None)
        self._adj.get(destino, {}).pop(origem, None)

    def neighbors(self, settlement: str) -> Iterable[str]:
        return self._adj.get(settlement, {}).keys()

    def routes(self) -> Iterable[tuple[str, str, RouteType]]:
        """Iterate over stored routes."""
        seen = set()
        for u, nbrs in self._adj.items():
            for v, data in nbrs.items():
                if (v, u) in seen:
                    continue
                seen.add((u, v))
                yield u, v, data.get("tipo", "terrestre")
