"""System aggregating morale changes and triggering nation collapse."""
from __future__ import annotations

from typing import Dict, Iterable

from core.simnode import SystemNode, SimNode
from core.plugins import register_node_type
from nodes.nation import NationNode


class MoralSystem(SystemNode):
    """Track morale of nations and emit collapse when it reaches zero.

    Parameters
    ----------
    collapse_threshold:
        Morale value at or below which a nation collapses.
    """

    def __init__(self, collapse_threshold: int = 0, **kwargs) -> None:
        super().__init__(**kwargs)
        self.collapse_threshold = collapse_threshold
        self._morale: Dict[NationNode, int] = {}
        self._collapsed: set[NationNode] = set()

    # ------------------------------------------------------------------
    def _iter_nations(self, node: SimNode) -> Iterable[NationNode]:
        for child in node.children:
            if isinstance(child, NationNode):
                yield child
            yield from self._iter_nations(child)

    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        root = self.parent or self
        for nation in self._iter_nations(root):
            morale = nation.morale
            self._morale[nation] = morale
            if morale <= self.collapse_threshold and nation not in self._collapsed:
                nation.emit("nation_collapsed", {"morale": morale})
                self._collapsed.add(nation)
        super().update(dt)


register_node_type("MoralSystem", MoralSystem)
