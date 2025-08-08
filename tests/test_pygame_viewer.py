import os

import pytest

from nodes.world import WorldNode
from nodes.inventory import InventoryNode


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
