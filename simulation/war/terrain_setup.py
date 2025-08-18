"""Terrain generation helpers for the war simulation."""
from __future__ import annotations

import logging
import time

from simulation.war.nodes import TerrainNode
from simulation.war.terrain import (
    carve_river,
    generate_base,
    place_forest,
    place_lake,
    place_mountains,
    place_swamp_desert,
)

logger = logging.getLogger(__name__)


def terrain_regen(world, params: dict) -> None:
    """Regenerate terrain tiles according to *params*."""

    terrain = next((c for c in world.children if isinstance(c, TerrainNode)), None)
    if terrain is None:
        return

    width, height = int(world.width), int(world.height)
    start_time = time.perf_counter()

    tiles = generate_base(width, height, fill="plain")
    logger.info("Base terrain generated in %.2fs", time.perf_counter() - start_time)

    obstacles: set[tuple[int, int]] = set()
    altitude_map: list[list[float]] | None = None

    step_start = time.perf_counter()
    for river in params.get("rivers", []):
        tiles, obstacles = carve_river(
            tiles,
            start=river.get("start", (0, 0)),
            end=river.get("end", (width - 1, height - 1)),
            width_min=river.get("width_min", 2),
            width_max=river.get("width_max", 5),
            meander=river.get("meander", 0.3),
            obstacles_set=obstacles,
        )
    logger.info("Rivers carved in %.2fs", time.perf_counter() - step_start)

    step_start = time.perf_counter()
    for lake in params.get("lakes", []):
        tiles, obstacles = place_lake(
            tiles,
            center=lake.get("center", (width // 2, height // 2)),
            radius=lake.get("radius", 20),
            irregularity=lake.get("irregularity", 0.4),
            obstacles_set=obstacles,
        )
    logger.info("Lakes placed in %.2fs", time.perf_counter() - step_start)

    forests = params.get("forests", {})
    step_start = time.perf_counter()
    tiles, obstacles = place_forest(
        tiles,
        total_area_pct=forests.get("total_area_pct", 10),
        clusters=forests.get("clusters", 5),
        cluster_spread=forests.get("cluster_spread", 0.5),
        obstacles_set=obstacles,
    )
    logger.info("Forests placed in %.2fs", time.perf_counter() - step_start)

    mountains = params.get("mountains", {})
    step_start = time.perf_counter()
    tiles, obstacles = place_mountains(
        tiles,
        total_area_pct=mountains.get("total_area_pct", 5),
        perlin_scale=mountains.get("perlin_scale", 0.01),
        peak_density=mountains.get("peak_density", 0.2),
        altitude_map_out=None,
        obstacles_set=obstacles,
        obstacle_threshold=params.get("obstacle_altitude_threshold", 0.75),
    )
    logger.info("Mountains generated in %.2fs", time.perf_counter() - step_start)

    swamp_desert = params.get("swamp_desert", {})
    step_start = time.perf_counter()
    tiles, obstacles = place_swamp_desert(
        tiles,
        swamp_pct=swamp_desert.get("swamp_pct", 3),
        desert_pct=swamp_desert.get("desert_pct", 5),
        clumpiness=swamp_desert.get("clumpiness", 0.5),
        obstacles_set=obstacles,
    )
    logger.info("Swamps and deserts placed in %.2fs", time.perf_counter() - step_start)
    logger.info("Terrain regeneration finished in %.2fs", time.perf_counter() - start_time)

    terrain.tiles = tiles
    terrain.obstacles = obstacles
    terrain.altitude_map = altitude_map
    terrain.speed_modifiers.update(
        {
            "water": 0.4,
            "mountain": 0.6,
            "swamp": 0.5,
            "desert": 0.8,
        }
    )
    terrain.combat_bonuses.update(
        {
            "water": -2,
            "mountain": 3,
            "swamp": -1,
            "desert": 0,
        }
    )
