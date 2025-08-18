"""Simple AI system reacting to idle units."""
from __future__ import annotations

import random

from core.simnode import SystemNode, SimNode
from core.plugins import register_node_type
from nodes.worker import WorkerNode
from nodes.transform import TransformNode
from nodes.nation import NationNode
from systems.visibility import VisibilitySystem


class AISystem(SystemNode):
    """Assign tasks to idle workers and explore unknown territory."""

    def __init__(self, exploration_radius: int = 5, **kwargs) -> None:
        super().__init__(**kwargs)
        self.exploration_radius = exploration_radius
        self.on_event("unit_idle", self._on_unit_idle)

    # ------------------------------------------------------------------
    def _on_unit_idle(self, origin: SimNode, _event: str, _payload: dict) -> None:
        if not isinstance(origin, WorkerNode):
            return
        if origin.find_task():
            return
        transform = self._get_transform(origin)
        if transform is None:
            return
        x0 = int(round(transform.position[0]))
        y0 = int(round(transform.position[1]))
        radius = self.exploration_radius
        explored = self._get_explored(origin)
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                if dx * dx + dy * dy > radius * radius:
                    continue
                pos = (x0 + dx, y0 + dy)
                if pos in explored:
                    continue
                origin.target = [pos[0], pos[1]]
                origin.state = "moving"
                origin.emit("unit_move", {"to": origin.target}, direction="up")
                return
        # fallback random move if everything explored
        dx = random.randint(-radius, radius)
        dy = random.randint(-radius, radius)
        origin.target = [x0 + dx, y0 + dy]
        origin.state = "moving"
        origin.emit("unit_move", {"to": origin.target}, direction="up")

    # ------------------------------------------------------------------
    def _get_transform(self, node: SimNode) -> TransformNode | None:
        if isinstance(node, TransformNode):
            return node
        for child in node.children:
            if isinstance(child, TransformNode):
                return child
        return None

    # ------------------------------------------------------------------
    def _get_explored(self, unit: SimNode) -> set[tuple[int, int]]:
        vis = self._find_visibility()
        if vis is None:
            return set()
        nation = self._get_nation(unit)
        if nation is None:
            return set()
        return vis.visible_tiles.get(id(nation), set())

    # ------------------------------------------------------------------
    def _get_nation(self, node: SimNode) -> NationNode | None:
        cur = node.parent
        while cur is not None:
            if isinstance(cur, NationNode):
                return cur
            cur = cur.parent
        return None

    # ------------------------------------------------------------------
    def _find_visibility(self) -> VisibilitySystem | None:
        node = self
        while node.parent is not None:
            node = node.parent
        for child in node.children:
            if isinstance(child, VisibilitySystem):
                return child
        return None


register_node_type("AISystem", AISystem)
