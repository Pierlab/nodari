# Global Specification for the Medieval City Growth Simulator

## Objectif général
Construire un simulateur de croissance de cité médiévale inspiré de *The Settlers II*. Le système doit permettre la création et l'expansion d'un royaume via la gestion des ressources, la construction de bâtiments, la production d'objets et l'activité militaire. La simulation est visualisée en temps réel avec une animation fluide.

---

## Vision initiale de la simulation
1. **Colonisation** : Des travailleurs quittent la capitale pour établir une nouvelle cité reliée par une route.
2. **Expansion démographique** : La capitale envoie régulièrement de nouveaux villageois vers les cités éloignées.
3. **Production de ressources** : Les cités produisent et stockent des ressources; elles peuvent être rapatriées à la capitale.
4. **Unités spécialisées** : Les travailleurs peuvent changer d'état pour devenir fermiers, bûcherons ou éclaireurs.
5. **Exploration** : Les éclaireurs dissipent le brouillard de guerre et révèlent de nouvelles régions.
6. **Combat** : Les unités attaquent automatiquement les ennemis dans leur champ de vision. Un bâtiment peut être détruit par les attaques.

---

## Conventions d'échelle
- **Temps** : secondes comme unité de base; minutes et heures utilisées pour l'affichage.
- **Espace** : mètres comme unité de base. Les tuiles de terrain sont converties via la constante `METERS_PER_TILE` définie dans `core/terrain.py`.

---

## Architecture logique
Le projet s'appuie sur une architecture modulaire composée de nœuds (`nodes`) interconnectés via un bus de messages (`bus`) et orchestrés par des systèmes (`systems`).

### Diagramme général
```text
+-------------------+
|  Simulation Core  |
+---------+---------+
          |
          v
    +-----+------+
    |   Bus      |
    +-----+------+
          |
  +-------+-------+-----------------------------+
  |       |       |                             |
  v       v       v                             v
Nodes  Systems  Scheduler                   Viewer
```

### Arborescence cible
```text
nodari/
├── core/
├── nodes/
│   ├── building.py
│   ├── resource.py
│   └── worker.py
├── systems/
│   ├── ai.py
│   ├── combat.py
│   ├── economy.py
│   ├── movement.py
│   ├── moderngl_viewer.py
│   ├── pygame_viewer.py
│   └── scheduler.py
├── docs/
│   ├── global_spec.md ← ce document
│   ├── viewers.md
│   └── workers.md
└── tests/
    ├── test_ai.py
    ├── test_combat_building.py
    └── test_economy.py
```

---

## Nœuds
Les nœuds représentent toutes les entités du monde (unités, bâtiments, stocks). Ils héritent de `SimNode` et communiquent via le bus.

### `BuildingNode`
| Attribut      | Description                               |
|---------------|-------------------------------------------|
| `type`        | Type de bâtiment (ferme, tour, entrepôt). |
| `capacity`    | Quantité maximale d'unités ou de ressources. |
| `hit_points`  | Points de vie pour les combats.           |
| `strategic`   | Sa destruction peut entraîner la défaite. |

### `ResourceNode`
| Attribut        | Description                                          |
|-----------------|------------------------------------------------------|
| `kind`          | Type de ressource (bois, nourriture, pierre...).     |
| `quantity`      | Quantité disponible.                                 |
| `max_quantity`  | Limite de stockage.                                  |

### `WorkerNode`
| État        | Description                                                      |
|-------------|------------------------------------------------------------------|
| `idle`      | Aucune tâche assignée; n'est pas programmé dans le scheduler.   |
| `gathering` | Collecte une ressource; inscrit dans le scheduler toutes les `n` secondes.
| `building`  | Participe à la construction d'un bâtiment.                       |

Les transitions d'état sont déclenchées par des événements : `task_assigned`, `task_complete`, `unit_idle`.

La méthode `find_task()` sélectionne la ressource disponible la plus proche grâce au `PathfindingSystem` et assigne la cible en émettant `unit_move`.

Voir `workers.md` pour une documentation d'utilisation détaillée.

### `BuilderNode`
Spécialisation de `WorkerNode` capable de fonder des villes et de relier les routes.
L'`AISystem` peut en créer automatiquement à intervalles réguliers.

