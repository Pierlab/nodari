"""Tests for procedural terrain generation helpers."""

from __future__ import annotations

import random

from tools.terrain_generators import (
    carve_river,
    generate_base,
    place_forest,
    place_lake,
    place_mountains,
    place_swamp_desert,
)
from core.terrain import TILE_CODES


def test_generate_base_and_lake() -> None:
    random.seed(0)
    tiles = generate_base(50, 30)
    tiles, obstacles = place_lake(
        tiles,
        center=(25, 15),
        radius=5,
        irregularity=0.2,
        obstacles_set=set(),
    )
    assert tiles[15][25] == TILE_CODES["water"]
    assert obstacles, "lake should add obstacles"


def test_carve_river_creates_water_line() -> None:
    random.seed(1)
    tiles = generate_base(40, 20)
    tiles, obstacles = carve_river(
        tiles,
        start=(0, 10),
        end=(39, 10),
        width_min=2,
        width_max=2,
        meander=0.0,
        obstacles_set=set(),
    )
    assert all(tiles[10][x] == TILE_CODES["water"] for x in range(40))
    assert len(obstacles) > 0


def test_forest_and_mountains_generation() -> None:
    random.seed(2)
    tiles = generate_base(30, 30)
    tiles, obstacles = place_forest(
        tiles,
        total_area_pct=10,
        clusters=3,
        cluster_spread=0.8,
        obstacles_set=set(),
    )
    assert any(TILE_CODES["forest"] in row for row in tiles)

    altitude = [[0.0 for _ in range(30)] for _ in range(30)]
    tiles, obstacles = place_mountains(
        tiles,
        total_area_pct=5,
        perlin_scale=0.01,
        peak_density=0.2,
        altitude_map_out=altitude,
        obstacles_set=obstacles,
    )
    assert any(TILE_CODES["mountain"] in row for row in tiles)
    assert len(obstacles) > 0
    assert altitude[0][0] >= 0.0


def test_swamp_and_desert() -> None:
    random.seed(3)
    tiles = generate_base(20, 20)
    tiles, obstacles = place_swamp_desert(
        tiles,
        swamp_pct=5,
        desert_pct=5,
        clumpiness=0.5,
        obstacles_set=set(),
    )
    flat = [t for row in tiles for t in row]
    assert TILE_CODES["swamp"] in flat
    assert TILE_CODES["desert"] in flat
    assert obstacles == set()

