"""Procedural terrain generation helpers for war simulations.

This module exposes pure functions operating on a two-dimensional list of
terrain tiles. Every function returns both the mutated ``tiles`` structure and
an ``obstacles`` set describing impassable coordinates. The implementation is
light‑weight and intentionally simple; it aims to offer varied landscapes
without adding heavy dependencies.
"""

from __future__ import annotations

import random
from typing import List, Sequence, Set, Tuple

TileGrid = List[List[str]]
Coord = Tuple[int, int]


# ---------------------------------------------------------------------------
def generate_base(width: int, height: int, fill: str = "plain") -> TileGrid:
    """Return a ``height``×``width`` grid filled with ``fill`` terrain."""

    # Using list multiplication for the inner rows keeps the operation in
    # C‑code and avoids a costly Python loop for every column.
    return [[fill] * width for _ in range(height)]


# ---------------------------------------------------------------------------
def carve_river(
    tiles: TileGrid,
    *,
    start: Sequence[int],
    end: Sequence[int],
    width_min: int,
    width_max: int,
    meander: float,
    obstacles_set: Set[Coord],
) -> Tuple[TileGrid, Set[Coord]]:
    """Carve a river from ``start`` to ``end`` mutating ``tiles``.

    The river follows a simple noisy interpolation between the two points. At
    each step a perpendicular offset influenced by ``meander`` is applied.
    Coordinates covered by water are added to ``obstacles_set``.
    """

    width = len(tiles[0])
    height = len(tiles)
    sx, sy = start
    ex, ey = end
    length = max(abs(ex - sx), abs(ey - sy))
    for i in range(length + 1):
        t = i / length if length else 0
        x = sx + (ex - sx) * t
        y = sy + (ey - sy) * t
        # Apply perpendicular random offset for meandering
        off = (random.random() - 0.5) * 2 * meander * length
        if abs(ex - sx) >= abs(ey - sy):
            y += off
        else:
            x += off
        cx, cy = int(round(x)), int(round(y))
        river_width = random.randint(width_min, width_max)
        half = river_width // 2
        for dx in range(-half, half + 1):
            for dy in range(-half, half + 1):
                px, py = cx + dx, cy + dy
                if 0 <= px < width and 0 <= py < height:
                    tiles[py][px] = "water"
                    obstacles_set.add((px, py))
    return tiles, obstacles_set


# ---------------------------------------------------------------------------
def place_lake(
    tiles: TileGrid,
    *,
    center: Sequence[int],
    radius: int,
    irregularity: float,
    obstacles_set: Set[Coord],
) -> Tuple[TileGrid, Set[Coord]]:
    """Place a roughly circular lake around ``center``."""

    width = len(tiles[0])
    height = len(tiles)
    cx, cy = center
    for y in range(cy - radius, cy + radius + 1):
        for x in range(cx - radius, cx + radius + 1):
            if 0 <= x < width and 0 <= y < height:
                dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                jitter = random.uniform(-irregularity, irregularity) * radius
                if dist <= radius + jitter:
                    tiles[y][x] = "water"
                    obstacles_set.add((x, y))
    return tiles, obstacles_set


# ---------------------------------------------------------------------------
def place_forest(
    tiles: TileGrid,
    *,
    total_area_pct: float,
    clusters: int,
    cluster_spread: float,
    obstacles_set: Set[Coord],
) -> Tuple[TileGrid, Set[Coord]]:
    """Scatter forests across the map.

    The original clustering algorithm became extremely slow on very large
    maps. This simplified version merely scatters the required number of
    forest tiles randomly, ignoring the clustering parameters but keeping the
    same function signature for compatibility.
    """

    width = len(tiles[0])
    height = len(tiles)
    total = int(width * height * total_area_pct / 100)
    if total <= 0:
        return tiles, obstacles_set

    for _ in range(total):
        x = random.randrange(width)
        y = random.randrange(height)
        tiles[y][x] = "forest"

    return tiles, obstacles_set


# ---------------------------------------------------------------------------
def place_mountains(
    tiles: TileGrid,
    *,
    total_area_pct: float,
    perlin_scale: float,
    peak_density: float,
    altitude_map_out: List[List[float]] | None,
    obstacles_set: Set[Coord],
    obstacle_threshold: float = 0.75,
) -> Tuple[TileGrid, Set[Coord]]:
    """Scatter mountains randomly across the map.

    The previous implementation generated a full ``width``×``height`` altitude
    map which became prohibitively slow for large worlds. Instead we now sample
    only the number of tiles required by ``total_area_pct`` and assign them a
    random altitude. ``perlin_scale`` and ``peak_density`` are accepted for API
    compatibility but are not used by this lightweight generator.
    """

    width = len(tiles[0])
    height = len(tiles)
    total = int(width * height * total_area_pct / 100)

    for _ in range(total):
        x = random.randrange(width)
        y = random.randrange(height)
        alt = random.random()
        if altitude_map_out is not None:
            altitude_map_out[y][x] = alt
        tiles[y][x] = "mountain"
        if alt >= obstacle_threshold:
            obstacles_set.add((x, y))

    return tiles, obstacles_set


# ---------------------------------------------------------------------------
def place_swamp_desert(
    tiles: TileGrid,
    *,
    swamp_pct: float,
    desert_pct: float,
    clumpiness: float,
    obstacles_set: Set[Coord],
) -> Tuple[TileGrid, Set[Coord]]:
    """Place swamp and desert patches on the map."""

    width = len(tiles[0])
    height = len(tiles)
    total = width * height

    def _scatter(tile: str, count: int) -> None:
        placed = 0
        while placed < count:
            x = random.randrange(width)
            y = random.randrange(height)
            if tiles[y][x] == "plain":
                tiles[y][x] = tile
                placed += 1
            # expand around the tile to create clumps
            for nx, ny in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]:
                if placed >= count:
                    break
                if 0 <= nx < width and 0 <= ny < height:
                    if tiles[ny][nx] == "plain" and random.random() < clumpiness:
                        tiles[ny][nx] = tile
                        placed += 1

    _scatter("swamp", int(total * swamp_pct / 100))
    _scatter("desert", int(total * desert_pct / 100))
    return tiles, obstacles_set


__all__ = [
    "generate_base",
    "carve_river",
    "place_lake",
    "place_forest",
    "place_mountains",
    "place_swamp_desert",
]

