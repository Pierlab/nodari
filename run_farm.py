"""Run the farm simulation with a visual Pygame window."""

from __future__ import annotations

import sys

import pygame

import config

from core.loader import load_simulation_from_file
from core.plugins import load_plugins
from nodes.ai_behavior import AIBehaviorNode
from nodes.inventory import InventoryNode
from nodes.resource_producer import ResourceProducerNode
from nodes.character import CharacterNode
from nodes.house import HouseNode
from systems.pygame_viewer import PygameViewerSystem
from systems.time import TimeSystem


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
        "nodes.animal",
        "nodes.barn",
        "nodes.silo",
        "nodes.pasture",
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
config_file = sys.argv[1] if len(sys.argv) > 1 else "example_farm.json"
world = load_simulation_from_file(config_file)

# Relie les producteurs de ressources à leur inventaire sibling

def _link_producers(node):
    if isinstance(node, ResourceProducerNode):
        inv = next((c for c in node.parent.children if isinstance(c, InventoryNode)), None) if node.parent else None
        if inv:
            node.output_inventory = inv
    for child in node.children:
        _link_producers(child)


_link_producers(world)


def _walk(node):
    yield node
    for child in node.children:
        yield from _walk(child)


def _assign_houses(root):
    houses = [n for n in _walk(root) if isinstance(n, HouseNode)]
    characters = [n for n in _walk(root) if isinstance(n, CharacterNode)]
    for i, char in enumerate(characters):
        ai = next((c for c in char.children if isinstance(c, AIBehaviorNode)), None)
        if ai is None:
            continue
        if ai.home is None and houses:
            house = houses[i % len(houses)]
            ai.home = house
            inv = next((c for c in house.children if isinstance(c, InventoryNode)), None)
            if ai.home_inventory is None and inv:
                ai.home_inventory = inv


_assign_houses(world)

# Ajoute un système d'affichage si absent
if not any(isinstance(c, PygameViewerSystem) for c in world.children):
    PygameViewerSystem(parent=world)

time_system = next((c for c in world.children if isinstance(c, TimeSystem)), None)
if time_system is not None:
    time_system.current_time = config.START_TIME


FPS = config.FPS
TIME_SCALE = config.TIME_SCALE

clock = pygame.time.Clock()
viewer = next((c for c in world.children if isinstance(c, PygameViewerSystem)), None)
paused = False
running = True
while running and pygame.get_init():
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            paused = not paused
    if viewer:
        viewer.process_events(events)
    dt = clock.tick(FPS) / 1000.0
    world.update(0 if paused else dt * TIME_SCALE)

pygame.quit()
