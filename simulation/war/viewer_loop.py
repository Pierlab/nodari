"""Viewer loop for the war simulation supporting multiple backends."""

from __future__ import annotations

import os
import pygame

import config
from simulation.war.presets import FOREST_LAYOUTS, MOUNTAIN_PRESETS, RIVER_WIDTH_PRESETS
from simulation.war.terrain_setup import terrain_regen
from simulation.war.ui import ModernGLViewerSystem, PygameViewerSystem
from simulation.war.war_loader import (
    load_plugins_for_war,
    reset_world,
    setup_world,
    sim_params,
)


def run(viewer: str = "pygame") -> None:
    """Run the interactive viewer for the war simulation."""

    if "DISPLAY" not in os.environ and os.environ.get("SDL_VIDEODRIVER") is None:
        os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()

    load_plugins_for_war()
    world, terrain_node, pathfinder = setup_world()

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
        viewer.set_render_params(soldiers_per_dot=sim_params["soldiers_per_dot"])

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

    river_width_index = 0
    mountain_preset_index = 0
    forest_layout_index = 0

    def _forest_minus() -> None:
        forests = sim_params["terrain"].setdefault(
            "forests", {"total_area_pct": 10, "clusters": 5, "cluster_spread": 0.5}
        )
        forests["total_area_pct"] = max(0.0, forests.get("total_area_pct", 0) - 1)
        terrain_regen(world, sim_params["terrain"])

    def _forest_plus() -> None:
        forests = sim_params["terrain"].setdefault(
            "forests", {"total_area_pct": 10, "clusters": 5, "cluster_spread": 0.5}
        )
        forests["total_area_pct"] = min(100.0, forests.get("total_area_pct", 0) + 1)
        terrain_regen(world, sim_params["terrain"])

    def _dispersion_minus() -> None:
        sim_params["dispersion"] = max(0.0, sim_params["dispersion"] - 10.0)
        _reset()

    def _dispersion_plus() -> None:
        sim_params["dispersion"] += 10.0
        _reset()

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
                elif event.key == pygame.K_b:
                    viewer.set_render_params(show_role_rings=not viewer.show_role_rings)
                elif event.key == pygame.K_SEMICOLON:
                    viewer.set_render_params(show_intel_overlay=not viewer.show_intel_overlay)
                elif paused:
                    if event.key == pygame.K_f:
                        _forest_minus()
                    elif event.key == pygame.K_g:
                        _forest_plus()
                    elif event.key == pygame.K_w and sim_params["terrain"].get("rivers"):
                        river_width_index = (river_width_index + 1) % len(RIVER_WIDTH_PRESETS)
                        wmin, wmax = RIVER_WIDTH_PRESETS[river_width_index]
                        for river in sim_params["terrain"].get("rivers", []):
                            river["width_min"], river["width_max"] = wmin, wmax
                        terrain_regen(world, sim_params["terrain"])
                    elif event.key == pygame.K_m:
                        mountain_preset_index = (mountain_preset_index + 1) % len(MOUNTAIN_PRESETS)
                        preset = MOUNTAIN_PRESETS[mountain_preset_index]
                        mountains = sim_params["terrain"].setdefault("mountains", {})
                        mountains["total_area_pct"] = preset["total_area_pct"]
                        sim_params["terrain"]["obstacle_altitude_threshold"] = preset["threshold"]
                        terrain_regen(world, sim_params["terrain"])
                    elif event.key == pygame.K_v:
                        forest_layout_index = (forest_layout_index + 1) % len(FOREST_LAYOUTS)
                        sim_params["terrain"]["forests"] = dict(FOREST_LAYOUTS[forest_layout_index])
                        terrain_regen(world, sim_params["terrain"])
                    elif event.key == pygame.K_d:
                        sim_params["dispersion"] = 0.0 if sim_params["dispersion"] > 0 else 200.0
                        _reset()
                    elif event.key == pygame.K_p:
                        _dispersion_minus()
                    elif event.key == pygame.K_o:
                        _dispersion_plus()

        if paused:
            forest_pct = sim_params["terrain"].get("forests", {}).get("total_area_pct", 0)
            menu_items = [
                {
                    "label": f"Dispersion R: {sim_params['dispersion']:.0f} m",
                    "minus": _dispersion_minus,
                    "plus": _dispersion_plus,
                },
                {
                    "label": f"Forest %: {forest_pct:.0f}",
                    "minus": _forest_minus,
                    "plus": _forest_plus,
                },
            ]
            viewer.set_menu_items(menu_items)
            info = [
                f"Soldiers/dot: {sim_params['soldiers_per_dot']}",
                f"Intel overlay: {'ON' if viewer.show_intel_overlay else 'OFF'}",
                "F/G or buttons: -/+ forest, W: river width, M: mountains, V: forest layout",
                "P/O or buttons: -/+ dispersion, D: cluster toggle, C: cycle dot scale",
                "B: rings, ;: intel, R: reset",
            ]
            viewer.extra_info = info
        else:
            viewer.set_menu_items([])
            viewer.extra_info = []
        viewer.process_events(events)
        dt = clock.tick(FPS) / 1000.0
        world.update(0 if paused else dt * TIME_SCALE)
        viewer.render(dt)

    pygame.quit()
