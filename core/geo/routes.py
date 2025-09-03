"""Utility for managing routes between settlements using networkx."""

from __future__ import annotations

from typing import Iterable, Literal

import networkx as nx

RouteType = Literal["terrestre", "fluvial", "maritimo"]


class RoutesGraph:
    """Graph of routes between settlements."""

    def __init__(self) -> None:
        self.graph = nx.Graph()

    def add_settlement(self, name: str) -> None:
        """Ensure a settlement node exists."""
        self.graph.add_node(name)

    def add_route(self, origem: str, destino: str, tipo: RouteType) -> None:
        """Add a route between two settlements."""
        if tipo not in {"terrestre", "fluvial", "maritimo"}:
            raise ValueError("tipo must be terrestre, fluvial or maritimo")
        self.add_settlement(origem)
        self.add_settlement(destino)
        self.graph.add_edge(origem, destino, tipo=tipo)

    def remove_route(self, origem: str, destino: str) -> None:
        if self.graph.has_edge(origem, destino):
            self.graph.remove_edge(origem, destino)

    def neighbors(self, settlement: str) -> Iterable[str]:
        return self.graph.neighbors(settlement)

    def routes(self) -> Iterable[tuple[str, str, RouteType]]:
        """Iterate over stored routes."""
        for u, v, data in self.graph.edges(data=True):
            yield u, v, data.get("tipo", "terrestre")
