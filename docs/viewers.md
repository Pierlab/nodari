# Viewers

Ce projet propose deux moteurs d'affichage interchangeables:

## `PygameViewerSystem`
- Rendu logiciel basé sur Pygame.
- Compatible avec la majorité des systèmes mais limité par le CPU.
- Adapté pour le débogage et les configurations légères.

## `ModernGLViewerSystem`
- Utilise `moderngl` pour exploiter la carte graphique.
- Rendu plus fluide lorsqu'il y a beaucoup d'unités ou de terrains complexes.
- Démarrage légèrement plus long dû à l'initialisation d'OpenGL.

## Performances
- Pygame atteint environ 30–40 FPS sur des scènes denses.
- ModernGL peut dépasser 120 FPS sur le même matériel grâce à l'accélération GPU.

Le choix du backend se fait via l'option `--viewer` de `run_war.py`.
