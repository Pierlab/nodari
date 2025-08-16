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

# global capital shared by all nations
nations = [n for n in world.children if isinstance(n, NationNode)]
GLOBAL_CAPITAL = [world.width / 2, world.height / 2]
for n in nations:
    n.capital_position = GLOBAL_CAPITAL

# parameters adjustable via pause menu
troops_per_nation = 5
speed_variation = 0.2
stat_variation = 0.2
distribution_mode = "cluster"


def _generate_obstacles(world, count: int = 20) -> None:
    terrain = next((c for c in world.children if isinstance(c, TerrainNode)), None)
    if terrain is None:
        return
    terrain.obstacles.clear()
    for _ in range(count):
        w = random.randint(1, 4)
        h = random.randint(1, 4)
        x = random.randint(0, int(world.width - w))
        y = random.randint(0, int(world.height - h))
        for ix in range(x, x + w):
            for iy in range(y, y + h):
                terrain.obstacles.add((ix, iy))


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
            unit = UnitNode(
                name=f"{nation.name}_unit_{i+1}",
                size=size,
                state="idle",
                speed=speed,
                morale=100,
                target=list(GLOBAL_CAPITAL),
            )
            unit.add_child(TransformNode(position=[px, py]))
            army.add_child(unit)
            general.add_child(army)


def _reset() -> None:
    _generate_obstacles(world)
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
            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                TIME_SCALE = max(0.1, TIME_SCALE / 2)
            elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                TIME_SCALE = min(100, TIME_SCALE * 2)
            elif paused:
                if event.key == pygame.K_1:
                    troops_per_nation = max(1, troops_per_nation - 1)
                elif event.key == pygame.K_2:
                    troops_per_nation += 1
                elif event.key == pygame.K_3:
                    speed_variation = max(0.0, speed_variation - 0.1)
                elif event.key == pygame.K_4:
                    speed_variation += 0.1
                elif event.key == pygame.K_5:
                    stat_variation = max(0.0, stat_variation - 0.1)
                elif event.key == pygame.K_6:
                    stat_variation += 0.1
                elif event.key == pygame.K_d:
                    distribution_mode = "spread" if distribution_mode == "cluster" else "cluster"
    if viewer:
        if paused:
            viewer.extra_info = [
                f"Troops/nation: {troops_per_nation}",
                f"Speed var: {speed_variation:.2f}",
                f"Stat var: {stat_variation:.2f}",
                f"Distribution: {distribution_mode}",
                "1/2: -/+ troops", "3/4: -/+ speed", "5/6: -/+ stats", "D: toggle dist", "R: reset",
            ]
        else:
            viewer.extra_info = []
        viewer.process_events(events)
    dt = clock.tick(FPS) / 1000.0
    world.update(0 if paused else dt * TIME_SCALE)

pygame.quit()
