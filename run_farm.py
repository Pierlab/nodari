from core.loader import load_simulation_from_file
from systems.pygame_viewer import PygameViewerSystem

# Charge la simulation depuis un fichier JSON/YAML
world = load_simulation_from_file("example_farm.json")

# Ajoute le système d'affichage (ex: Pygame)
viewer = PygameViewerSystem(parent=world)

# Boucle de mise à jour
while True:
    world.update(0.016)
