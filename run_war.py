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


def _spawn_armies(world, per_nation: int = 5) -> None:
    nations = [n for n in world.children if isinstance(n, NationNode)]
    capitals = {n: getattr(n, "capital_position", [0, 0]) for n in nations}
    for nation in nations:
        capital = capitals.get(nation, [0, 0])
        enemy_capital = None
        for other, cap in capitals.items():
            if other is not nation:
                enemy_capital = cap
                break
        general = next((c for c in nation.children if isinstance(c, GeneralNode)), None)
        if general is None or enemy_capital is None:
            continue
        # remove existing armies
        for child in list(general.children):
            if isinstance(child, ArmyNode):
                general.remove_child(child)
        for i in range(per_nation):
            px = capital[0] + random.uniform(-5, 5)
            py = capital[1] + random.uniform(-5, 5)
            army = ArmyNode(name=f"{nation.name}_army_{i+1}", goal="advance", size=1)
            army.add_child(TransformNode(position=[px, py]))
            unit = UnitNode(
                name=f"{nation.name}_unit_{i+1}",
                size=100,
                state="idle",
                speed=1.0,
                morale=100,
                target=list(enemy_capital),
            )
            unit.add_child(TransformNode(position=[px, py]))
            army.add_child(unit)
            general.add_child(army)


_spawn_armies(world, per_nation=5)
movement_system = next((c for c in world.children if isinstance(c, MovementSystem)), None)
if movement_system:
    movement_system.direction_noise = 0.2

clock = pygame.time.Clock()
viewer = next((c for c in world.children if isinstance(c, PygameViewerSystem)), None)
# Center the view on the world by default
if viewer:
    viewer.scale = 10
    viewer.unit_radius = 8
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
            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                TIME_SCALE = max(0.1, TIME_SCALE / 2)
            elif event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                TIME_SCALE = min(100, TIME_SCALE * 2)
    if viewer:
        viewer.process_events(events)
    dt = clock.tick(FPS) / 1000.0
    world.update(0 if paused else dt * TIME_SCALE)

pygame.quit()
