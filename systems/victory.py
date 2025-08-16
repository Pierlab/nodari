from __future__ import annotations

"""System monitoring victory conditions such as capital capture."""

from typing import Iterable

from core.simnode import SystemNode, SimNode
from core.plugins import register_node_type
from nodes.nation import NationNode
from nodes.unit import UnitNode
from nodes.transform import TransformNode


class VictorySystem(SystemNode):
    """Detect when enemy units capture a nation's capital.

    Parameters
    ----------
    capture_unit_threshold:
        Number of enemy units required on a capital tile to capture it.
    """

    def __init__(self, capture_unit_threshold: int = 3, **kwargs) -> None:
        super().__init__(**kwargs)
        self.capture_unit_threshold = capture_unit_threshold
        self._captured: set[NationNode] = set()

    # ------------------------------------------------------------------
    def _iter_nations(self, node: SimNode) -> Iterable[NationNode]:
        for child in node.children:
            if isinstance(child, NationNode):
                yield child
            yield from self._iter_nations(child)

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
    def _find_nation(self, node: SimNode) -> NationNode | None:
        cur = node.parent
        while cur is not None:
            if isinstance(cur, NationNode):
                return cur
            cur = cur.parent
        return None

    # ------------------------------------------------------------------
    def update(self, dt: float) -> None:
        root = self.parent or self
        units = list(self._iter_units(root))
        for nation in self._iter_nations(root):
            if nation in self._captured:
                continue
            cx, cy = nation.capital_position
            count = 0
            for unit in units:
                owner = self._find_nation(unit)
                if owner is nation:
                    continue
                transform = self._get_transform(unit)
                if transform is None:
                    continue
                ux, uy = transform.position
                if int(round(ux)) == cx and int(round(uy)) == cy:
                    count += 1
                    if count >= self.capture_unit_threshold:
                        nation.capture_capital()
                        self._captured.add(nation)
                        break
        super().update(dt)


register_node_type("VictorySystem", VictorySystem)
