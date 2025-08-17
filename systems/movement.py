"""System to move units toward targets considering terrain and morale."""
from __future__ import annotations

from math import atan2, cos, hypot, sin, pi
from typing import Iterable, List, Optional
import random

from core.simnode import SystemNode, SimNode
from core.plugins import register_node_type
from nodes.unit import UnitNode
from nodes.terrain import TerrainNode
from nodes.transform import TransformNode
from systems.pathfinding import PathfindingSystem


class MovementSystem(SystemNode):
    """Move units each update toward their target position.

    The movement speed of a unit is affected by the terrain tile modifier and
    the unit's morale (scaled between ``0`` and ``1``).

    Parameters
    ----------
    terrain:
        Reference to the :class:`TerrainNode` providing tile modifiers. If a
        string is supplied the node with this id is looked up on first update.
    obstacles:
        Optional list of additional impassable ``[x, y]`` coordinates. These
        are merged with obstacles defined on the :class:`TerrainNode`.
    """

    def __init__(
        self,
        terrain: TerrainNode | str | None = None,
        obstacles: Optional[List[List[int]]] | None = None,
        direction_noise: float = 0.0,
        avoid_obstacles: bool = False,
        pathfinder: PathfindingSystem | str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._terrain_ref = terrain
        self.terrain: TerrainNode | None = terrain if isinstance(terrain, TerrainNode) else None
        self.obstacles = {tuple(o) for o in (obstacles or [])}
        self.direction_noise = direction_noise
        self.avoid_obstacles = avoid_obstacles
        self._pathfinder_ref = pathfinder
        self.pathfinder: PathfindingSystem | None = (
            pathfinder if isinstance(pathfinder, PathfindingSystem) else None
        )

    # ------------------------------------------------------------------
    def _resolve_terrain(self) -> None:
        if self.terrain is not None:
            return
        name = self._terrain_ref if isinstance(self._terrain_ref, str) else None
        root = self.parent
        if root is None:
            return
        self.terrain = self._find_terrain(root, name)

    def _find_terrain(self, node: SimNode, name: str | None) -> TerrainNode | None:
        if isinstance(node, TerrainNode) and (name is None or node.name == name):
            return node
        for child in node.children:
            found = self._find_terrain(child, name)
            if found is not None:
                return found
        return None

    # ------------------------------------------------------------------
    def _resolve_pathfinder(self) -> None:
        if self.pathfinder is not None:
            return
        name = self._pathfinder_ref if isinstance(self._pathfinder_ref, str) else None
        root = self.parent
        if root is None:
            return
        self.pathfinder = self._find_pathfinder(root, name)

    def _find_pathfinder(self, node: SimNode, name: str | None) -> PathfindingSystem | None:
        if isinstance(node, PathfindingSystem) and (name is None or node.name == name):
            return node
        for child in node.children:
            found = self._find_pathfinder(child, name)
            if found is not None:
                return found
        return None

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
    def update(self, dt: float) -> None:
        self._resolve_terrain()
        self._resolve_pathfinder()
        blocked_tiles = set(self.obstacles)
        for other in self._iter_units(self.parent or self):
            if getattr(other, "state", "") == "fighting":
                tr = self._get_transform(other)
                if tr is not None:
                    blocked_tiles.add((int(round(tr.position[0])), int(round(tr.position[1]))))
        for unit in self._iter_units(self.parent or self):
            if getattr(unit, "state", "") == "fighting":
                continue
            if not hasattr(unit, "target") or unit.target is None:
                continue
            transform = self._get_transform(unit)
            if transform is None:
                continue
            tx, ty = transform.position
            if hasattr(unit, "_path") and unit._path:
                gx, gy = unit._path[0]
            else:
                gx, gy = unit.target
            dx, dy = gx - tx, gy - ty
            dist = hypot(dx, dy)
            if dist == 0:
                if hasattr(unit, "_path") and unit._path:
                    unit._path.pop(0)
                    continue
                unit.state = "idle"
                continue
            speed = unit.speed
            if self.terrain is not None:
                speed *= self.terrain.get_speed_modifier(int(tx), int(ty))
            speed *= max(unit.morale, 0) / 100.0
            step = speed * dt
            if step <= 0:
                continue
            if step >= dist:
                new_x, new_y = gx, gy
            else:
                angle = atan2(dy, dx)
                if self.direction_noise > 0:
                    angle += random.uniform(-self.direction_noise, self.direction_noise)
                nx = tx + cos(angle) * step
                ny = ty + sin(angle) * step
                new_x, new_y = nx, ny
            ix, iy = int(round(new_x)), int(round(new_y))
            blocked = (ix, iy) in blocked_tiles or (
                self.terrain is not None and self.terrain.is_obstacle(ix, iy)
            )
            if blocked:
                if not self.avoid_obstacles or self.pathfinder is None:
                    continue
                start = (int(round(tx)), int(round(ty)))
                goal = (int(round(unit.target[0])), int(round(unit.target[1])))
                path = self.pathfinder.find_path(start, goal, blocked_tiles)
                if len(path) > 1:
                    unit._path = path[1:]
                continue
            transform.position[0] = new_x
            transform.position[1] = new_y
            unit.state = "moving"
            if hasattr(unit, "_path") and unit._path and (ix, iy) == unit._path[0]:
                unit._path.pop(0)
            unit.emit(
                "unit_moved",
                {"from": [tx, ty], "to": [new_x, new_y]},
                direction="up",
            )
        super().update(dt)


register_node_type("MovementSystem", MovementSystem)
