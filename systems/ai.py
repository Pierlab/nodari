"""Simple AI system reacting to idle units."""
from __future__ import annotations

import logging
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

logger = logging.getLogger(__name__)


class AISystem(SystemNode):
    """Assign tasks to idle workers and explore unknown territory."""

    def __init__(
        self,
        exploration_radius: int = 5,
        capital_min_radius: int = 0,

      
        city_influence_radius: int = 0,

      
        builder_spawn_interval: float = 0.0,
        build_duration: float = 0.0,

      
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.exploration_radius = exploration_radius
        self.capital_min_radius = capital_min_radius

        
        self.city_influence_radius = city_influence_radius

        
        self.builder_spawn_interval = builder_spawn_interval
        self._spawn_acc = 0.0

        self.build_duration = build_duration


        self.on_event("unit_idle", self._on_unit_idle)
        self.on_event("city_built", self._on_city_built)
        self._last_city: dict[int, SimNode] = {}
        self._init_last_cities()

    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        if self.builder_spawn_interval > 0:
            self._spawn_acc += dt
            if self._spawn_acc >= self.builder_spawn_interval:
                self._spawn_acc -= self.builder_spawn_interval
                root = self
                while root.parent is not None:
                    root = root.parent
                for nation in self._iter_nations(root):
                    count = sum(1 for c in nation.children if isinstance(c, BuilderNode))
                    builder = BuilderNode(
                        name=f"{nation.name}_builder_{count + 1}",
                        state="exploring",
                        speed=1.0,
                        morale=100,
                        build_duration=self.build_duration,
                    )
                    builder.add_child(
                        TransformNode(position=list(nation.capital_position))
                    )
                    nation.add_child(builder)
                    logger.info("Spawned builder %s for %s", builder.name, nation.name)
                    builder.emit("unit_idle", {}, direction="up")
        # After potentially spawning builders, check all existing builders that
        # are currently exploring to see whether they should establish a new
        # city.  A builder found outside the cumulative influence of all
        # existing cities will immediately construct a new one and extend the
        # nation's influence area.
        root = self
        while root.parent is not None:
            root = root.parent
        for nation in self._iter_nations(root):
            key = id(nation)
            last = self._last_city.get(key)
            if last is None:
                # Fallback to the capital if the last city tracking was lost
                last = BuildingNode(type="city")
                TransformNode(parent=last, position=list(nation.capital_position))
                self._last_city[key] = last
            last_tr = self._get_transform(last)
            if last_tr is None:
                continue
            lx = int(round(last_tr.position[0]))
            ly = int(round(last_tr.position[1]))
            radius = getattr(nation, "city_influence_radius", self.city_influence_radius)
            for unit in self._iter_units(nation):
                if not isinstance(unit, BuilderNode) or unit.state != "exploring":
                    continue
                tr = self._get_transform(unit)
                if tr is None:
                    continue
                x = int(round(tr.position[0]))
                y = int(round(tr.position[1]))
                dx = x - lx
                dy = y - ly
                if dx * dx + dy * dy < self.capital_min_radius * self.capital_min_radius:
                    continue
                too_close = False
                for cx, cy in nation.cities_positions:
                    ddx = x - int(round(cx))
                    ddy = y - int(round(cy))
                    if ddx * ddx + ddy * ddy < radius * radius:
                        too_close = True
                        break
                if too_close:
                    continue
                unit.begin_construction((x, y), last)
        super().update(dt)

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
            city = BuildingNode(type="city")
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
                    last = BuildingNode(type="city")
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
                        radius = getattr(
                            nation, "city_influence_radius", self.city_influence_radius
                        )
                        too_close = False
                        for cx, cy in nation.cities_positions:
                            ddx = x0 - int(round(cx))
                            ddy = y0 - int(round(cy))
                            if ddx * ddx + ddy * ddy < radius * radius:
                                too_close = True
                                break
                        if not too_close:
                            origin.begin_construction((x0, y0), last)
                            return
        origin.state = "exploring"
        origin.target = None

    # ------------------------------------------------------------------
    def _on_city_built(self, origin: SimNode, _event: str, payload: dict) -> None:
        if not isinstance(origin, BuilderNode):
            return
        nation = self._get_nation(origin)
        city = payload.get("city")
        if nation is not None and isinstance(city, BuildingNode):
            self._last_city[id(nation)] = city

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
