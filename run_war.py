"""Run the war simulation with a visual Pygame window."""

from __future__ import annotations

import os
import sys
import random

import pygame

import config

from core.loader import load_simulation_from_file
from core.plugins import load_plugins
from nodes.army import ArmyNode
from nodes.general import GeneralNode
from nodes.nation import NationNode
from nodes.transform import TransformNode
from nodes.unit import UnitNode
from nodes.terrain import TerrainNode
from tools.terrain_generators import (
    carve_river,
    generate_base,
    place_forest,
    place_lake,
    place_mountains,
    place_swamp_desert,
)
from systems.movement import MovementSystem
from systems.logger import LoggingSystem
from systems.pygame_viewer import PygameViewerSystem
from systems.time import TimeSystem


# Ensure pygame can be used even when no display is available
if "DISPLAY" not in os.environ and os.environ.get("SDL_VIDEODRIVER") is None:
    os.environ["SDL_VIDEODRIVER"] = "dummy"

try:
    pygame.init()
except pygame.error as exc:  # pragma: no cover - environment-specific
    print(f"Unable to initialize pygame: {exc}")
    sys.exit(1)


# Load all plugins required for the war simulation
load_plugins(
    [
        "nodes.world",
        "nodes.nation",
        "nodes.general",
        "nodes.army",
        "nodes.unit",
        "nodes.terrain",
        "nodes.transform",
        "systems.time",
        "systems.movement",
        "systems.combat",
        "systems.moral",
        "systems.victory",
        "systems.logger",
        "systems.pygame_viewer",
    ]
)


# Load the simulation from a JSON/YAML file
config_file = sys.argv[1] if len(sys.argv) > 1 else "example/war_simulation_config.json"
world = load_simulation_from_file(config_file)

terrain_node = next((c for c in world.children if isinstance(c, TerrainNode)), None)
if terrain_node is not None:
    terrain_params = dict(getattr(terrain_node, "params", {}))
else:
    terrain_params = {}

terrain_params.setdefault("forests", {"total_area_pct": 10, "clusters": 5, "cluster_spread": 0.5})
terrain_params.setdefault("rivers", [])
terrain_params.setdefault("lakes", [])
terrain_params.setdefault("mountains", {"total_area_pct": 5, "perlin_scale": 0.01, "peak_density": 0.2})
terrain_params.setdefault("swamp_desert", {"swamp_pct": 3, "desert_pct": 5, "clumpiness": 0.5})


# Ensure logging and visualization systems are present
if not any(isinstance(c, LoggingSystem) for c in world.children):
    LoggingSystem(parent=world)

if not any(isinstance(c, PygameViewerSystem) for c in world.children):
    PygameViewerSystem(parent=world)

time_system = next((c for c in world.children if isinstance(c, TimeSystem)), None)
if time_system is not None:
    time_system.current_time = config.START_TIME


FPS = config.FPS
TIME_SCALE = config.TIME_SCALE

# parameters adjustable via pause menu
troops_per_nation = 5
speed_variation = 0.2
stat_variation = 0.2
distribution_mode = "cluster"
terrain_params = {}


