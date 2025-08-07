# Checklist de nettoyage

Historique des améliorations techniques. Les tâches encore ouvertes sont aussi listées dans [todo.md](todo.md).

- [x] Permettre d'arrêter la propagation d'un évènement et ajouter des horodatages.
- [x] Utiliser `SchedulerSystem` pour planifier les mises à jour des nœuds lents (`NeedNode`, IA...).
- [x] Implémenter un `WeatherSystem` impactant la production et les comportements.
- [ ] Refactorer `AIBehaviorNode` :
  - [ ] Séparer planification, navigation et interactions économiques.
  - [ ] Utiliser une machine à états ou un arbre de comportement configurable.
  - [ ] Résoudre les références lors du chargement.
  - [ ] Paramétrer durées, vitesses et seuils via la configuration.
  - [x] Confier la cadence de mise à jour au `SchedulerSystem`.
- [x] Mettre en cache les distances ou introduire un index spatial.
- [x] Étendre `SimNode.serialize` pour inclure positions, inventaires et besoins.
- [x] Enrichir `EconomySystem` avec une économie dynamique.
- [x] Permettre la sérialisation complète et le rechargement de l'état du monde.
- [ ] Créer des outils de création (templates, validation de schéma, éditeur graphique).
- [ ] Enrichir la visualisation (zoom, caméra, mode web, 3D).
- [ ] Ajouter des mécaniques avancées (animaux, quêtes, combat, arbres de comportement).
- [ ] Mettre en place un CI/benchmark et versionnage des plugins.
- [ ] Améliorer la documentation, les tutoriels et préparer une marketplace communautaire.
