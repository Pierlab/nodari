"""Run the farm simulation with a visual Pygame window."""

from __future__ import annotations

import pygame

from core.loader import load_simulation_from_file
from core.plugins import load_plugins
from nodes.ai_behavior import AIBehaviorNode
from nodes.inventory import InventoryNode
from nodes.resource_producer import ResourceProducerNode
from systems.pygame_viewer import PygameViewerSystem


# Charge tous les plugins nécessaires pour la simulation
load_plugins(
    [
        "nodes.world",
        "nodes.farm",
        "nodes.inventory",
        "nodes.resource_producer",
        "nodes.character",
        "nodes.need",
        "nodes.ai_behavior",
        "nodes.transform",
        "nodes.house",
        "nodes.well",
        "nodes.warehouse",
        "systems.time",
        "systems.economy",
        "systems.logger",
        "systems.distance",
        "systems.pygame_viewer",
    ]
)


def _find(node, name):
    if node.name == name:
        return node
    for child in node.children:
        found = _find(child, name)
        if found:
            return found
    return None


# Charge la simulation depuis un fichier JSON/YAML
world = load_simulation_from_file("example_farm.json")

# Relie les producteurs de ressources à leur inventaire sibling

def _link_producers(node):
    if isinstance(node, ResourceProducerNode):
        inv = next((c for c in node.parent.children if isinstance(c, InventoryNode)), None) if node.parent else None
        if inv:
            node.output_inventory = inv
    for child in node.children:
        _link_producers(child)


_link_producers(world)

# Ajoute un système d'affichage si absent
if not any(isinstance(c, PygameViewerSystem) for c in world.children):
    PygameViewerSystem(parent=world)


FPS = 24
TIME_SCALE = 86400 / 120  # 1 journée simulée = 2 minutes réelles

clock = pygame.time.Clock()

while pygame.get_init():
    dt = clock.tick(FPS) / 1000.0
    world.update(dt * TIME_SCALE)

pygame.quit()
