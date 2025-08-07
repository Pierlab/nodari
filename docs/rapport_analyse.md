# Rapport d'analyse du projet nodari

## 1. Objectifs et contexte
Le projet **nodari** vise à construire un moteur de simulation modulaire capable de modéliser des fermes puis d'autres scénarios (aventure, guerre, société...). Les objectifs principaux sont :
- **Modularité et extensibilité** : chaque fonctionnalité est encapsulée dans un nœud réutilisable et de nouveaux nœuds peuvent être ajoutés sans modifier le cœur de l'engine.
- **Rejouabilité** : les simulations doivent être déterministes via une graine.
- **Séparation modèle/rendu** : la logique de simulation est indépendante du rendu graphique.
- **Chargement déclaratif** : l'arbre de nœuds est décrit dans un fichier JSON ou YAML et instancié automatiquement.
- **Observabilité** : l'état de la simulation doit être inspectable, avec journalisation et évènements horodatés.

Le fichier `README.md` rappelle l'usage du mètre et du mètre par seconde comme unités de base (helpers dans `core/units.py`). Un exemple de monde minimal est fourni dans `example_farm.json`.

## 2. Structure et conformité au cahier des charges

### 2.1 Arbre de nœuds et bus d'évènements
La classe `SimNode` (`core/simnode.py`) forme le cœur de l'engine. Chaque nœud possède un parent et une liste d'enfants, et gère l'enregistrement de gestionnaires d'évènements via `on_event`/`off_event`. La méthode `emit` propage un évènement vers tous les enfants ainsi que vers le parent et ajoute désormais un horodatage. Les gestionnaires peuvent retourner `False` ou renseigner `stop_propagation` dans le payload pour interrompre la diffusion.

### 2.2 Systèmes globaux
Plusieurs systèmes héritent de `SystemNode` et appliquent des comportements globaux :

| Système | Rôle | Notes |
|--------|------|-------|
| `TimeSystem` | Gère l'écoulement du temps et émet `tick`/`phase_changed`. | Durées paramétrables. |
| `EconomySystem` | Traite les demandes d'achat entre nœuds. | Pas de fluctuation de prix. |
| `DistanceSystem` | Calcule la distance euclidienne entre deux nœuds. | Met en cache les distances à chaque tick. |
| `SchedulerSystem` | Planifie la mise à jour de nœuds à des cadences différentes. | Base d'un scheduler complet. |
| `LoggingSystem` | Journalise les évènements. | Simple mais efficace. |
| `PygameViewerSystem` | Affiche une vue 2D et des panneaux d'inventaire. | Zoom et outils possibles. |

Le `WeatherSystem` mentionné dans la spécification n'est pas encore implémenté.

### 2.3 Nœuds génériques et composés
La spécification définit plusieurs nœuds de base que le projet implémente :
- `InventoryNode` : gère un dictionnaire `items` et émet `inventory_changed` à chaque modification.
- `NeedNode` : modélise un besoin croissant, déclenchant `need_threshold_reached` et `need_satisfied`.
- `ResourceProducerNode` : produit une ressource à chaque tick ou sur demande.
- `TransformNode` : stocke position et vitesse en mètres/m/s.
- `AIBehaviorNode` : pilote les personnages humains (déplacements, besoins, économie). Ce fichier est volumineux (~350 lignes) et regroupe plusieurs responsabilités.
- `CharacterNode`, `FarmNode`, `WorldNode`, `HouseNode`, `WellNode`, `WarehouseNode` : nœuds composés servant de conteneurs.

Le chargement déclaratif est assuré par `core/loader.py` via un registre global de classes (`register_node_type`, `get_node_type`).
La méthode `serialize` de `SimNode` inclut désormais positions, inventaires et besoins dans l'état exporté.

## 3. Observations sur les fichiers
La plupart des fichiers Python sont concis. `AIBehaviorNode` constitue l'exception principale et pourrait devenir une source de dette technique sans refactorisation.

## 4. Pistes d'optimisation et d'amélioration

### 4.1 Bus d'évènements et boucle de mise à jour
- Le bus d'évènements gère l'arrêt de la propagation et ajoute un horodatage à chaque émission.
- Utiliser `SchedulerSystem` pour réduire la fréquence de mise à jour des nœuds lents (`NeedNode`, IA...).
- Généraliser les caches immuables (ex. `_iter_children`) aux gestionnaires d'évènements.

### 4.2 Nœud `AIBehaviorNode`
- Séparer planification, navigation et interactions économiques en composants distincts.
- Remplacer les horaires codés en dur par une machine à états ou un arbre de comportement.
- Résoudre les références (`home`, `work`, etc.) lors du chargement pour éviter les recherches répétées.
- Paramétrer les valeurs clés (durée de journée, vitesse de marche, seuils) via la configuration.
- Confier la cadence de mise à jour au `SchedulerSystem`.

### 4.3 Autres pistes
- Enrichir `EconomySystem` avec une économie dynamique.
- Implémenter un `WeatherSystem` impactant la production et les comportements.

## 5. Roadmap et tâches en attente
Le fichier `project_spec.md` recense les jalons atteints et les étapes futures. Les tâches identifiées incluent :
- Optimiser le scheduler pour les grandes simulations.
- Permettre la sérialisation complète et le rechargement de l'état du monde.
- Créer des outils de création (templates, validation de schéma, éditeur de nœuds).
- Enrichir la visualisation (zoom, caméra, mode web, 3D).
- Ajouter des mécaniques avancées (météo, animaux, quêtes, combat, économie dynamique, arbres de comportement).
- Mettre en place un CI/benchmark avec alertes de régression et versionnage des plugins.
- Développer la documentation, des tutoriels et une marketplace communautaire.

## 6. Conclusion
Nodari constitue un socle prometteur pour des simulations modulaires. L'architecture en nœuds, le bus d'évènements et le chargement déclaratif respectent la spécification, tandis que l'unification des unités renforce la cohérence du moteur.

Le point de vigilance majeur reste `AIBehaviorNode`, dont la complexité justifie une refactorisation. Parallèlement, l'amélioration du bus d'évènements, la sérialisation et les outils de benchmark renforceront la robustesse du projet.
