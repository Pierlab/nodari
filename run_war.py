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
terrain_density = 0.1


def _generate_terrain(world, density: float = 0.1) -> None:
    terrain = next((c for c in world.children if isinstance(c, TerrainNode)), None)
    if terrain is None:
        return
    width, height = int(world.width), int(world.height)
    terrain.tiles = [["plain" for _ in range(width)] for _ in range(height)]
    terrain.obstacles.clear()
    terrain.speed_modifiers.update({
        "water": 0.4,
        "mountain": 0.6,
        "swamp": 0.5,
        "desert": 0.8,
    })
    terrain.combat_bonuses.update({
        "water": -2,
        "mountain": 3,
        "swamp": -1,
        "desert": 0,
    })
    types = ["forest", "hill", "water", "mountain", "swamp", "desert"]
    for y in range(height):
        for x in range(width):
            if random.random() < density:
                tile = random.choice(types)
                terrain.tiles[y][x] = tile
                if tile == "water":
                    terrain.obstacles.add((x, y))


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
    _generate_terrain(world, terrain_density)
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
                TIME_SCALE = max(0.1, TIME_SCALE / 2)
            elif event.key == pygame.K_x:
                TIME_SCALE = min(100, TIME_SCALE * 2)
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
                    terrain_density = max(0.0, terrain_density - 0.05)
                    _generate_terrain(world, terrain_density)
                elif event.key == pygame.K_g:
                    terrain_density = min(1.0, terrain_density + 0.05)
                    _generate_terrain(world, terrain_density)
                elif event.key == pygame.K_d:
                    distribution_mode = "spread" if distribution_mode == "cluster" else "cluster"
    if viewer:
        if paused:
            viewer.extra_info = [
                f"Troops/nation: {troops_per_nation}",
                f"Speed var: {speed_variation:.2f}",
                f"Stat var: {stat_variation:.2f}",
                f"Terrain dens.: {terrain_density:.2f}",
                f"Distribution: {distribution_mode}",
                "A/Z: -/+ troops", "E/T: -/+ speed", "Y/U: -/+ stats", "F/G: -/+ terrain", "D: toggle dist", "R: reset",
            ]
        else:
            viewer.extra_info = []
        viewer.process_events(events)
    dt = clock.tick(FPS) / 1000.0
    world.update(0 if paused else dt * TIME_SCALE)

pygame.quit()
