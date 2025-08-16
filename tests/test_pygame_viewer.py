import os

import pytest

from nodes.world import WorldNode
from nodes.inventory import InventoryNode
from nodes.character import CharacterNode
from nodes.transform import TransformNode


def test_pygame_viewer_runs():
    pygame = pytest.importorskip("pygame")
    from systems.pygame_viewer import PygameViewerSystem

    os.environ["SDL_VIDEODRIVER"] = "dummy"
    world = WorldNode(name="world")
    InventoryNode(name="inv", items={"wheat": 1}, parent=world)
    viewer = PygameViewerSystem(parent=world, width=120, height=80, panel_width=30)
    world.update(0)
    assert viewer.screen.get_size() == (150, 80)
    pygame.quit()


def test_viewer_zoom_and_center():
    pygame = pytest.importorskip("pygame")
    from systems.pygame_viewer import PygameViewerSystem

    os.environ["SDL_VIDEODRIVER"] = "dummy"
    world = WorldNode(name="world")
    char = CharacterNode(name="hero", parent=world)
    TransformNode(position=[20, 30], parent=char)
    viewer = PygameViewerSystem(parent=world, width=100, height=100, scale=1, panel_width=0)
    viewer.process_events([pygame.event.Event(pygame.MOUSEWHEEL, {"y": 1})])
    assert viewer.scale > 1
    viewer.process_events([pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (20, 30), "button": 1})])
    assert viewer.selected is char
    expected_x = 20 - viewer.view_width / (2 * viewer.scale)
    expected_y = 30 - viewer.view_height / (2 * viewer.scale)
    assert viewer.offset_x == pytest.approx(expected_x)
    assert viewer.offset_y == pytest.approx(expected_y)
    pygame.quit()
