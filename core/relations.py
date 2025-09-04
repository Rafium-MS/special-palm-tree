"""Utility classes for managing bidirectional relations between entities.

The original implementation wrapped :mod:`networkx` directly which meant the
library had to be installed even when only the basic data structure was
required.  This module now provides a small in-house graph structure that
covers the limited feature set we need (bidirectional edges with attributes)
while keeping :mod:`networkx` as an optional dependency for visualisation.
"""

from __future__ import annotations

from typing import Dict, Iterable


class _MiniGraph:
    """Very small undirected graph with edge and node attributes.

    The implementation is intentionally tiny – it only supports the handful of
    operations required by :class:`RelationGraph`.  Nodes are stored in a
    dictionary mapping to their neighbours and optional edge attribute
    dictionaries.
    """

    def __init__(self) -> None:
        self._adj: Dict[str, Dict[str, Dict[str, object]]] = {}
        self._node_attrs: Dict[str, Dict[str, object]] = {}

    # -- basic mutation -------------------------------------------------
    def add_node(self, node: str, **attrs: object) -> None:
        self._adj.setdefault(node, {})
        if attrs:
            self._node_attrs.setdefault(node, {}).update(attrs)

    def add_edge(self, a: str, b: str, **attrs: object) -> None:
        self.add_node(a)
        self.add_node(b)
        self._adj[a][b] = attrs
        self._adj[b][a] = attrs

    def remove_edge(self, a: str, b: str) -> None:
        self._adj.get(a, {}).pop(b, None)
        self._adj.get(b, {}).pop(a, None)

    # -- helpers --------------------------------------------------------
    def has_edge(self, a: str, b: str) -> bool:
        return b in self._adj.get(a, {})

    def neighbors(self, node: str) -> Dict[str, Dict[str, object]]:
        return self._adj.get(node, {})

    def nodes(self) -> Iterable[str]:
        return self._adj.keys()

    def node_attrs(self, node: str) -> Dict[str, object]:
        return self._node_attrs.get(node, {})

    def edges(self) -> Iterable[tuple[str, str, Dict[str, object]]]:
        seen = set()
        for a, nbrs in self._adj.items():
            for b, data in nbrs.items():
                if (b, a) in seen:
                    continue
                seen.add((a, b))
                yield a, b, data


class RelationGraph:
    """Maintain bidirectional relations between world entities.

    Nodes are referenced by a unique identifier (typically the entity name).
    Edges are undirected and may carry a ``relation`` attribute describing
    the type of connection.
    """

    def __init__(self) -> None:
        self._graph = _MiniGraph()

    def add_entity(self, entity_id: str, **attrs: object) -> None:
        """Register a new entity node in the graph."""

        self._graph.add_node(entity_id, **attrs)

    def add_relation(self, a: str, b: str, relation: str) -> None:
        """Create a bidirectional relation between ``a`` and ``b``."""

        self._graph.add_edge(a, b, relation=relation)

    def remove_relation(self, a: str, b: str) -> None:
        """Remove the relation between ``a`` and ``b`` if it exists."""

        self._graph.remove_edge(a, b)

    def relations_of(self, entity_id: str) -> Iterable[tuple[str, str]]:
        """Iterate over relations for ``entity_id``.

        Yields tuples of ``(other_id, relation_type)``.
        """

        for other, data in self._graph.neighbors(entity_id).items():
            yield other, data.get("relation", "")

    def to_networkx(self):  # pragma: no cover - convenience helper
        """Return a ``networkx.Graph`` representing the relations.

        ``networkx`` is imported lazily so that it remains an optional
        dependency.  A :class:`ModuleNotFoundError` is raised if the package is
        missing.
        """

        try:
            import networkx as nx  # type: ignore
        except ModuleNotFoundError as exc:  # pragma: no cover - environment dep
            raise ModuleNotFoundError(
                "networkx is required for converting to a networkx.Graph"
            ) from exc

        g = nx.Graph()
        for node in self._graph.nodes():
            g.add_node(node, **self._graph.node_attrs(node))
        for a, b, data in self._graph.edges():
            g.add_edge(a, b, **data)
        return g

    def plot(self) -> None:  # pragma: no cover - optional UI helper
        """Quick visualisation using ``matplotlib``.

        Both :mod:`networkx` and :mod:`matplotlib` are imported lazily to avoid
        forcing the dependencies for users that only need the data structure.
        """

        try:
            import matplotlib.pyplot as plt  # type: ignore
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError("matplotlib is required for plotting") from exc

        nx_graph = self.to_networkx()
        # networkx will be imported by ``to_networkx``
        import networkx as nx  # type: ignore

        nx.draw_networkx(nx_graph)
        plt.show()
