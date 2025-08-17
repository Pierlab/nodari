"""Procedural terrain generation helpers for war simulations.

This module exposes pure functions operating on a two-dimensional grid of
terrain **codes**. Each tile is represented by a single byte instead of a
Python string which drastically reduces memory requirements for large maps.
Every function returns both the mutated ``tiles`` structure and an
``obstacles`` set describing impassable coordinates. The implementation is
light‑weight and intentionally simple; it aims to offer varied landscapes
without adding heavy dependencies.
"""

from __future__ import annotations

import random
from typing import List, Sequence, Set, Tuple

from core.terrain import TILE_CODES

TileGrid = List[bytearray]
Coord = Tuple[int, int]


# ---------------------------------------------------------------------------
def generate_base(width: int, height: int, fill: str = "plain") -> TileGrid:
    """Return a ``height``×``width`` grid filled with ``fill`` terrain.

    The grid is implemented as a list of ``bytearray`` rows to minimise memory
    usage. ``fill`` may be any key from :data:`core.terrain.TILE_CODES`.
    """

    code = TILE_CODES.get(fill, TILE_CODES["plain"])
    return [bytearray([code] * width) for _ in range(height)]


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
                    tiles[py][px] = TILE_CODES["water"]
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
                    tiles[y][x] = TILE_CODES["water"]
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
    """Place groups of forest tiles forming contiguous patches.

    The previous implementation scattered individual forest tiles which
    produced very noisy maps and was surprisingly slow for large worlds.  The
    new approach creates a handful of circular clusters which is both visually
    pleasing and executes in linear time with respect to the number of forest
    tiles requested.
    """

    width = len(tiles[0])
    height = len(tiles)
    total = int(width * height * total_area_pct / 100)
    if total <= 0:
        return tiles, obstacles_set

    cluster_count = max(1, int(clusters))
    tiles_per_cluster = max(1, total // cluster_count)
    code = TILE_CODES["forest"]
    for _ in range(cluster_count):
        cx = random.randrange(width)
        cy = random.randrange(height)
        radius = int((tiles_per_cluster / 3.14) ** 0.5)
        radius = max(10, int(radius * random.uniform(1 - cluster_spread, 1 + cluster_spread)))
        for y in range(max(0, cy - radius), min(height, cy + radius + 1)):
            dy = y - cy
            dx = int((radius**2 - dy**2) ** 0.5)
            start = max(0, cx - dx)
            end = min(width, cx + dx + 1)
            tiles[y][start:end] = bytearray([code]) * (end - start)

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
    """Create simple mountain clusters quickly.

    ``perlin_scale`` and ``peak_density`` parameters are kept for API
    compatibility but are not used.  Instead of sampling a full altitude map we
    simply paint a number of circular clusters and optionally record a random
    altitude for each affected tile.  Tiles with altitude greater than
    ``obstacle_threshold`` are marked as obstacles.
    """

    width = len(tiles[0])
    height = len(tiles)
    total = int(width * height * total_area_pct / 100)
    if total <= 0:
        return tiles, obstacles_set

    cluster_count = max(1, int(peak_density * 10))
    tiles_per_cluster = max(1, total // cluster_count)
    code = TILE_CODES["mountain"]
    for _ in range(cluster_count):
        cx = random.randrange(width)
        cy = random.randrange(height)
        radius = int((tiles_per_cluster / 3.14) ** 0.5)
        radius = max(10, radius)
        for y in range(max(0, cy - radius), min(height, cy + radius + 1)):
            dy = y - cy
            dx = int((radius**2 - dy**2) ** 0.5)
            start = max(0, cx - dx)
            end = min(width, cx + dx + 1)
            tiles[y][start:end] = bytearray([code]) * (end - start)
            for x in range(start, end):
                alt = random.random()
                if altitude_map_out is not None:
                    altitude_map_out[y][x] = alt
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

    def _clusters(tile: int, pct: float) -> None:
        count = int(total * pct / 100)
        if count <= 0:
            return
        cluster_count = max(1, int((1 - clumpiness) * 5) + 1)
        tiles_per_cluster = max(1, count // cluster_count)
        for _ in range(cluster_count):
            cx = random.randrange(width)
            cy = random.randrange(height)
            radius = int((tiles_per_cluster / 3.14) ** 0.5)
            radius = max(10, radius)
            for y in range(max(0, cy - radius), min(height, cy + radius + 1)):
                dy = y - cy
                dx = int((radius**2 - dy**2) ** 0.5)
                start = max(0, cx - dx)
                end = min(width, cx + dx + 1)
                for x in range(start, end):
                    if tiles[y][x] == TILE_CODES["plain"]:
                        tiles[y][x] = tile

    _clusters(TILE_CODES["swamp"], swamp_pct)
    _clusters(TILE_CODES["desert"], desert_pct)
    return tiles, obstacles_set


__all__ = [
    "generate_base",
    "carve_river",
    "place_lake",
    "place_forest",
    "place_mountains",
    "place_swamp_desert",
]

