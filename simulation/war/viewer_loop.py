"""Viewer loop for the war simulation supporting multiple backends."""

from __future__ import annotations

import os
import pygame

import config
from simulation.war.ui import ModernGLViewerSystem, PygameViewerSystem
from simulation.war.war_loader import (
    load_plugins_for_war,
    reset_world,
    setup_world,
)


def run(viewer: str = "pygame") -> None:
    """Run the interactive viewer for the war simulation."""

    if "DISPLAY" not in os.environ and os.environ.get("SDL_VIDEODRIVER") is None:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()

    load_plugins_for_war()
    world, _, pathfinder = setup_world()

    viewer_cls = PygameViewerSystem
    if viewer == "moderngl":
        viewer_cls = ModernGLViewerSystem
    viewer = viewer_cls(parent=world)
    movement_system = None

    def _reset() -> None:
        nonlocal movement_system
        movement_system = reset_world(world, pathfinder)
        if movement_system:
            movement_system.direction_noise = 0.2
            movement_system.avoid_obstacles = True
            movement_system.pathfinder = pathfinder

    _reset()

    # Center the view on the world by default
    scale_x = viewer.view_width / world.width
    scale_y = viewer.view_height / world.height
    viewer.scale = min(scale_x, scale_y)
    viewer.unit_radius = 10
    viewer.draw_capital = True
    viewer.offset_x = world.width / 2 - viewer.view_width / (2 * viewer.scale)
    viewer.offset_y = world.height / 2 - viewer.view_height / (2 * viewer.scale)

    FPS = config.FPS
    TIME_SCALE = config.TIME_SCALE
    clock = pygame.time.Clock()

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
                elif event.key == pygame.K_c:
                    TIME_SCALE = max(0.01, TIME_SCALE / 2)
                elif event.key == pygame.K_x:
                    TIME_SCALE = min(100, TIME_SCALE * 2)
                elif event.key == pygame.K_LEFTBRACKET:
                    prev = viewer.scale
                    viewer.scale = max(0.1, viewer.scale * 0.9)
                    cx = viewer.offset_x + viewer.view_width / (2 * prev)
                    cy = viewer.offset_y + viewer.view_height / (2 * prev)
                    viewer.offset_x = cx - viewer.view_width / (2 * viewer.scale)
                    viewer.offset_y = cy - viewer.view_height / (2 * viewer.scale)
                elif event.key == pygame.K_RIGHTBRACKET:
                    prev = viewer.scale
                    viewer.scale = viewer.scale * 1.1
                    cx = viewer.offset_x + viewer.view_width / (2 * prev)
                    cy = viewer.offset_y + viewer.view_height / (2 * prev)
                    viewer.offset_x = cx - viewer.view_width / (2 * viewer.scale)
                    viewer.offset_y = cy - viewer.view_height / (2 * viewer.scale)
                elif event.key == pygame.K_q:
                    viewer.offset_x -= viewer.view_width * 0.1 / viewer.scale
                elif event.key == pygame.K_d:
                    viewer.offset_x += viewer.view_width * 0.1 / viewer.scale
                elif event.key == pygame.K_s:
                    viewer.offset_y += viewer.view_height * 0.1 / viewer.scale
                elif event.key == pygame.K_z:
                    viewer.offset_y -= viewer.view_height * 0.1 / viewer.scale
                # no additional controls when paused

        viewer.extra_info = []
        viewer.set_menu_items([])
        viewer.process_events(events)
        dt = clock.tick(FPS) / 1000.0
        world.update(0 if paused else dt * TIME_SCALE)
        viewer.render(dt)

    pygame.quit()
