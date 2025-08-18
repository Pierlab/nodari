"""Simple AI system reacting to idle units."""
from __future__ import annotations

import random

from core.simnode import SystemNode, SimNode
from core.plugins import register_node_type
from nodes.worker import WorkerNode
from nodes.builder import BuilderNode
from nodes.building import BuildingNode
from nodes.transform import TransformNode
from nodes.nation import NationNode
from nodes.unit import UnitNode
from nodes.terrain import TerrainNode
from systems.visibility import VisibilitySystem


class AISystem(SystemNode):
    """Assign tasks to idle workers and explore unknown territory."""

    def __init__(
        self,
        exploration_radius: int = 5,
        capital_min_radius: int = 0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.exploration_radius = exploration_radius
        self.capital_min_radius = capital_min_radius
        self.on_event("unit_idle", self._on_unit_idle)
        self._last_city: dict[int, SimNode] = {}
        self._init_last_cities()

    # ------------------------------------------------------------------
    def _init_last_cities(self) -> None:
        """Seed ``_last_city`` with each nation's capital."""
        root = self
        while root.parent is not None:
            root = root.parent
        for nation in self._iter_nations(root):
            key = id(nation)
            if key in self._last_city:
                continue
            city = BuildingNode(parent=root, type="city")
            TransformNode(parent=city, position=list(nation.capital_position))
            self._last_city[key] = city

    # ------------------------------------------------------------------
    def _on_unit_idle(self, origin: SimNode, _event: str, _payload: dict) -> None:
        if not isinstance(origin, WorkerNode):
            return
        if origin.find_task():
            return
        transform = self._get_transform(origin)
        if transform is None:
            return
        if isinstance(origin, BuilderNode) and self.capital_min_radius > 0:
            nation = self._get_nation(origin)
            if nation is not None:
                key = id(nation)
                last = self._last_city.get(key)
                if last is None:
                    root = self
                    while root.parent is not None:
                        root = root.parent
                    last = BuildingNode(parent=root, type="city")
                    TransformNode(parent=last, position=list(nation.capital_position))
                    self._last_city[key] = last
                last_tr = self._get_transform(last)
                if last_tr is not None:
                    x0 = int(round(transform.position[0]))
                    y0 = int(round(transform.position[1]))
                    lx = int(round(last_tr.position[0]))
                    ly = int(round(last_tr.position[1]))
                    dx = x0 - lx
                    dy = y0 - ly
                    if dx * dx + dy * dy >= self.capital_min_radius * self.capital_min_radius:
                        city = origin.build_city([x0, y0], last, emit_idle=False)
                        if city is not None:
                            self._last_city[key] = city
                            origin.emit("unit_idle", {}, direction="up")
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
                if not self._beyond_capital_radius(origin, pos):
                    continue
                if not self._is_free(pos):
                    continue
                origin.target = [pos[0], pos[1]]
                origin.state = "moving"
                origin.emit("unit_move", {"to": origin.target}, direction="up")
                return
        # fallback random move if everything explored
        for _ in range(10):
            dx = random.randint(-radius, radius)
            dy = random.randint(-radius, radius)
            pos = (x0 + dx, y0 + dy)
            if not self._beyond_capital_radius(origin, pos):
                continue
            if not self._is_free(pos):
                continue
            origin.target = [pos[0], pos[1]]
            origin.state = "moving"
            origin.emit("unit_move", {"to": origin.target}, direction="up")
            return

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
    def _beyond_capital_radius(
        self, unit: SimNode, pos: tuple[int, int]
    ) -> bool:
        nation = self._get_nation(unit)
        if nation is None:
            return True
        cx, cy = nation.capital_position
        dx = pos[0] - cx
        dy = pos[1] - cy
        return dx * dx + dy * dy >= self.capital_min_radius * self.capital_min_radius

    # ------------------------------------------------------------------
    def _iter_units(self, node: SimNode):
        for child in node.children:
            if isinstance(child, UnitNode):
                yield child
            yield from self._iter_units(child)

    # ------------------------------------------------------------------
    def _iter_nations(self, node: SimNode):
        for child in node.children:
            if isinstance(child, NationNode):
                yield child
            yield from self._iter_nations(child)

    # ------------------------------------------------------------------
    def _find_terrain(self) -> TerrainNode | None:
        node = self
        while node.parent is not None:
            node = node.parent
        for child in node.children:
            if isinstance(child, TerrainNode):
                return child
        return None

    # ------------------------------------------------------------------
    def _is_free(self, pos: tuple[int, int]) -> bool:
        terrain = self._find_terrain()
        if terrain is not None and terrain.is_obstacle(pos[0], pos[1]):
            return False
        root = self
        while root.parent is not None:
            root = root.parent
        for unit in self._iter_units(root):
            tr = self._get_transform(unit)
            if tr is None:
                continue
            ux = int(round(tr.position[0]))
            uy = int(round(tr.position[1]))
            if (ux, uy) == pos:
                return False
        return True

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
