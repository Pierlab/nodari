import json
import os
import sys
from pathlib import Path
from typing import Any

import pygame

# Ensure repository root on path so ``config`` can be imported when
# executing the script from the ``tools`` directory.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config

# Allow headless execution (e.g. in CI) by falling back to the SDL
# ``dummy`` video driver when a display is not available.
if (
    sys.platform.startswith("linux")
    and "DISPLAY" not in os.environ
    and os.environ.get("SDL_VIDEODRIVER") is None
):
    os.environ["SDL_VIDEODRIVER"] = "dummy"

SCALE = config.SCALE
WORLD_WIDTH = config.WORLD_WIDTH
WORLD_HEIGHT = config.WORLD_HEIGHT
BUILDING_SIZE = 10  # in world units

COLOR_BG = (30, 30, 30)
COLOR_BUILDING = (200, 180, 80)

KEY_TO_TYPE = {
    pygame.K_1: "HouseNode",
    pygame.K_2: "BarnNode",
    pygame.K_3: "SiloNode",
    pygame.K_4: "PastureNode",
    pygame.K_5: "WellNode",
    pygame.K_6: "WarehouseNode",
}


def export(buildings, path="custom_map.json") -> None:
    """Export buildings to ``path`` in the required JSON format."""
    children: list[dict[str, Any]] = []
    data: dict[str, Any] = {
        "world": {
            "type": "WorldNode",
            "config": {"width": WORLD_WIDTH, "height": WORLD_HEIGHT},
            "children": children,
        }
    }
    for i, (rect, btype) in enumerate(buildings, 1):
        if rect.width <= 0 or rect.height <= 0:
            raise ValueError(f"Building {i} has non-positive size")
        if (
            rect.x < 0
            or rect.y < 0
            or rect.right > WORLD_WIDTH * SCALE
            or rect.bottom > WORLD_HEIGHT * SCALE
        ):
            raise ValueError(f"Building {i} is out of bounds")

        cell_x = rect.x // SCALE
        cell_y = rect.y // SCALE
        node: dict[str, Any] = {
            "type": btype,
            "id": f"building{i}",
            "config": {"position": [cell_x, cell_y]},
            "children": [
                {
                    "type": "TransformNode",
                    "config": {"position": [cell_x, cell_y]},
                }
            ],
        }
        children.append(node)
    with open(path, "w", encoding="utf8") as fh:
        json.dump(data, fh, indent=2)
    print(f"Exported {len(buildings)} buildings to {path}")


def main(output_path: str = "custom_map.json") -> None:
    pygame.init()
    screen = pygame.display.set_mode((WORLD_WIDTH * SCALE, WORLD_HEIGHT * SCALE))
    pygame.display.set_caption("Map Editor")
    clock = pygame.time.Clock()
    buildings: list[tuple[pygame.Rect, str]] = []
    current_type = KEY_TO_TYPE[pygame.K_1]
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos
                    size = BUILDING_SIZE * SCALE
                    rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
                    buildings.append((rect, current_type))
                elif event.button == 3:
                    x, y = event.pos
                    for i in range(len(buildings) - 1, -1, -1):
                        rect, _ = buildings[i]
                        if rect.collidepoint(x, y):
                            del buildings[i]
                            break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    export(buildings, output_path)
                elif event.key == pygame.K_z:
                    if buildings:
                        buildings.pop()
                elif event.key in KEY_TO_TYPE:
                    current_type = KEY_TO_TYPE[event.key]
        screen.fill(COLOR_BG)
        for rect, _ in buildings:
            pygame.draw.rect(screen, COLOR_BUILDING, rect)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "custom_map.json"
    main(out)
