"""System resolving combat between opposing units on the same tile."""
from __future__ import annotations

import random
from typing import Iterable

from core.simnode import SystemNode, SimNode
from core.plugins import register_node_type
from nodes.unit import UnitNode
from nodes.terrain import TerrainNode
from nodes.transform import TransformNode
from nodes.nation import NationNode


class CombatSystem(SystemNode):
    """Resolve combat when opposing units occupy the same tile.

    Parameters
    ----------
    terrain:
        Reference to the :class:`TerrainNode` providing combat bonuses. If a
        string is supplied the node with this id is looked up on first update.
    """

    def __init__(self, terrain: TerrainNode | str | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._terrain_ref = terrain
        self.terrain: TerrainNode | None = terrain if isinstance(terrain, TerrainNode) else None

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
    def _get_nation(self, node: SimNode) -> NationNode | None:
        cur = node.parent
        while cur is not None:
            if isinstance(cur, NationNode):
                return cur
            cur = cur.parent
        return None

    # ------------------------------------------------------------------
    def _resolve_combat(self, a: UnitNode, b: UnitNode, x: int, y: int) -> None:
        a.engage(b)
        b.engage(a)
        bonus = self.terrain.get_combat_bonus(x, y) if self.terrain is not None else 0
        strength_a = a.size + bonus + random.randint(0, 10)
        strength_b = b.size + bonus + random.randint(0, 10)
        if strength_a == strength_b:
            return
        if strength_a > strength_b:
            loser = b
        else:
            loser = a
        loss = max(1, int(loser.size * 0.1))
        loser.size = max(0, loser.size - loss)
        nation = self._get_nation(loser)
        if nation is not None:
            nation.change_morale(-loss)
        loser.route(loss=loss)

    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        self._resolve_terrain()
        units = list(self._iter_units(self.parent or self))
        tiles: dict[tuple[int, int], list[UnitNode]] = {}
        for unit in units:
            transform = self._get_transform(unit)
            if transform is None:
                continue
            x, y = int(round(transform.position[0])), int(round(transform.position[1]))
            tiles.setdefault((x, y), []).append(unit)
        for (x, y), occupants in tiles.items():
            if len(occupants) < 2:
                continue
            nations: dict[NationNode, list[UnitNode]] = {}
            for unit in occupants:
                nation = self._get_nation(unit)
                if nation is None:
                    continue
                nations.setdefault(nation, []).append(unit)
            if len(nations) < 2:
                continue
            nation_units = list(nations.values())
            for i in range(len(nation_units)):
                for j in range(i + 1, len(nation_units)):
                    if not nation_units[i] or not nation_units[j]:
                        continue
                    self._resolve_combat(nation_units[i][0], nation_units[j][0], x, y)
        super().update(dt)


register_node_type("CombatSystem", CombatSystem)
