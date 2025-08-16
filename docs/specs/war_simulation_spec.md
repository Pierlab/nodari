# Spécifications de la Simulation de Guerre (Projet Nodari)

## Objectif
Créer une simulation de guerre inspirée de *Kingdom*, basée sur le moteur **Nodari**, permettant de visualiser en temps réel ou accéléré l'affrontement entre deux nations.  
La version initiale est simplifiée mais conçue pour évoluer.

---

## 1. Architecture générale
La simulation est construite à partir de **SimNodes** et de **systèmes globaux**.  
Chaque entité (Nation, Général, Armée, Unité, Terrain) est un nœud ou un regroupement de nœuds.  
Un **bus d’événements** centralise les interactions (combats, mouvements, ordres).

---

## 2. Entités principales

### Nation
- Regroupe toutes les forces d’un camp.
- Possède un objectif : **capturer la capitale ennemie**.
- Caractéristique principale : **moral global** (impacte toutes les armées).

### Général
- Chaque nation dispose de **2 à 3 généraux**.
- Commande une ou plusieurs armées.
- Caractéristique principale : **style tactique** (agressif, défensif, équilibré).
- Reçoit les informations partielles du champ de bataille (brouillard de guerre).
- Ajuste les objectifs des armées selon ces rapports et le moral national.

### Armée
- Regroupe un ensemble d’unités.
- Caractéristique principale : **taille** (nombre d’unités).
- Objectif : avancer vers le camp adverse ou exécuter les ordres du général.

### Unité
- Représente un petit groupe de soldats (ex. 100 hommes = 1 unité).
- Caractéristique principale : **état** (combat, déplacement, fuite).
- Actions possibles :
  - Se déplacer
  - Combattre
  - Battre en retraite

### Terrain
- La carte est divisée en zones : **plaine, forêt, colline**.
- Caractéristique principale : **influence sur les mouvements**.
  - Plaines → déplacements rapides
  - Forêts → ralentissement, bonus défensif
  - Collines → bonus de visibilité et de défense
- La grille est contrôlée par le paramètre ``grid_type`` du ``TerrainNode``
  (``square`` par défaut, ``hex`` prévu pour une future version).
- Les obstacles infranchissables (rivières, montagnes) sont listés via
  ``obstacles`` dans le ``TerrainNode``.

### Positionnement initial
- Chaque nation définit une ``capital_position`` dans la configuration.
- Les ``GeneralNode`` et ``ArmyNode`` reçoivent un ``TransformNode`` indiquant leur position de départ.
- Les ``UnitNode`` disposent également d'un ``TransformNode`` pour être placées sur la carte.

---

## 3. Systèmes globaux

### Temps
- Simulation basée sur des ticks (1 tick = 1 unité de temps).
- Possibilité de mode temps réel ou accéléré.
- Le paramètre `time_scale` du `TimeSystem` ajuste l'accélération du temps.

### Mouvement
- Les unités se déplacent vers une position cible.
- La vitesse est affectée par le type de terrain et le moral de l’unité.
- Les obstacles définis dans ``TerrainNode.obstacles`` sont infranchissables.
- Implémentation initiale en grille carrée (préparation pour une grille hexagonale ultérieure).

### Combat
- Lorsque deux unités ennemies se rencontrent :
  - Jet de combat simplifié basé sur la taille de l’unité, un bonus de terrain et un facteur aléatoire.
  - Le perdant subit une perte de taille, voit son moral national réduit et passe en état **fuite**.

### Moral
- Chaque nation possède un moral global.
- Un `MoralSystem` agrège les variations de moral et émet `nation_collapsed` quand il atteint zéro.
- Le moral baisse lorsque :
  - Une armée subit une lourde défaite.
  - Un général est battu ou tué.
- Si le moral atteint 0 → effondrement, la nation perd.

### Journalisation des événements
- Un `LoggingSystem` écoute les événements comme `unit_moved`, `combat_occurred`,
  `unit_engaged` et `unit_routed`.
- Il consigne ces événements pour une visualisation en temps réel ou accélérée.

---

## 4. Conditions de victoire
- Une nation gagne si :
  - **Un nombre suffisant d’unités atteint le camp ennemi** (capture de capitale).
  - **Le moral adverse tombe à 0**.

---

## 5. Visualisation
- Vue aérienne du champ de bataille.
- Chaque armée représentée par un bloc.
- Déplacements visibles en temps réel ou accéléré.
- Possibilité de zoomer sur une unité.

---

## 6. Principes de Sun Tzu intégrés (version simplifiée)
- **Terrain** : toujours pris en compte dans les combats et déplacements.
- **Moral** : facteur décisif dans la victoire.
- **Surprise** : chaque général peut tenter une manœuvre de flanc (probabilité d’efficacité).
- **Information incomplète** : les généraux n’ont pas accès à toute la carte.

---

## 7. Évolution prévue
- Ajout progressif de nouvelles caractéristiques :
  - Fatigue, logistique, ravitaillement.
  - Types d’unités (archers, cavalerie, artillerie).
  - Stratégies complexes (diversions, embuscades).
- Extension du moteur IA des généraux.
- Export des journaux de bataille pour analyse.

---

## 8. Prototype initial
- 2 nations, 1 général chacune.
- 1 armée de 100 unités par général.
- Terrain plat.
- Objectif : atteindre le camp adverse.
- Gestion des états : déplacement, combat, fuite.
