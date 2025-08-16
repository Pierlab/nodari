"""System to move units toward targets considering terrain and morale."""
from __future__ import annotations

from math import hypot
from typing import Iterable, List, Optional

from core.simnode import SystemNode, SimNode
from core.plugins import register_node_type
from nodes.unit import UnitNode
from nodes.terrain import TerrainNode
from nodes.transform import TransformNode


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
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._terrain_ref = terrain
        self.terrain: TerrainNode | None = terrain if isinstance(terrain, TerrainNode) else None
        self.obstacles = {tuple(o) for o in (obstacles or [])}

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
        for unit in self._iter_units(self.parent or self):
            if not hasattr(unit, "target") or unit.target is None:
                continue
            transform = self._get_transform(unit)
            if transform is None:
                continue
            tx, ty = transform.position
            gx, gy = unit.target
            dx, dy = gx - tx, gy - ty
            dist = hypot(dx, dy)
            if dist == 0:
                unit.state = "idle"
                continue
            # compute speed modifiers
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
                nx = tx + dx / dist * step
                ny = ty + dy / dist * step
                new_x, new_y = nx, ny
            ix, iy = int(round(new_x)), int(round(new_y))
            blocked = (ix, iy) in self.obstacles
            if not blocked and self.terrain is not None:
                blocked = self.terrain.is_obstacle(ix, iy)
            if blocked:
                continue
            transform.position[0] = new_x
            transform.position[1] = new_y
            unit.state = "moving"
            unit.emit(
                "unit_moved",
                {"from": [tx, ty], "to": [new_x, new_y]},
                direction="up",
            )
        super().update(dt)


register_node_type("MovementSystem", MovementSystem)
