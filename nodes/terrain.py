"""Terrain node defining map tiles and modifiers."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from core.simnode import SimNode
from core.plugins import register_node_type
from core.terrain import TILE_CODES, TILE_NAMES


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
    obstacles:
        Optional list of impassable ``[x, y]`` coordinates such as rivers or
        mountains.
    """

    def __init__(
        self,
        tiles: List[List[int]] | List[List[str]],
        speed_modifiers: Optional[Dict[str, float]] | None = None,
        combat_bonuses: Optional[Dict[str, int]] | None = None,
        grid_type: str = "square",
        obstacles: Optional[List[List[int]]] | None = None,
        altitude_map: Optional[List[List[float]]] | None = None,
        terrain_params: Optional[Dict[str, Any]] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        # Convert any string based grid to byte codes
        if tiles and isinstance(tiles[0][0], str):
            self.tiles: List[bytearray] = [
                bytearray(TILE_CODES[t] for t in row) for row in tiles
            ]
        else:
            self.tiles = [bytearray(row) for row in tiles]
        self.height = len(self.tiles)
        self.width = len(self.tiles[0]) if self.tiles else 0
        default_speed = {
            "plain": 1.0,
            "forest": 0.7,
            "hill": 0.9,
            "water": 0.4,
            "mountain": 0.6,
            "swamp": 0.5,
            "desert": 0.8,
            "road": 1.0,
        }
        default_combat = {
            "plain": 0,
            "forest": 1,
            "hill": 2,
            "water": -2,
            "mountain": 3,
            "swamp": -1,
            "desert": 0,
            "road": 0,
        }
        sm = speed_modifiers or default_speed
        cb = combat_bonuses or default_combat
        self.speed_modifiers = {TILE_CODES[k]: v for k, v in sm.items()}
        self.combat_bonuses = {TILE_CODES[k]: v for k, v in cb.items()}
        self.grid_type = grid_type
        if self.grid_type not in {"square", "hex"}:
            raise ValueError("grid_type must be 'square' or 'hex'")
        self.obstacles = {tuple(o) for o in (obstacles or [])}
        self.altitude_map = altitude_map
        self.params = terrain_params or {}

    # ------------------------------------------------------------------
    def get_tile_code(self, x: int, y: int) -> int | None:
        """Return the terrain code at ``(x, y)`` or ``None`` if out of bounds."""

        if 0 <= y < self.height and 0 <= x < self.width:
            return self.tiles[y][x]
        return None

    # ------------------------------------------------------------------
    def get_tile(self, x: int, y: int) -> str | None:
        """Return the terrain name at ``(x, y)`` or ``None`` if out of bounds."""

        code = self.get_tile_code(x, y)
        if code is None:
            return None
        return TILE_NAMES.get(code)

    # ------------------------------------------------------------------
    def get_speed_modifier(self, x: int, y: int) -> float:
        """Return movement speed modifier for tile at ``(x, y)``."""

        code = self.get_tile_code(x, y)
        if code is None:
            return 1.0
        return self.speed_modifiers.get(code, 1.0)

    # ------------------------------------------------------------------
    def get_combat_bonus(self, x: int, y: int) -> int:
        """Return combat bonus for tile at ``(x, y)``."""

        code = self.get_tile_code(x, y)
        if code is None:
            return 0
        return self.combat_bonuses.get(code, 0)

    # ------------------------------------------------------------------
    def is_obstacle(self, x: int, y: int) -> bool:
        """Return ``True`` if ``(x, y)`` is marked as an obstacle."""

        return (x, y) in self.obstacles

    # ------------------------------------------------------------------
    def get_altitude(self, x: int, y: int) -> float | None:
        """Return altitude value at ``(x, y)`` if an altitude map exists."""

        if self.altitude_map is None:
            return None
        if 0 <= y < len(self.altitude_map) and 0 <= x < len(self.altitude_map[0]):
            return self.altitude_map[y][x]
        return None

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
