import json
import os
import sys
from pathlib import Path

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

pygame.init()

SCALE = config.SCALE
WORLD_WIDTH = config.WORLD_WIDTH
WORLD_HEIGHT = config.WORLD_HEIGHT
BUILDING_SIZE = 10  # in world units

COLOR_BG = (30, 30, 30)
COLOR_BUILDING = (200, 180, 80)


def export(buildings, path="custom_map.json") -> None:
    """Export buildings to ``path`` in the required JSON format."""
    data = {
        "world": {
            "type": "WorldNode",
            "config": {"width": WORLD_WIDTH, "height": WORLD_HEIGHT},
            "children": [],
        }
    }
    for i, rect in enumerate(buildings, 1):
        cell_x = rect.x // SCALE
        cell_y = rect.y // SCALE
        node = {
            "type": "Building",
            "id": f"building{i}",
            "config": {
                "position": [cell_x, cell_y],
                "width": BUILDING_SIZE,
                "height": BUILDING_SIZE,
            },
        }
        data["world"]["children"].append(node)
    with open(path, "w", encoding="utf8") as fh:
        json.dump(data, fh, indent=2)
    print(f"Exported {len(buildings)} buildings to {path}")


def main(output_path: str = "custom_map.json") -> None:
    screen = pygame.display.set_mode((WORLD_WIDTH * SCALE, WORLD_HEIGHT * SCALE))
    pygame.display.set_caption("Map Editor")
    clock = pygame.time.Clock()
    buildings: list[pygame.Rect] = []
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                size = BUILDING_SIZE * SCALE
                rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
                buildings.append(rect)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                export(buildings, output_path)
        screen.fill(COLOR_BG)
        for rect in buildings:
            pygame.draw.rect(screen, COLOR_BUILDING, rect)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "custom_map.json"
    main(out)
