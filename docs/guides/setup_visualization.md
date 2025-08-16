# Mise en place de l'environnement de visualisation

Ce guide explique comment préparer un environnement Python pour exécuter la simulation avec l'interface Pygame.

## 1. Pré-requis

- Python 3.9 ou plus récent
- `git` pour récupérer le dépôt
- Un affichage graphique (ou `SDL_VIDEODRIVER=dummy` pour un environnement sans écran)

## 2. Installation automatique

Exécutez les commandes suivantes à la racine du projet pour créer un environnement virtuel et installer les dépendances.

```bash
python -m venv .venv
# Sous Linux/macOS
source .venv/bin/activate
# Sous Windows
# .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

Ces commandes peuvent être copiées/collées telles quelles : tout s'enchaîne automatiquement.

## 3. Vérification des dépendances

Lancer les tests unitaires pour s'assurer que l'installation est correcte :

```bash
pytest
```

## 4. Lancer une visualisation d'exemple

Pour voir une simulation simple s'afficher dans une fenêtre Pygame :

```bash
# Dans le terminal où l'environnement virtuel est activé
unset SDL_VIDEODRIVER  # laisser Pygame gérer l'affichage
python - <<'PY'
from core.loader import load_simulation_from_file
from systems.pygame_viewer import PygameViewerSystem

world = load_simulation_from_file("example_farm.json")
viewer = PygameViewerSystem(parent=world)
for _ in range(1000):
    world.update(0.016)
PY
```

Une fenêtre Pygame apparaît avec un affichage minimal des entités simulées. Le viewer superpose désormais le type de terrain, des icônes d'unités et des flèches indiquant leurs déplacements. Fermez la fenêtre ou utilisez `Ctrl+C` dans le terminal pour arrêter la simulation.

## 5. Pour aller plus loin

Vous pouvez regrouper les commandes d'installation dans un script shell (`setup_env.sh`) et l'exécuter d'un seul coup :

```bash
bash setup_env.sh
```

(adaptez le script à vos besoins pour automatiser la configuration sur vos machines).
