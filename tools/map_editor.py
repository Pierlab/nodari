import json
import os
from dataclasses import dataclass
from typing import List, Tuple

import pygame

import config

# Use dummy driver if headless
if "DISPLAY" not in os.environ and os.environ.get("SDL_VIDEODRIVER") is None:
    os.environ["SDL_VIDEODRIVER"] = "dummy"

pygame.init()

SCALE = 5
WORLD_WIDTH = 240
WORLD_HEIGHT = 144
VIEW_WIDTH = WORLD_WIDTH * SCALE
VIEW_HEIGHT = WORLD_HEIGHT * SCALE
PANEL_WIDTH = config.PANEL_WIDTH
FONT = pygame.font.Font(None, config.FONT_SIZE)

BUILDING_KEYS = {
    pygame.K_1: ("HouseNode", (50, 100, 200)),
    pygame.K_2: ("BarnNode", (139, 69, 19)),
    pygame.K_3: ("FarmNode", (150, 100, 50)),
    pygame.K_4: ("PastureNode", (34, 139, 34)),
    pygame.K_5: ("SiloNode", (200, 200, 50)),
    pygame.K_6: ("WarehouseNode", (150, 150, 150)),
}

default_type = "HouseNode"

@dataclass
class Building:
    type: str
    rect: pygame.Rect


def draw_panel(screen, buildings, current_type):
    panel_rect = pygame.Rect(VIEW_WIDTH, 0, PANEL_WIDTH, VIEW_HEIGHT)
    pygame.draw.rect(screen, (50, 50, 50), panel_rect)
    lines = [f"Current: {current_type}", "Buildings:"]
    for b in buildings:
        w = b.rect.width / SCALE
        h = b.rect.height / SCALE
        lines.append(f"{b.type}: {w:.1f}x{h:.1f}")
    for i, text in enumerate(lines):
        surf = FONT.render(text, True, (255, 255, 255))
        screen.blit(surf, (panel_rect.x + 10, 10 + i * FONT.get_linesize()))


def export(buildings, path="custom_map.json"):
    data = {
        "world": {
            "type": "WorldNode",
            "config": {"width": WORLD_WIDTH, "height": WORLD_HEIGHT},
            "children": [],
        }
    }
    for i, b in enumerate(buildings, 1):
        x = (b.rect.x + b.rect.width / 2) / SCALE
        y = (b.rect.y + b.rect.height / 2) / SCALE
        w = b.rect.width / SCALE
        h = b.rect.height / SCALE
        node = {
            "type": b.type,
            "id": f"{b.type.lower()}{i}",
            "config": {"width": w, "height": h},
            "children": [
                {"type": "TransformNode", "config": {"position": [x, y]}}
            ],
        }
        data["world"]["children"].append(node)
    with open(path, "w", encoding="utf8") as fh:
        json.dump(data, fh, indent=2)
    print(f"Exported {len(buildings)} buildings to {path}")


def main():
    screen = pygame.display.set_mode((VIEW_WIDTH + PANEL_WIDTH, VIEW_HEIGHT))
    pygame.display.set_caption("Map Editor")
    running = True
    buildings: List[Building] = []
    current_type = default_type
    start_pos: Tuple[int, int] | None = None
    current_rect: pygame.Rect | None = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in BUILDING_KEYS:
                    current_type = BUILDING_KEYS[event.key][0]
                elif event.key == pygame.K_e:
                    export(buildings)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.pos[0] < VIEW_WIDTH:
                start_pos = event.pos
                current_rect = pygame.Rect(start_pos, (0, 0))
            elif event.type == pygame.MOUSEMOTION and start_pos and current_rect:
                x, y = start_pos
                w = event.pos[0] - x
                h = event.pos[1] - y
                current_rect.width = w
                current_rect.height = h
            elif event.type == pygame.MOUSEBUTTONUP and start_pos and current_rect:
                rect = current_rect.copy()
                if rect.width < 0:
                    rect.x += rect.width
                    rect.width = abs(rect.width)
                if rect.height < 0:
                    rect.y += rect.height
                    rect.height = abs(rect.height)
                buildings.append(Building(current_type, rect))
                start_pos = None
                current_rect = None

        screen.fill((30, 30, 30))
        for b in buildings:
            color = BUILDING_KEYS[[k for k, v in BUILDING_KEYS.items() if v[0] == b.type][0]][1]
            pygame.draw.rect(screen, color, b.rect)
        if current_rect:
            color = BUILDING_KEYS[[k for k, v in BUILDING_KEYS.items() if v[0] == current_type][0]][1]
            pygame.draw.rect(screen, color, current_rect, 1)
        draw_panel(screen, buildings, current_type)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
