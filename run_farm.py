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
        "systems.time",
        "systems.economy",
        "systems.logger",
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

# Relie les composants qui doivent coopérer
farm_inventory = _find(world, "farm_inventory")
producer = _find(world, "producer")
if isinstance(producer, ResourceProducerNode) and isinstance(farm_inventory, InventoryNode):
    producer.output_inventory = farm_inventory

farmer = _find(world, "farmer")
if farmer:
    ai = next((c for c in farmer.children if isinstance(c, AIBehaviorNode)), None)
    if ai and isinstance(farm_inventory, InventoryNode):
        ai.target_inventory = farm_inventory

# Ajoute un système d'affichage si absent
if not any(isinstance(c, PygameViewerSystem) for c in world.children):
    PygameViewerSystem(parent=world)


FPS = 24
TIME_SCALE = 86400 / (3 * 60)  # 1 journée simulée = 3 minutes réelles

clock = pygame.time.Clock()

while pygame.get_init():
    dt = clock.tick(FPS) / 1000.0
    world.update(dt * TIME_SCALE)

pygame.quit()
