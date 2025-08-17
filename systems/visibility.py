"""System managing fog of war and enemy spotting."""
from __future__ import annotations

from typing import Dict, Iterable, List, Set, Tuple

from core.simnode import SystemNode, SimNode
from core.plugins import register_node_type
from nodes.unit import UnitNode
from nodes.transform import TransformNode
from nodes.nation import NationNode
from config import WORLD_SCALE_M


class VisibilitySystem(SystemNode):
    """Track visible tiles per nation and emit intel events."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        # Mapping of nation id to set of visible tile coordinates
        self.visible_tiles: Dict[int, Set[Tuple[int, int]]] = {}
        self._time = 0.0

    # ------------------------------------------------------------------
    def _iter_units(self, node: SimNode) -> Iterable[UnitNode]:
        for child in node.children:
            if isinstance(child, UnitNode):
                yield child
            yield from self._iter_units(child)

    # ------------------------------------------------------------------
    def _get_transform(self, node: SimNode) -> TransformNode | None:
        if isinstance(node, TransformNode):
            return node
        for child in node.children:
            if isinstance(child, TransformNode):
                return child
        return None

    # ------------------------------------------------------------------
    def _get_nation(self, node: SimNode) -> NationNode | None:
        cur = node.parent
        while cur is not None:
            if isinstance(cur, NationNode):
                return cur
            cur = cur.parent
        return None

    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        """Recompute visibility and publish spotting events."""

        super().update(dt)
        self._time += dt
        self.visible_tiles.clear()

        units: List[Tuple[UnitNode, TransformNode, NationNode]] = []
        for unit in self._iter_units(self.parent or self):
            transform = self._get_transform(unit)
            nation = self._get_nation(unit)
            if transform is None or nation is None:
                continue
            units.append((unit, transform, nation))

        # Compute visible tiles per nation
        for unit, transform, nation in units:
            radius = getattr(unit, "vision_radius_m", 0.0) / WORLD_SCALE_M
            x0, y0 = int(round(transform.position[0])), int(round(transform.position[1]))
            tiles = self.visible_tiles.setdefault(id(nation), set())
            r = int(round(radius))
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    if dx * dx + dy * dy <= r * r:
                        tiles.add((x0 + dx, y0 + dy))

        # Spot enemies
        for unit, transform, nation in units:
            pos = (int(round(transform.position[0])), int(round(transform.position[1])))
            for other_nation_id, tiles in self.visible_tiles.items():
                if other_nation_id == id(nation):
                    continue
                if pos in tiles:
                    payload = {
                        "nation": getattr(nation, "name", ""),
                        "enemy": getattr(unit, "name", ""),
                        "position": list(pos),
                        "timestamp": self._time,
                        "confidence": 1.0,
                    }
                    # Broadcast so strategists can hear it
                    self.emit("enemy_spotted", payload, direction="up")


register_node_type("VisibilitySystem", VisibilitySystem)
