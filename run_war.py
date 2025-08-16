"""Run the war simulation with a visual Pygame window."""

from __future__ import annotations

import os
import sys

import pygame

import config

from core.loader import load_simulation_from_file
from core.plugins import load_plugins
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

clock = pygame.time.Clock()
viewer = next((c for c in world.children if isinstance(c, PygameViewerSystem)), None)
# Center the view on the world by default
if viewer:
    viewer.offset_x = world.width / 2 - viewer.view_width / (2 * viewer.scale)
    viewer.offset_y = world.height / 2 - viewer.view_height / (2 * viewer.scale)
paused = False
running = True
while running and pygame.get_init():
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            paused = not paused
    if viewer:
        viewer.process_events(events)
    dt = clock.tick(FPS) / 1000.0
    world.update(0 if paused else dt * TIME_SCALE)

pygame.quit()
