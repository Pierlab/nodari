"""Pygame-based viewer system to visualise simulation state."""
from __future__ import annotations

import os
import time
import logging
from math import atan2, cos, sin, pi, ceil
from typing import Any, Callable, Iterator, List, Optional, Tuple, Protocol

import pygame

import config

from core.simnode import SimNode, SystemNode
from core.plugins import register_node_type
from nodes.transform import TransformNode
from nodes.unit import UnitNode
from nodes.terrain import TerrainNode
from core.terrain import TILE_CODES, TILE_NAMES
from nodes.nation import NationNode
from nodes.general import GeneralNode
from nodes.strategist import StrategistNode
from nodes.officer import OfficerNode
from nodes.bodyguard import BodyguardUnitNode
from systems.time import TimeSystem

UNIT_RADIUS = 4

TERRAIN_COLORS: dict[int, Tuple[int, int, int]] = {
    TILE_CODES["plain"]: (80, 160, 80),
    TILE_CODES["forest"]: (34, 139, 34),
    TILE_CODES["hill"]: (110, 110, 110),
    TILE_CODES["water"]: (0, 0, 200),
    TILE_CODES["mountain"]: (139, 137, 137),
    TILE_CODES["swamp"]: (47, 79, 47),
    TILE_CODES["desert"]: (210, 180, 140),
    TILE_CODES["road"]: (120, 120, 120),
}
ARROW_COLOR = (255, 255, 0)
# Shorter arrows for unit targets
ARROW_MAX_LEN = 25
CAPITAL_COLOR = (0, 200, 0)
NATION_COLORS = [
    (200, 50, 50),
    (50, 50, 200),
    (50, 200, 50),
    (200, 200, 50),
]

ROLE_RING_COLORS: dict[str, Tuple[int, int, int]] = {
    "general": (255, 215, 0),
    "strategist": (255, 255, 255),
    "officer": (0, 255, 255),
    "bodyguard": (255, 0, 255),
    "soldier": (0, 0, 0),
}


class Viewer(Protocol):
    """Interface commune aux différents moteurs d'affichage."""

    def process_events(self, events: List[Any]) -> None:
        """Traiter les événements spécifiques au backend."""

    def update(self, dt: float) -> None:
        """Mettre à jour l'état interne sans effectuer de rendu."""

    def render(self, dt: float = 0.0) -> None:
        """Dessiner l'état courant à l'écran.

        Le paramètre ``dt`` représente le temps simulé écoulé depuis le
        précédent rendu et est fourni pour assurer la cohérence de
        l'interface entre les différents moteurs d'affichage.
        """


