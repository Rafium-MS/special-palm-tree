"""Utility classes for managing bidirectional relations between entities.

The :class:`RelationGraph` provides a lightweight interface around
``networkx`` to register entities (characters, factions, locations, etc.)
with bidirectional edges. It can be exported to a ``networkx.Graph`` for
visualisation with any backend (matplotlib, pyvis, ...).
"""

from __future__ import annotations

from typing import Iterable

import networkx as nx


class RelationGraph:
    """Maintain bidirectional relations between world entities.

    Nodes are referenced by a unique identifier (typically the entity name).
    Edges are undirected and may carry a ``relation`` attribute describing
    the type of connection.
    """

    def __init__(self) -> None:
        self._graph = nx.Graph()

    def add_entity(self, entity_id: str, **attrs: object) -> None:
        """Register a new entity node in the graph."""

        self._graph.add_node(entity_id, **attrs)

    def add_relation(self, a: str, b: str, relation: str) -> None:
        """Create a bidirectional relation between ``a`` and ``b``."""

        self._graph.add_edge(a, b, relation=relation)

    def remove_relation(self, a: str, b: str) -> None:
        """Remove the relation between ``a`` and ``b`` if it exists."""

        if self._graph.has_edge(a, b):
            self._graph.remove_edge(a, b)

    def relations_of(self, entity_id: str) -> Iterable[tuple[str, str]]:
        """Iterate over relations for ``entity_id``.

        Yields tuples of ``(other_id, relation_type)``.
        """

        for other, data in self._graph[entity_id].items():
            yield other, data.get("relation", "")

    def to_networkx(self) -> nx.Graph:
        """Return the underlying ``networkx`` graph instance."""

        return self._graph

    def plot(self) -> None:  # pragma: no cover - optional UI helper
        """Quick visualisation using ``matplotlib``.

        This method imports ``matplotlib`` lazily to avoid forcing the
        dependency for users that only need the data structure.
        """

        import matplotlib.pyplot as plt

        nx.draw_networkx(self._graph)
        plt.show()
