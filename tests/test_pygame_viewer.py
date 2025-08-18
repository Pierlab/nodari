import os
import pytest

from nodes.world import WorldNode
from nodes.inventory import InventoryNode
from nodes.character import CharacterNode
from nodes.transform import TransformNode
from nodes.terrain import TerrainNode
from nodes.unit import UnitNode
from nodes.nation import NationNode


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


def test_viewer_draws_overlay():
    pygame = pytest.importorskip("pygame")
    from systems.pygame_viewer import PygameViewerSystem

    os.environ["SDL_VIDEODRIVER"] = "dummy"
    world = WorldNode(name="world")
    TerrainNode(name="terrain", tiles=[["plain"]], parent=world)
    nation = NationNode(name="n", morale=100, capital_position=[0, 0], parent=world)
    unit = UnitNode(name="u", target=[0.5, 1.5], parent=nation)
    TransformNode(position=[1.5, 1.5], parent=unit)
    viewer = PygameViewerSystem(parent=world, width=40, height=40, scale=20, panel_width=0)
    world.update(0)

    assert viewer.screen.get_at((5, 5))[:3] == (80, 160, 80)
    assert viewer.screen.get_at((30, 30))[:3] == (200, 50, 50)
    assert viewer.screen.get_at((20, 30))[:3] == (255, 255, 0)
    pygame.quit()


def test_menu_buttons_trigger_callbacks():
    pygame = pytest.importorskip("pygame")
    from systems.pygame_viewer import PygameViewerSystem

    os.environ["SDL_VIDEODRIVER"] = "dummy"
    world = WorldNode(name="world")
    viewer = PygameViewerSystem(parent=world, width=100, height=80, panel_width=80)

    calls = {"minus": 0, "plus": 0}

    def dec():
        calls["minus"] += 1

    def inc():
        calls["plus"] += 1

    viewer.set_menu_items([{ "label": "Val", "minus": dec, "plus": inc }])
    world.update(0)

    minus_rect, plus_rect = viewer._menu_button_rects[0][0], viewer._menu_button_rects[1][0]
    viewer.process_events([
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": minus_rect.center, "button": 1})
    ])
    viewer.process_events([
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": plus_rect.center, "button": 1})
    ])

    assert calls["minus"] == 1
    assert calls["plus"] == 1
    pygame.quit()