def _generate_terrain(world, params: dict) -> None:
    """Regenerate terrain tiles according to *params*."""

    terrain = next((c for c in world.children if isinstance(c, TerrainNode)), None)
    if terrain is None:
        return

    width, height = int(world.width), int(world.height)
    tiles = generate_base(width, height, fill="plain")
    obstacles: set[tuple[int, int]] = set()
    altitude_map = [[0.0 for _ in range(width)] for _ in range(height)]

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

    for lake in params.get("lakes", []):
        tiles, obstacles = place_lake(
            tiles,
            center=lake.get("center", (width // 2, height // 2)),
            radius=lake.get("radius", 20),
            irregularity=lake.get("irregularity", 0.4),
            obstacles_set=obstacles,
        )

    forests = params.get("forests", {})
    tiles, obstacles = place_forest(
        tiles,
        total_area_pct=forests.get("total_area_pct", 10),
        clusters=forests.get("clusters", 5),
        cluster_spread=forests.get("cluster_spread", 0.5),
        obstacles_set=obstacles,
    )

    mountains = params.get("mountains", {})
    tiles, obstacles = place_mountains(
        tiles,
        total_area_pct=mountains.get("total_area_pct", 5),
        perlin_scale=mountains.get("perlin_scale", 0.01),
        peak_density=mountains.get("peak_density", 0.2),
        altitude_map_out=altitude_map,
        obstacles_set=obstacles,
        obstacle_threshold=params.get("obstacle_altitude_threshold", 0.75),
    )

    swamp_desert = params.get("swamp_desert", {})
    tiles, obstacles = place_swamp_desert(
        tiles,
        swamp_pct=swamp_desert.get("swamp_pct", 3),
        desert_pct=swamp_desert.get("desert_pct", 5),
        clumpiness=swamp_desert.get("clumpiness", 0.5),
        obstacles_set=obstacles,
    )

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


def _spawn_armies(
    world,
    per_nation: int,
    distribution: str,
    speed_var: float,
    stat_var: float,
) -> None:
    nations = [n for n in world.children if isinstance(n, NationNode)]
    width, height = world.width, world.height
    for idx, nation in enumerate(nations):
        general = next((c for c in nation.children if isinstance(c, GeneralNode)), None)
        if general is None:
            continue
        for child in list(general.children):
            if isinstance(child, ArmyNode):
                general.remove_child(child)
        start_x = 10 if idx % 2 == 0 else width - 10
        for i in range(per_nation):
            if distribution == "spread":
                px = random.uniform(0, width)
                py = random.uniform(0, height)
            else:
                px = start_x + random.uniform(-5, 5)
                py = height / 2 + random.uniform(-5, 5)
            army = ArmyNode(name=f"{nation.name}_army_{i+1}", goal="advance", size=1)
            army.add_child(TransformNode(position=[px, py]))
            size = int(100 * random.uniform(1 - stat_var, 1 + stat_var))
            speed = 1.0 * random.uniform(1 - speed_var, 1 + speed_var)
            enemies = [n for n in nations if n is not nation]
            target_cap = enemies[0].capital_position if enemies else [width / 2, height / 2]
            unit = UnitNode(
                name=f"{nation.name}_unit_{i+1}",
                size=size,
                state="idle",
                speed=speed,
                morale=100,
                target=list(target_cap),
            )
            unit.add_child(TransformNode(position=[px, py]))
            army.add_child(unit)
            general.add_child(army)


def _reset() -> None:
    _generate_terrain(world, terrain_params)
    _spawn_armies(world, troops_per_nation, distribution_mode, speed_variation, stat_variation)
    if time_system is not None:
        time_system.current_time = config.START_TIME


_reset()
movement_system = next((c for c in world.children if isinstance(c, MovementSystem)), None)
if movement_system:
    movement_system.direction_noise = 0.2
    movement_system.avoid_obstacles = True

clock = pygame.time.Clock()
viewer = next((c for c in world.children if isinstance(c, PygameViewerSystem)), None)
# Center the view on the world by default
if viewer:
    viewer.scale = 10
    viewer.unit_radius = 10
    viewer.draw_capital = True
    viewer.offset_x = world.width / 2 - viewer.view_width / (2 * viewer.scale)
    viewer.offset_y = world.height / 2 - viewer.view_height / (2 * viewer.scale)
paused = False
running = True
while running and pygame.get_init():
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused
            elif event.key == pygame.K_r:
                _reset()
            elif event.key == pygame.K_s:
                TIME_SCALE = max(0.01, TIME_SCALE / 2)
            elif event.key == pygame.K_x:
                TIME_SCALE = min(100, TIME_SCALE * 2)
            elif viewer and event.key == pygame.K_LEFTBRACKET:
                prev = viewer.scale
                viewer.scale = max(0.1, viewer.scale * 0.9)
                cx = viewer.offset_x + viewer.view_width / (2 * prev)
                cy = viewer.offset_y + viewer.view_height / (2 * prev)
                viewer.offset_x = cx - viewer.view_width / (2 * viewer.scale)
                viewer.offset_y = cy - viewer.view_height / (2 * viewer.scale)
            elif viewer and event.key == pygame.K_RIGHTBRACKET:
                prev = viewer.scale
                viewer.scale = viewer.scale * 1.1
                cx = viewer.offset_x + viewer.view_width / (2 * prev)
                cy = viewer.offset_y + viewer.view_height / (2 * prev)
                viewer.offset_x = cx - viewer.view_width / (2 * viewer.scale)
                viewer.offset_y = cy - viewer.view_height / (2 * viewer.scale)
            elif viewer and event.key == pygame.K_h:
                viewer.offset_x -= viewer.view_width * 0.1 / viewer.scale
            elif viewer and event.key == pygame.K_l:
                viewer.offset_x += viewer.view_width * 0.1 / viewer.scale
            elif viewer and event.key == pygame.K_j:
                viewer.offset_y += viewer.view_height * 0.1 / viewer.scale
            elif viewer and event.key == pygame.K_k:
                viewer.offset_y -= viewer.view_height * 0.1 / viewer.scale
            elif paused:
                if event.key == pygame.K_a:
                    troops_per_nation = max(1, troops_per_nation - 1)
                elif event.key == pygame.K_z:
                    troops_per_nation += 1
                elif event.key == pygame.K_e:
                    speed_variation = max(0.0, speed_variation - 0.1)
                elif event.key == pygame.K_t:
                    speed_variation += 0.1
                elif event.key == pygame.K_y:
                    stat_variation = max(0.0, stat_variation - 0.1)
                elif event.key == pygame.K_u:
                    stat_variation += 0.1
                elif event.key == pygame.K_f:
                    forests = terrain_params.setdefault(
                        "forests", {"total_area_pct": 10, "clusters": 5, "cluster_spread": 0.5}
                    )
                    forests["total_area_pct"] = max(0.0, forests.get("total_area_pct", 0) - 1)
                    _generate_terrain(world, terrain_params)
                elif event.key == pygame.K_g:
                    forests = terrain_params.setdefault(
                        "forests", {"total_area_pct": 10, "clusters": 5, "cluster_spread": 0.5}
                    )
                    forests["total_area_pct"] = min(100.0, forests.get("total_area_pct", 0) + 1)
                    _generate_terrain(world, terrain_params)
                elif event.key == pygame.K_d:
                    distribution_mode = "spread" if distribution_mode == "cluster" else "cluster"
    if viewer:
        if paused:
            viewer.extra_info = [
                f"Troops/nation: {troops_per_nation}",
                f"Speed var: {speed_variation:.2f}",
                f"Stat var: {stat_variation:.2f}",
                f"Forest %: {terrain_params.get('forests', {}).get('total_area_pct', 0):.0f}",
                f"Distribution: {distribution_mode}",
                "A/Z: -/+ troops", "E/T: -/+ speed", "Y/U: -/+ stats", "F/G: -/+ forest", "D: toggle dist", "R: reset",
            ]
        else:
            viewer.extra_info = []
        viewer.process_events(events)
    dt = clock.tick(FPS) / 1000.0
    world.update(0 if paused else dt * TIME_SCALE)

pygame.quit()
