import importlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Mapping, cast

import pygame

# Ensure repository root on path so ``config`` and ``core`` can be imported when
# executing the script from the ``tools`` directory.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config
from core import plugins

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
BUILDING_SIZE = config.BUILDING_SIZE  # in world units

COLOR_BG = (30, 30, 30)
COLOR_BUILDING = (200, 180, 80)
COLOR_GRID = (50, 50, 50)
COLOR_CHARACTER_MALE = (50, 150, 255)
COLOR_CHARACTER_FEMALE = (255, 105, 180)
CHAR_RADIUS = 5

DEFAULT_KEYMAP: dict[int, str] = {
    pygame.K_1: "HouseNode",
    pygame.K_2: "BarnNode",
    pygame.K_3: "SiloNode",
    pygame.K_4: "PastureNode",
    pygame.K_5: "WellNode",
    pygame.K_6: "WarehouseNode",
}


def _load_plugin_for_type(type_name: str) -> None:
    """Import the module defining ``type_name`` to register the plugin."""
    module = re.sub(r"(?<!^)(?=[A-Z])", "_", type_name).lower()
    if module.endswith("_node"):
        module = module[: -len("_node")]
    try:
        importlib.import_module(f"nodes.{module}")
    except ModuleNotFoundError:
        pass


def load_key_mapping(source: Mapping[int | str, str] | str | None = None) -> dict[int, str]:
    """Return a key-to-type mapping verifying node type existence.

    ``source`` may be a mapping or path to a JSON file. Keys may be either
    integers (pygame key codes) or strings acceptable to ``pygame.key.key_code``.
    """
    if source is None:
        data = cast(Mapping[int | str, str], DEFAULT_KEYMAP)
    elif isinstance(source, str):
        with open(source, "r", encoding="utf8") as fh:
            data = json.load(fh)
    else:
        data = source

    mapping: dict[int, str] = {}
    for key, type_name in data.items():
        key_code = (
            pygame.key.key_code(key) if isinstance(key, str) else int(key)
        )
        _load_plugin_for_type(type_name)
        plugins.get_node_type(type_name)  # raises if type is unknown
        mapping[key_code] = type_name
    return mapping


