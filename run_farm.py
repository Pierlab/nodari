from core.loader import load_simulation_from_file
from core.plugins import load_plugins
from systems.pygame_viewer import PygameViewerSystem

# Enregistre les types de nœuds disponibles
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
    ]
)

# Charge la simulation depuis un fichier JSON
world = load_simulation_from_file("example_farm.json")

# Ajoute le système d'affichage
viewer = PygameViewerSystem(parent=world)

# Boucle de mise à jour
try:
    while True:
        world.update(0.016)
except KeyboardInterrupt:
    pass
