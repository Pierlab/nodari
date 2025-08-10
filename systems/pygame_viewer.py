"""Pygame-based viewer system to visualise simulation state."""
from __future__ import annotations

import os
from typing import Iterator, List, Optional, Tuple, Type

import pygame

import config

from core.simnode import SimNode, SystemNode
from core.plugins import register_node_type
from nodes.transform import TransformNode
from nodes.character import CharacterNode
from nodes.farm import FarmNode
from nodes.house import HouseNode
from nodes.well import WellNode
from nodes.warehouse import WarehouseNode
from nodes.barn import BarnNode
from nodes.silo import SiloNode
from nodes.pasture import PastureNode
from systems.time import TimeSystem

DEFAULT_BUILDING_SIZES: dict[Type[SimNode], Tuple[int, int]] = {
    FarmNode: (60, 40),
    HouseNode: (40, 40),
    WarehouseNode: (50, 30),
    BarnNode: (60, 30),
    SiloNode: (20, 40),
    PastureNode: (80, 80),
}
BUILDING_COLORS: dict[Type[SimNode], Tuple[int, int, int]] = {
    FarmNode: (150, 100, 50),
    HouseNode: (50, 100, 200),
    WarehouseNode: (150, 150, 150),
    BarnNode: (139, 69, 19),
    SiloNode: (200, 200, 50),
    PastureNode: (34, 139, 34),
}
WELL_RADIUS = 10
CHAR_RADIUS = 5


class PygameViewerSystem(SystemNode):
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
    """

    def __init__(
        self,
        width: int = config.VIEW_WIDTH,
        height: int = config.VIEW_HEIGHT,
        scale: float = 5.0,
        panel_width: int = config.PANEL_WIDTH,
        font_size: int = config.FONT_SIZE,
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
        self.scale = scale
        self.selected: Optional[SimNode] = None

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
    def process_events(self, events: List[pygame.event.Event]) -> None:
        """Handle external Pygame events."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.pos[0] < self.view_width:
                self.selected = self._node_at_pixel(event.pos)

    def _node_at_pixel(self, pos) -> Optional[SimNode]:
        """Return the topmost node at the given pixel position."""
        selected: Optional[SimNode] = None
        for node in self._walk(self._root()):
            for child in node.children:
                if isinstance(child, TransformNode):
                    px, py = child.position
                    parent = child.parent
                    sx, sy = px * self.scale, py * self.scale
                    if isinstance(parent, CharacterNode):
                        if (sx - pos[0]) ** 2 + (sy - pos[1]) ** 2 <= CHAR_RADIUS ** 2:
                            selected = parent
                    elif isinstance(parent, WellNode):
                        if (sx - pos[0]) ** 2 + (sy - pos[1]) ** 2 <= WELL_RADIUS ** 2:
                            selected = parent
                    else:
                        rect = self._building_rect(parent)
                        if rect is not None:
                            rect.center = (int(sx), int(sy))
                            if rect.collidepoint(pos):
                                selected = parent
        return selected

    def _building_rect(self, node: SimNode) -> Optional[pygame.Rect]:
        if isinstance(node, (FarmNode, HouseNode, WarehouseNode, BarnNode, SiloNode, PastureNode)):
            w = getattr(node, "width", None)
            h = getattr(node, "height", None)
            if w is None or h is None:
                w, h = DEFAULT_BUILDING_SIZES.get(type(node), (0, 0))
            return pygame.Rect(0, 0, int(w), int(h))
        return None

    def _info_lines(self, node: SimNode) -> List[str]:
        """Return a list of human-readable attributes for ``node``."""
        lines: List[str] = [node.name]
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

    def update(self, dt: float) -> None:  # noqa: D401 - inherit docstring
        """Update the window and render state."""
        self.screen.fill((30, 30, 30))

        lines: List[str] = []
        time_sys: Optional[TimeSystem] = None
        character_count = 0
        for node in self._walk(self._root()):
            if isinstance(node, CharacterNode):
                character_count += 1
            if isinstance(node, TransformNode):
                parent = node.parent
                x, y = node.position
                pos = (int(x * self.scale), int(y * self.scale))
                if isinstance(parent, CharacterNode):
                    color = (50, 150, 255) if getattr(parent, "gender", "male") == "male" else (255, 105, 180)
                    pygame.draw.circle(self.screen, color, pos, CHAR_RADIUS)
                elif isinstance(parent, WellNode):
                    pygame.draw.circle(self.screen, (0, 100, 200), pos, WELL_RADIUS)
                    name = self.font.render(parent.name, True, (255, 255, 255))
                    name_rect = name.get_rect()
                    name_rect.center = (pos[0], pos[1] + WELL_RADIUS + name_rect.height // 2 + 2)
                    self.screen.blit(name, name_rect)
                else:
                    rect = self._building_rect(parent)
                    if rect is not None:
                        rect.center = pos
                        color = BUILDING_COLORS.get(type(parent), (200, 200, 200))
                        pygame.draw.rect(self.screen, color, rect)
                        name = self.font.render(parent.name, True, (255, 255, 255))
                        name_rect = name.get_rect()
                        name_rect.center = (pos[0], pos[1] + rect.height // 2 + name_rect.height // 2 + 2)
                        self.screen.blit(name, name_rect)
                    else:
                        pygame.draw.circle(self.screen, (200, 200, 200), pos, 3)
            if isinstance(node, TimeSystem):
                time_sys = node

        # draw a scale bar representing 100 meters
        scale_length = int(100 * self.scale)
        bar_y = self.view_height - 20
        pygame.draw.line(self.screen, (255, 255, 255), (10, bar_y), (10 + scale_length, bar_y), 2)
        label = self.font.render("100 m", True, (255, 255, 255))
        label_rect = label.get_rect()
        label_rect.center = (10 + scale_length / 2, bar_y + label_rect.height / 2 + 2)
        self.screen.blit(label, label_rect)

        panel_rect = pygame.Rect(self.view_width, 0, self.panel_width, self.view_height)
        pygame.draw.rect(self.screen, (50, 50, 50), panel_rect)

        if self.selected:
            lines.extend(self._info_lines(self.selected))

        if time_sys is not None:
            hours = int(time_sys.current_time // 3600) % 24
            minutes = int((time_sys.current_time % 3600) // 60)
            time_text = f"{hours:02d}:{minutes:02d}"
            lines.insert(0, f"Phase: {time_sys.phase}")
            lines.insert(0, f"Tick: {time_sys.current_tick}")
            lines.insert(0, time_text)
        lines.insert(0, f"Characters: {character_count}")

        line_height = self.font.get_linesize()
        for i, text in enumerate(lines):
            surf = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(surf, (panel_rect.x + 10, 10 + i * line_height))

        pygame.display.flip()
        super().update(dt)


register_node_type("PygameViewerSystem", PygameViewerSystem)