def export(
    buildings,
    path: str = "custom_map.json",
    characters: list[tuple[tuple[int, int], str]] | None = None,
) -> None:
    """Export buildings and characters to ``path`` in the required JSON format."""
    if characters is None:
        characters = []
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
            "config": {
                "width": rect.width // SCALE,
                "height": rect.height // SCALE,
            },
            "children": [
                {
                    "type": "TransformNode",
                    "config": {"position": [cell_x, cell_y]},
                }
            ],
        }
        children.append(node)
    for i, ((x, y), gender) in enumerate(characters, 1):
        if (
            x < 0
            or y < 0
            or x >= WORLD_WIDTH * SCALE
            or y >= WORLD_HEIGHT * SCALE
        ):
            raise ValueError(f"Character {i} is out of bounds")
        cell_x = x // SCALE
        cell_y = y // SCALE
        node = {
            "type": "CharacterNode",
            "id": f"character{i}",
            "config": {"gender": gender},
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
    print(
        f"Exported {len(buildings)} buildings and {len(characters)} characters to {path}"
    )


def main(
    output_path: str = "custom_map.json",
    keymap: Mapping[int | str, str] | str | None = None,
    input_path: str | None = None,
) -> None:
    pygame.init()
    key_to_type = load_key_mapping(keymap)
    screen = pygame.display.set_mode((WORLD_WIDTH * SCALE, WORLD_HEIGHT * SCALE))
    pygame.display.set_caption("Map Editor")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 20)
    buildings: list[tuple[pygame.Rect, str]] = []
    characters: list[tuple[tuple[int, int], str]] = []
    history: list[str] = []
    current_type = next(iter(key_to_type.values()))
    mode = "building"
    current_gender = "male"
    selected: int | None = None

    if input_path and os.path.exists(input_path):
        with open(input_path, "r", encoding="utf8") as fh:
            data = json.load(fh)
        children = data.get("world", {}).get("children", [])
        for child in children:
            _load_plugin_for_type(child.get("type", ""))
            if child.get("type") == "CharacterNode":
                pos = child.get("children", [])[0]["config"].get("position", [0, 0])
                x, y = pos[0] * SCALE, pos[1] * SCALE
                gender = child.get("config", {}).get("gender", "male")
                characters.append(((x, y), gender))
            else:
                pos = child.get("children", [])[0]["config"].get("position", [0, 0])
                width = child.get("config", {}).get("width", BUILDING_SIZE)
                height = child.get("config", {}).get("height", BUILDING_SIZE)
                rect = pygame.Rect(
                    pos[0] * SCALE, pos[1] * SCALE, width * SCALE, height * SCALE
                )
                buildings.append((rect, child.get("type", "Unknown")))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                export(buildings, output_path, characters)
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = event.pos
                    x = round(x / SCALE) * SCALE
                    y = round(y / SCALE) * SCALE
                    if mode == "building":
                        size = BUILDING_SIZE * SCALE
                        rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
                        buildings.append((rect, current_type))
                        history.append("building")
                    elif mode == "character":
                        characters.append(((x, y), current_gender))
                        history.append("character")
                    else:  # selection
                        selected = None
                        for i in range(len(buildings) - 1, -1, -1):
                            rect, _ = buildings[i]
                            if rect.collidepoint(x, y):
                                selected = i
                                break
                elif event.button == 3:
                    x, y = event.pos
                    for i in range(len(buildings) - 1, -1, -1):
                        rect, _ = buildings[i]
                        if rect.collidepoint(x, y):
                            del buildings[i]
                            break
                    else:
                        for i in range(len(characters) - 1, -1, -1):
                            (cx, cy), _ = characters[i]
                            if (cx - x) ** 2 + (cy - y) ** 2 <= CHAR_RADIUS ** 2:
                                del characters[i]
                                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    export(buildings, output_path, characters)
                elif event.key == pygame.K_z:
                    if history:
                        last = history.pop()
                        if last == "building" and buildings:
                            buildings.pop()
                        elif last == "character" and characters:
                            characters.pop()
                elif event.key in key_to_type:
                    current_type = key_to_type[event.key]
                    mode = "building"
                    selected = None
                elif event.key == pygame.K_m:
                    mode = "character"
                    current_gender = "male"
                    selected = None
                elif event.key == pygame.K_f:
                    mode = "character"
                    current_gender = "female"
                    selected = None
                elif event.key == pygame.K_s:
                    mode = "select"
                elif selected is not None and event.key in (
                    pygame.K_LEFT,
                    pygame.K_RIGHT,
                    pygame.K_UP,
                    pygame.K_DOWN,
                ):
                    rect, btype = buildings[selected]
                    if event.key == pygame.K_LEFT and rect.width > SCALE:
                        rect.width -= SCALE
                    elif event.key == pygame.K_RIGHT:
                        rect.width += SCALE
                    elif event.key == pygame.K_UP and rect.height > SCALE:
                        rect.height -= SCALE
                    elif event.key == pygame.K_DOWN:
                        rect.height += SCALE
        screen.fill(COLOR_BG)

        # Draw a grid to help users place buildings aligned with the scale.
        for gx in range(0, WORLD_WIDTH * SCALE, SCALE):
            pygame.draw.line(screen, COLOR_GRID, (gx, 0), (gx, WORLD_HEIGHT * SCALE))
        for gy in range(0, WORLD_HEIGHT * SCALE, SCALE):
            pygame.draw.line(
                screen, COLOR_GRID, (0, gy), (WORLD_WIDTH * SCALE, gy)
            )

        for i, (rect, _) in enumerate(buildings):
            pygame.draw.rect(screen, COLOR_BUILDING, rect)
            if i == selected:
                pygame.draw.rect(screen, (255, 255, 255), rect, 2)
        for (x, y), gender in characters:
            color = COLOR_CHARACTER_MALE if gender == "male" else COLOR_CHARACTER_FEMALE
            pygame.draw.circle(screen, color, (x, y), CHAR_RADIUS)

        lines = [
            f"Current: {current_type if mode == 'building' else f'Character ({current_gender})'}",
            "1-6: buildings",
            "M/F: male/female character",
            "S: select/resize mode",
            "Arrows: resize selected",
            "Left click: place/select, Right click: delete",
            "Z: undo, E: export",
        ]
        for i, line in enumerate(lines):
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (5, 5 + i * 18))

        pygame.display.flip()
        clock.tick(60)
    pygame.quit()


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "custom_map.json"
    cfg = sys.argv[2] if len(sys.argv) > 2 else None
    inp = sys.argv[3] if len(sys.argv) > 3 else None
    main(out, cfg, inp)