class PygameViewerSystem(SystemNode, Viewer):
    """Render simulation state using a simple Pygame window.

    Parameters
    ----------
    width, height:
        Size of the simulation area in pixels.
    scale:
        Scale applied to positions stored in :class:`TransformNode`s.
    panel_width:
        Width of the information panel appended to the right of the view.
    font_size:
        Font size used to render the panel text.
    max_terrain_resolution:
        Maximum width or height of the cached terrain surface in pixels.
    """

    def __init__(
        self,
        width: int = config.VIEW_WIDTH,
        height: int = config.VIEW_HEIGHT,
        scale: float = 5.0,
        panel_width: int = config.PANEL_WIDTH,
        font_size: int = config.FONT_SIZE,
        draw_capital: bool = False,
        # Cache terrain at a modest resolution to avoid long pre-render times
        max_terrain_resolution: int = 1024,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        # Use dummy driver only when no display is available
        if "DISPLAY" not in os.environ and os.environ.get("SDL_VIDEODRIVER") is None:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        self.view_width = width
        self.view_height = height
        self.panel_width = panel_width
        self.screen = pygame.display.set_mode((width + self.panel_width, height))
        pygame.display.set_caption(self.name)
        self.font = pygame.font.Font(None, font_size)
        self._scale = scale
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.selected: Optional[SimNode] = None
        self.unit_radius = UNIT_RADIUS
        # number of soldiers represented by a single dot – coarser by default for speed
        self.soldiers_per_dot = 10
        self.draw_capital = draw_capital
        # Toggle display options (disabled overlays yield a faster startup)
        self.show_role_rings = False
        self.show_intel_overlay = False
        # Extra informational lines injected by external code (e.g. pause menu)
        self.extra_info: List[str] = []
        # Interactive menu entries displayed in the side panel
        self.menu_items: List[dict] = []
        self._menu_button_rects: List[tuple[pygame.Rect, Callable[[], None]]] = []
        self._terrain_cache: pygame.Surface | None = None
        self._terrain_cache_scale = self.scale
        self._terrain_cache_size: tuple[int, int] | None = None
        self.max_terrain_resolution = max_terrain_resolution
        self._frame_count = 0
        self._log_frame_interval = 60
        self._verbose_frame_logging = False

    @property
    def scale(self) -> float:
        return self._scale

    @scale.setter
    def scale(self, value: float) -> None:
        if value != self._scale:
            self._scale = value
            self._terrain_cache = None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _root(self) -> SystemNode:
        node: SystemNode = self
        while node.parent is not None:
            node = node.parent  # type: ignore[assignment]
        return node

    def _walk(self, node) -> Iterator[SystemNode]:
        yield node
        for child in node.children:
            yield from self._walk(child)

    # ------------------------------------------------------------------
    # Simulation API
    # ------------------------------------------------------------------
    def set_render_params(
        self,
        *,
        soldiers_per_dot: int | None = None,
        show_role_rings: bool | None = None,
        show_intel_overlay: bool | None = None,
    ) -> None:
        """Update runtime rendering parameters."""

        if soldiers_per_dot is not None:
            self.soldiers_per_dot = soldiers_per_dot
        if show_role_rings is not None:
            self.show_role_rings = show_role_rings
        if show_intel_overlay is not None:
            self.show_intel_overlay = show_intel_overlay

    def set_menu_items(self, items: List[dict]) -> None:
        """Replace interactive menu items.

        Each *item* mapping should define ``label``, ``minus`` and ``plus``
        callables which will be invoked when the corresponding button is
        clicked.
        """

        self.menu_items = items

    def process_events(self, events: List[pygame.event.Event]) -> None:
        """Handle external Pygame events."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if event.pos[0] < self.view_width:
                    self.selected = self._node_at_pixel(event.pos)
                    if self.selected:
                        self._center_on(self.selected)
                else:
                    for rect, cb in self._menu_button_rects:
                        if rect.collidepoint(event.pos):
                            cb()
                            break
            elif event.type == pygame.MOUSEWHEEL:
                factor = 1.1 if event.y > 0 else 0.9
                prev_scale = self.scale
                self.scale = max(0.1, self.scale * factor)
                cx = self.offset_x + self.view_width / (2 * prev_scale)
                cy = self.offset_y + self.view_height / (2 * prev_scale)
                self.offset_x = cx - self.view_width / (2 * self.scale)
                self.offset_y = cy - self.view_height / (2 * self.scale)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    self._verbose_frame_logging = not self._verbose_frame_logging

    def _node_at_pixel(self, pos) -> Optional[SimNode]:
        """Return the topmost node at the given pixel position."""
        selected: Optional[SimNode] = None
        for node in self._walk(self._root()):
            for child in node.children:
                if isinstance(child, TransformNode):
                    px, py = child.position
                    parent = child.parent
                    sx = (px - self.offset_x) * self.scale
                    sy = (py - self.offset_y) * self.scale
                    if isinstance(parent, UnitNode):
                        if (sx - pos[0]) ** 2 + (sy - pos[1]) ** 2 <= self.unit_radius ** 2:
                            selected = parent
        return selected

    def _center_on(self, node: SimNode) -> None:
        """Center the camera on ``node`` if it has a transform."""
        for child in node.children:
            if isinstance(child, TransformNode):
                x, y = child.position
                self.offset_x = x - self.view_width / (2 * self.scale)
                self.offset_y = y - self.view_height / (2 * self.scale)
                break

    def _draw_intel_overlay(self) -> None:
        root = self._root()
        for node in self._walk(root):
            for child in node.children:
                if isinstance(child, TransformNode) and isinstance(child.parent, UnitNode):
                    px, py = child.position
                    radius = int(
                        getattr(child.parent, "vision_radius_m", 0.0)
                        / config.WORLD_SCALE_M
                        * self.scale
                    )
                    if radius > 0:
                        sx = int((px - self.offset_x) * self.scale)
                        sy = int((py - self.offset_y) * self.scale)
                        pygame.draw.circle(self.screen, (255, 255, 255), (sx, sy), radius, 1)
            if isinstance(node, StrategistNode):
                for report in node.get_enemy_estimates():
                    x, y = report.get("position", [0, 0])
                    sx = int((x - self.offset_x) * self.scale)
                    sy = int((y - self.offset_y) * self.scale)
                    pygame.draw.line(self.screen, (255, 0, 0), (sx - 4, sy - 4), (sx + 4, sy + 4), 2)
                    pygame.draw.line(self.screen, (255, 0, 0), (sx - 4, sy + 4), (sx + 4, sy - 4), 2)

    def _info_lines(self, node: SimNode) -> List[str]:
        """Return a list of human-readable attributes for ``node``."""
        lines: List[str] = [f"{node.name} ({node.__class__.__name__})"]
        for attr, value in vars(node).items():
            if attr.startswith("_") or attr in {"parent", "children"}:
                continue
            lines.append(f"{attr}:")
            lines.append(f"  {value}")
        for child in node.children:
            lines.append(child.__class__.__name__ + ":")
            for attr, value in vars(child).items():
                if attr.startswith("_") or attr in {"parent", "children"}:
                    continue
                lines.append(f"  {attr}:")
                lines.append(f"    {value}")
        return lines

    # ------------------------------------------------------------------
    def _nation_of(self, node: SimNode) -> Optional[SimNode]:
        cur: Optional[SimNode] = node
        while cur is not None:
            if isinstance(cur, NationNode):
                return cur
            cur = cur.parent
        return None

    def _draw_arrow(
        self, start: Tuple[int, int], end: Tuple[int, int], color: Tuple[int, int, int]
    ) -> None:
        dx, dy = end[0] - start[0], end[1] - start[1]
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist > ARROW_MAX_LEN:
            scale = ARROW_MAX_LEN / dist
            end = (start[0] + dx * scale, start[1] + dy * scale)
            dx, dy = end[0] - start[0], end[1] - start[1]
        pygame.draw.line(self.screen, color, start, end, 2)
        angle = atan2(dy, dx)
        size = 6
        left = (
            end[0] - size * cos(angle - pi / 6),
            end[1] - size * sin(angle - pi / 6),
        )
        right = (
            end[0] - size * cos(angle + pi / 6),
            end[1] - size * sin(angle + pi / 6),
        )
        pygame.draw.polygon(self.screen, color, [end, left, right])

    def _draw_cross(self, center: Tuple[int, int], size: int) -> None:
        """Draw a cross centered on ``center`` with given ``size``."""
        x, y = center
        pygame.draw.line(
            self.screen, (255, 0, 0), (x - size, y - size), (x + size, y + size), 2
        )
        pygame.draw.line(
            self.screen, (255, 0, 0), (x - size, y + size), (x + size, y - size), 2
        )

    def _terrain_surface(self, terrain: TerrainNode) -> pygame.Surface:
        rows = len(terrain.tiles)
        cols = len(terrain.tiles[0])
        if (
            self._terrain_cache is None
            or self._terrain_cache_scale != self.scale
            or self._terrain_cache_size != (rows, cols)
        ):
            # Clamp desired scale to stay within maximum cached resolution
            max_res = self.max_terrain_resolution
            cache_scale = min(self.scale, max_res / rows, max_res / cols)
            if cache_scale != self._scale:
                self._scale = cache_scale

            # Downsample tiles to a manageable surface
            step = max(1, ceil(max(rows, cols) / max_res))
            raw_w = ceil(cols / step)
            raw_h = ceil(rows / step)
            raw_surface = pygame.Surface((raw_w, raw_h))
            for py, y in enumerate(range(0, rows, step)):
                y1 = min(y + step, rows)
                for px, x in enumerate(range(0, cols, step)):
                    x1 = min(x + step, cols)
                    r = g = b = 0
                    count = 0
                    for ty in range(y, y1):
                        row = terrain.tiles[ty]
                        for tx in range(x, x1):
                            cr, cg, cb = TERRAIN_COLORS.get(row[tx], (80, 80, 80))
                            r += cr
                            g += cg
                            b += cb
                            count += 1
                    raw_surface.set_at((px, py), (r // count, g // count, b // count))

            final_width = int(cols * cache_scale)
            final_height = int(rows * cache_scale)
            self._terrain_cache = pygame.transform.scale(
                raw_surface, (final_width, final_height)
            )
            self._terrain_cache_scale = cache_scale
            self._terrain_cache_size = (rows, cols)
        return self._terrain_cache

    def _draw_terrain(self, terrain: TerrainNode) -> None:
        surface = self._terrain_surface(terrain)
        self.screen.blit(
            surface,
            (-int(self.offset_x * self.scale), -int(self.offset_y * self.scale)),
        )

    def update(self, dt: float) -> None:  # noqa: D401 - part of Viewer
        """Mettre à jour l'état interne sans rendu."""
        pass

    def render(self, dt: float = 0.0) -> None:
        """Render the current simulation state.

        Parameters
        ----------
        dt:
            Simulation time elapsed since the previous frame.
        """
        start_time = time.perf_counter()
        self.screen.fill((30, 30, 30))

        root = self._root()
        terrain = next((n for n in self._walk(root) if isinstance(n, TerrainNode)), None)
        if terrain is not None:
            self._draw_terrain(terrain)
        nations = [n for n in self._walk(root) if isinstance(n, NationNode)]
        nation_colors = {n: NATION_COLORS[i % len(NATION_COLORS)] for i, n in enumerate(nations)}
        if nations and self.draw_capital:
            for n in nations:
                cap = getattr(n, "capital_position", None)
                if cap is not None:
                    cx = int((cap[0] - self.offset_x) * self.scale)
                    cy = int((cap[1] - self.offset_y) * self.scale)
                    size = int(self.unit_radius * 3)
                    rect = pygame.Rect(cx - size, cy - size, size * 2, size * 2)
                    pygame.draw.rect(self.screen, CAPITAL_COLOR, rect)

        lines: List[str] = []
        time_sys: Optional[TimeSystem] = None
        unit_count = 0
        for node in self._walk(root):
            if isinstance(node, UnitNode):
                unit_count += 1
            if isinstance(node, TransformNode):
                parent = node.parent
                x, y = node.position
                pos = (
                    int((x - self.offset_x) * self.scale),
                    int((y - self.offset_y) * self.scale),
                )
                if isinstance(parent, UnitNode):
                    col = nation_colors.get(self._nation_of(parent), (200, 200, 200))
                    target = getattr(parent, "target", None)
                    if target is not None and parent.state != "defeated":
                        end = (
                            int((target[0] - self.offset_x) * self.scale),
                            int((target[1] - self.offset_y) * self.scale),
                        )
                        self._draw_arrow(pos, end, ARROW_COLOR)
                    radius = int(
                        self.unit_radius
                        * max(
                            0.5,
                            (
                                parent.size
                                / max(1, self.soldiers_per_dot)
                                / 100
                            )
                            ** 0.5,
                        )
                    )
                    if parent.state == "defeated":
                        self._draw_cross(pos, radius)
                    else:
                        pygame.draw.circle(self.screen, col, pos, radius)
                        if self.show_role_rings:
                            ring = (
                                ROLE_RING_COLORS["bodyguard"]
                                if isinstance(parent, BodyguardUnitNode)
                                else ROLE_RING_COLORS["soldier"]
                            )
                            pygame.draw.circle(self.screen, ring, pos, radius, 2)
                elif isinstance(parent, GeneralNode):
                    col = nation_colors.get(self._nation_of(parent), (200, 200, 200))
                    radius = int(self.unit_radius * 1.3)
                    pygame.draw.circle(self.screen, col, pos, radius)
                    if self.show_role_rings:
                        pygame.draw.circle(
                            self.screen, ROLE_RING_COLORS["general"], pos, radius, 2
                        )
                elif isinstance(parent, StrategistNode):
                    col = nation_colors.get(self._nation_of(parent), (200, 200, 200))
                    radius = int(self.unit_radius)
                    pygame.draw.circle(self.screen, col, pos, radius)
                    if self.show_role_rings:
                        pygame.draw.circle(
                            self.screen, ROLE_RING_COLORS["strategist"], pos, radius, 2
                        )
                elif isinstance(parent, OfficerNode):
                    col = nation_colors.get(self._nation_of(parent), (200, 200, 200))
                    radius = int(self.unit_radius)
                    pygame.draw.circle(self.screen, col, pos, radius)
                    if self.show_role_rings:
                        pygame.draw.circle(
                            self.screen, ROLE_RING_COLORS["officer"], pos, radius, 2
                        )
                else:
                    pygame.draw.circle(self.screen, (200, 200, 200), pos, 3)
            if isinstance(node, TimeSystem):
                time_sys = node

        if self.show_intel_overlay:
            self._draw_intel_overlay()

        # draw a scale bar representing 1 kilometre
        grid_units_for_1km = 1000 / config.WORLD_SCALE_M
        scale_length = int(grid_units_for_1km * self.scale)
        bar_y = self.view_height - 20
        pygame.draw.line(self.screen, (255, 255, 255), (10, bar_y), (10 + scale_length, bar_y), 2)
        label = self.font.render("1 km", True, (255, 255, 255))
        label_rect = label.get_rect()
        label_rect.center = (10 + scale_length / 2, bar_y + label_rect.height / 2 + 2)
        self.screen.blit(label, label_rect)

        # terrain legend next to the scale bar
        line_height = self.font.get_linesize()
        legend_y = bar_y - line_height * len(TERRAIN_COLORS) - 5
        for idx, (code, color) in enumerate(TERRAIN_COLORS.items()):
            y = legend_y + idx * line_height
            pygame.draw.rect(self.screen, color, pygame.Rect(10, y, 12, 12))
            name = self.font.render(TILE_NAMES.get(code, ""), True, (255, 255, 255))
            self.screen.blit(name, (26, y - 2))

        panel_rect = pygame.Rect(self.view_width, 0, self.panel_width, self.view_height)
        pygame.draw.rect(self.screen, (50, 50, 50), panel_rect)

        if self.selected:
            lines.extend(self._info_lines(self.selected))

        if time_sys is not None:
            hours = int(time_sys.current_time // 3600) % 24
            minutes = int((time_sys.current_time % 3600) // 60)
            time_text = f"{hours:02d}:{minutes:02d}"
            day = int(
                time_sys.current_tick * time_sys.tick_duration // time_sys.day_length
            ) + 1
            lines.insert(0, f"Phase: {time_sys.phase}")
            lines.insert(0, f"Tick: {time_sys.current_tick}")
            lines.insert(0, f"Day: {day} {time_text}")
        lines.insert(0, f"Units: {unit_count}")

        line_height = self.font.get_linesize()
        text_y = 10
        for text in lines:
            surf = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(surf, (panel_rect.x + 10, text_y))
            text_y += line_height

        # draw interactive menu items with +/- buttons
        self._menu_button_rects = []
        if self.menu_items:
            text_y += line_height
            for item in self.menu_items:
                surf = self.font.render(item["label"], True, (255, 255, 255))
                self.screen.blit(surf, (panel_rect.x + 10, text_y))
                minus_rect = pygame.Rect(
                    panel_rect.right - 60, text_y - 2, 20, line_height - 4
                )
                plus_rect = pygame.Rect(
                    panel_rect.right - 30, text_y - 2, 20, line_height - 4
                )
                pygame.draw.rect(self.screen, (80, 80, 80), minus_rect)
                pygame.draw.rect(self.screen, (80, 80, 80), plus_rect)
                minus_surf = self.font.render("-", True, (255, 255, 255))
                plus_surf = self.font.render("+", True, (255, 255, 255))
                self.screen.blit(
                    minus_surf,
                    minus_surf.get_rect(center=minus_rect.center),
                )
                self.screen.blit(
                    plus_surf,
                    plus_surf.get_rect(center=plus_rect.center),
                )
                self._menu_button_rects.append((minus_rect, item["minus"]))
                self._menu_button_rects.append((plus_rect, item["plus"]))
                text_y += line_height

        controls = [
            "",
            "Controls:",
            " Space: pause/resume",
            " +/- : change speed",
            " [: zoom out, ]: zoom in",
            " Z/Q/S/D: pan view",
            " V: toggle frame logging",
        ]
        controls.extend(self.extra_info)
        for text in controls:
            surf = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(surf, (panel_rect.x + 10, text_y))
            text_y += line_height

        if self.show_role_rings:
            # Draw legend for role rings
            text_y += line_height
            legend_title = self.font.render("Legend:", True, (255, 255, 255))
            self.screen.blit(legend_title, (panel_rect.x + 10, text_y))
            text_y += line_height
            for label, key in [
                ("General", "general"),
                ("Strategist", "strategist"),
                ("Officer", "officer"),
                ("Bodyguard", "bodyguard"),
                ("Soldier", "soldier"),
            ]:
                pygame.draw.circle(
                    self.screen,
                    ROLE_RING_COLORS[key],
                    (panel_rect.x + 15, text_y + line_height // 2),
                    5,
                    2,
                )
                surf = self.font.render(label, True, (255, 255, 255))
                self.screen.blit(surf, (panel_rect.x + 25, text_y))
                text_y += line_height

        pygame.display.flip()
        end_time = time.perf_counter()
        if self._verbose_frame_logging:
            self._frame_count += 1
            if self._frame_count % self._log_frame_interval == 0:
                logging.debug(
                    "PygameViewerSystem frame %d took %.3f ms",
                    self._frame_count,
                    (end_time - start_time) * 1000,
                )
        super().update(dt)


register_node_type("PygameViewerSystem", PygameViewerSystem)