---

## Systèmes
Les systèmes encapsulent des règles de jeu spécifiques et écoutent les messages.

### `EconomySystem`
- Gère la **production**, la **consommation** et les **transferts** de ressources.
- Méthodes principales :
  - `produce(node, kind, amount)`
  - `transfer(src, dst, kind, amount)` (`dst` peut être `None` pour une consommation directe)
- Émet des événements `resource_produced` et `resource_consumed`.
- Lève une erreur si le stock est insuffisant.

### `SchedulerSystem`
- Exécute les mises à jour d'unités selon un intervalle (`n` secondes) au lieu de chaque tick.
- Les ouvriers inactifs sont désinscrits du scheduler.
- Les unités ajoutées dynamiquement sont inscrites dès qu'une tâche leur est assignée.

### `AISystem`
- Réagit à `unit_idle` pour chercher une nouvelle tâche via `find_task()`.
- Peut générer un `BuilderNode` à la capitale de chaque nation toutes les
  `builder_spawn_interval` secondes et émet immédiatement `unit_idle` pour
  qu'il soit pris en charge.
- Stratégies :
  - **Recherche de ressource** la plus proche en utilisant `systems.pathfinding`.
  - **Exploration** de coordonnées inconnues dans un rayon donné en émettant `unit_move`.

### `CombatSystem`
- Permet d'attaquer des unités et des bâtiments (`attack_building`).
- Déclenche `building_destroyed` lorsque les `hit_points` tombent à zéro.
- Interagit avec `VictorySystem` pour évaluer la perte de bâtiments stratégiques.

### `Viewer`
- Interface de rendu abstraite.
- Implémentations :
  - `pygame_viewer.py` : backend existant.
  - `moderngl_viewer.py` : backend OpenGL pour de meilleures performances.
- `run_war.py` accepte `--viewer` pour choisir l'implémentation.
- Voir `viewers.md` pour une comparaison de performances.

### `MovementSystem` et `TimeSystem`
- Garantissent la cohérence des unités de temps et d'espace.
- Conversions explicites entre mètres et tuiles.

### `VictorySystem`
- Détecte la capture de la capitale et l'effondrement moral.
- Écoute `building_destroyed` pour déclarer la défaite lorsqu'un bâtiment stratégique est perdu.

---

## Événements principaux
| Événement              | Déclencheur / Résultat                                |
|------------------------|--------------------------------------------------------|
| `task_assigned`        | Assigner une tâche à un ouvrier.                       |
| `task_complete`        | Fin de collecte ou de construction.                    |
| `unit_idle`            | Aucun travail; déclenche la recherche de tâche.        |
| `resource_produced`    | Production réussie d'une ressource.                    |
| `resource_consumed`    | Consommation de ressource.                             |
| `unit_move`            | Déplacement d'une unité vers une cible.                |
| `attack_building`      | Cible un bâtiment; peut mener à `building_destroyed`.  |
| `building_destroyed`   | Bâtiment détruit, potentielle condition de défaite.   |

---

## Exemple de cycle de jeu
1. **Assignation** : Un `WorkerNode` reçoit `task_assigned` pour récolter du bois.
2. **Scheduler** : `SchedulerSystem` planifie une vérification toutes les `n` secondes.
3. **Collecte** : `EconomySystem.produce` augmente le stock de bois dans un `ResourceNode`.
4. **Transport** : `EconomySystem.transfer` déplace le bois vers l'entrepôt.
5. **Construction** : Les ressources disponibles permettent de construire un `BuildingNode` supplémentaire.
6. **Combat** : Un ennemi attaque l'entrepôt; `CombatSystem.attack_building` réduit ses `hit_points` jusqu'à `building_destroyed`.

---

## Exemples
Un fichier de configuration minimal `example/farm_warehouse.json` illustre une ferme et un entrepôt utilisant `BuildingNode` et `ResourceNode` avec des stocks initiaux.

---

## Notes de développement
- Le système doit minimiser les calculs inutiles : les ouvriers ne font pas de vérification à chaque tick.
- Tous les comportements IA restent simples mais extensibles.
- L'objectif final est d'étendre le royaume en explorant et exploitant les ressources environnantes.

---

Fin du document.
