"""Pygame-based viewer system to visualise simulation state."""
from __future__ import annotations

import os
from typing import Iterator, List, Optional

import pygame

import config

from core.simnode import SimNode, SystemNode
from core.plugins import register_node_type
from nodes.inventory import InventoryNode
from nodes.need import NeedNode
from nodes.transform import TransformNode
from nodes.character import CharacterNode
from nodes.farm import FarmNode
from nodes.house import HouseNode
from nodes.well import WellNode
from nodes.warehouse import WarehouseNode
from systems.time import TimeSystem

BUILDING_SIZES = {
    FarmNode: (60, 40),
    HouseNode: (40, 40),
    WarehouseNode: (50, 30),
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
        x = pos[0] / self.scale
        y = pos[1] / self.scale
        for node in self._walk(self._root()):
            for child in node.children:
                if isinstance(child, TransformNode):
                    px, py = child.position
                    parent = child.parent
                    sx, sy = px * self.scale, py * self.scale
                    if isinstance(parent, CharacterNode):
                        if (sx - pos[0]) ** 2 + (sy - pos[1]) ** 2 <= CHAR_RADIUS ** 2:
                            return parent
                    elif isinstance(parent, FarmNode):
                        w, h = BUILDING_SIZES[FarmNode]
                        rect = pygame.Rect(0, 0, w, h)
                        rect.center = (int(sx), int(sy))
                        if rect.collidepoint(pos):
                            return parent
                    elif isinstance(parent, HouseNode):
                        w, h = BUILDING_SIZES[HouseNode]
                        rect = pygame.Rect(0, 0, w, h)
                        rect.center = (int(sx), int(sy))
                        if rect.collidepoint(pos):
                            return parent
                    elif isinstance(parent, WellNode):
                        if (sx - pos[0]) ** 2 + (sy - pos[1]) ** 2 <= WELL_RADIUS ** 2:
                            return parent
                    elif isinstance(parent, WarehouseNode):
                        w, h = BUILDING_SIZES[WarehouseNode]
                        rect = pygame.Rect(0, 0, w, h)
                        rect.center = (int(sx), int(sy))
                        if rect.collidepoint(pos):
                            return parent
        return None

    def _info_lines(self, node: SimNode) -> List[str]:
        lines: List[str] = [node.name]
        for child in node.children:
            if isinstance(child, InventoryNode):
                lines.append(f"Inventory: {child.items}")
            if isinstance(child, NeedNode):
                lines.append(f"{child.need_name}: {child.value:.1f}/{child.threshold}")
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
                elif isinstance(parent, FarmNode):
                    w, h = BUILDING_SIZES[FarmNode]
                    rect = pygame.Rect(0, 0, w, h)
                    rect.center = pos
                    pygame.draw.rect(self.screen, (150, 100, 50), rect)
                elif isinstance(parent, HouseNode):
                    w, h = BUILDING_SIZES[HouseNode]
                    rect = pygame.Rect(0, 0, w, h)
                    rect.center = pos
                    pygame.draw.rect(self.screen, (50, 100, 200), rect)
                elif isinstance(parent, WellNode):
                    pygame.draw.circle(self.screen, (0, 100, 200), pos, WELL_RADIUS)
                elif isinstance(parent, WarehouseNode):
                    w, h = BUILDING_SIZES[WarehouseNode]
                    rect = pygame.Rect(0, 0, w, h)
                    rect.center = pos
                    pygame.draw.rect(self.screen, (150, 150, 150), rect)
                else:
                    pygame.draw.circle(self.screen, (200, 200, 200), pos, 3)
            if isinstance(node, TimeSystem):
                time_sys = node

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
