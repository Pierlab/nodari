# Checklist de refactorisation pour recentrer le projet sur la simulation de guerre

Cette checklist décrit les actions à réaliser pour supprimer la simulation de ferme et optimiser la simulation de guerre. Chaque tâche doit être exécutée dans l’ordre indiqué afin de conserver un code fonctionnel et cohérent. Les chemins sont relatifs à la racine du dépôt **Pierlab/nodari**.

---

## 1. Suppression de la simulation de ferme

- [x] Supprimer `run_farm.py`.
- [x] Supprimer les nœuds liés à la ferme dans `nodes/` :
  - `farm.py`, `animal.py`, `barn.py`, `silo.py`, `pasture.py`, `house.py`, `well.py`, `warehouse.py`, `inventory.py`, `resource_producer.py`, `character.py`, `need.py`, `ai_behavior.py`, `ai_utils.py`.
  - Supprimer aussi le sous-répertoire `nodes/routines/` et ses fichiers (`farmer.py`, etc.).
- [x] Supprimer les systèmes de ferme dans `systems/`, notamment `economy.py`.
- [x] Nettoyer `systems/pygame_viewer.py` :
  - Supprimer les importations de classes agricoles (FarmNode, BarnNode, SiloNode, PastureNode, HouseNode, WellNode, WarehouseNode).
  - Retirer les dictionnaires et constantes qui définissent tailles/couleurs pour les bâtiments agricoles.
- [x] Vérifier et supprimer dans `tools/` les scripts orientés ferme.
- [x] Nettoyer la documentation `docs/` pour supprimer les références à la ferme.

---

## 2. Recentralisation sur la simulation de guerre

- [x] Adapter `run_war.py` :
  - Supprimer le chargement des modules agricoles dans `load_plugins()`.
  - Découper le fichier trop volumineux en sous-modules :
    - `war_loader.py` (chargement des paramètres et du monde).
    - `terrain_setup.py` (génération et placement des terrains).
    - `viewer_loop.py` (gestion de la boucle d’affichage Pygame).
    - `presets.py` (configurations de terrain, unités, etc.).
- [x] Créer un package dédié (par ex. `simulation/war/`) regroupant :
  - `nodes/` (armée, général, nation, unité, etc.).
  - `systems/` (combat, mouvement, moral, victoire, pathfinding, visibilité).
  - `terrain/` et `ui/` pour une séparation claire.
- [x] Maintenir uniquement les systèmes militaires (combat, moral, mouvement, pathfinding, victoire).

---

## 3. Optimisation de la rapidité

- [x] Mettre en place un **cache de terrain** :
  - Créer un script `tools/precompute_map.py` pour générer un terrain et le sauvegarder.
  - Modifier `run_war.py` pour charger directement ce cache si disponible.
- [x] Réduire les importations lourdes au démarrage :
  - Importer certains modules (ex. Pygame, terrain) seulement au moment de leur utilisation.
- [x] Profiler et optimiser `systems/movement.py`, `systems/pathfinding.py`, `systems/visibility.py` :
  - Utiliser des structures de données plus efficaces si nécessaire (numpy, graphes optimisés).
  - Réduire la fréquence des calculs et logs.
- [x] Vérifier `pygame_viewer.py` :
  - Paramétrer correctement `max_terrain_resolution` et les options de rendu pour accélérer le démarrage.

---

## 4. Tests et documentation

- [x] Supprimer les tests liés à la ferme (farm, barn, etc.).
- [x] Vérifier que les tests restants couvrent les nœuds et systèmes militaires.
- [x] Ajouter de nouveaux tests unitaires pour :
  - ArmyNode, UnitNode, OfficerNode.
  - Systèmes combat, moral, pathfinding, victoire.
  - Chargement de presets et cohérence des paramètres.
- [x] Mettre à jour la documentation dans `docs/` pour :
  - Fournir un guide clair sur la simulation de guerre.
  - Documenter la nouvelle architecture modulaire.
  - Lister les paramètres disponibles (remplacer `parameter_inventory.md`).

---
