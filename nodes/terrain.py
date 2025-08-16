"""Terrain node defining map tiles and modifiers."""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from core.simnode import SimNode
from core.plugins import register_node_type


class TerrainNode(SimNode):
    """Store terrain tiles and provide movement/combat modifiers.

    Parameters
    ----------
    tiles:
        Two-dimensional list describing the terrain type at each map
        position.
    speed_modifiers:
        Optional mapping of terrain type to movement speed modifier.
    combat_bonuses:
        Optional mapping of terrain type to combat bonus value.
    grid_type:
        ``"square"`` for a 4-neighbour grid or ``"hex"`` for a hexagonal
        layout. Only the square grid is fully supported for now.
    """

    def __init__(
        self,
        tiles: List[List[str]],
        speed_modifiers: Optional[Dict[str, float]] | None = None,
        combat_bonuses: Optional[Dict[str, int]] | None = None,
        grid_type: str = "square",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.tiles = tiles
        self.height = len(tiles)
        self.width = len(tiles[0]) if tiles else 0
        self.speed_modifiers = speed_modifiers or {
            "plain": 1.0,
            "forest": 0.7,
            "hill": 0.9,
        }
        self.combat_bonuses = combat_bonuses or {
            "plain": 0,
            "forest": 1,
            "hill": 2,
        }
        self.grid_type = grid_type
        if self.grid_type not in {"square", "hex"}:
            raise ValueError("grid_type must be 'square' or 'hex'")

    # ------------------------------------------------------------------
    def get_tile(self, x: int, y: int) -> str | None:
        """Return the terrain type at ``(x, y)`` or ``None`` if out of bounds."""

        if 0 <= y < self.height and 0 <= x < self.width:
            return self.tiles[y][x]
        return None

    # ------------------------------------------------------------------
    def get_speed_modifier(self, x: int, y: int) -> float:
        """Return movement speed modifier for tile at ``(x, y)``."""

        terrain = self.get_tile(x, y)
        if terrain is None:
            return 1.0
        return self.speed_modifiers.get(terrain, 1.0)

    # ------------------------------------------------------------------
    def get_combat_bonus(self, x: int, y: int) -> int:
        """Return combat bonus for tile at ``(x, y)``."""

        terrain = self.get_tile(x, y)
        if terrain is None:
            return 0
        return self.combat_bonuses.get(terrain, 0)

    # ------------------------------------------------------------------
    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Return neighbouring coordinates for the given tile.

        For a square grid this returns up to four neighbours (N, S, E, W).
        For a hex grid, up to six neighbours are returned using a simple
        axial coordinate system.
        """

        if self.grid_type == "square":
            offsets = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        else:  # hex grid
            offsets = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]
        neighbors: List[Tuple[int, int]] = []
        for dx, dy in offsets:
            nx, ny = x + dx, y + dy
            if 0 <= ny < self.height and 0 <= nx < self.width:
                neighbors.append((nx, ny))
        return neighbors


register_node_type("TerrainNode", TerrainNode)
