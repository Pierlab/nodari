# Échelle de la simulation

## Temps
- L'unité de base est la **seconde**.
- `TimeSystem` émet un évènement `tick` toutes les `tick_duration` secondes.
- Tous les paramètres de durée (`dt`, `start_time`, etc.) sont exprimés en secondes.

## Espace
- L'unité de base est le **mètre**.
- La conversion entre mètres et tuiles de terrain est définie par `METERS_PER_TILE` dans `core/terrain.py`.
- Conversion :
  - mètres vers tuiles : `tile = meter / METERS_PER_TILE`
  - tuiles vers mètres : `meter = tile * METERS_PER_TILE`

## Exemple
Si `METERS_PER_TILE = 1.0` et qu'une unité possède une vitesse de `2.0` m/s :

```python
unit.speed = 2.0          # mètres par seconde
dt = 3.0                  # secondes
# Déplacement en mètres
step = unit.speed * dt    # 6.0 m
# Conversion en tuiles
step_tiles = step / METERS_PER_TILE  # 6.0 tuiles
```

Cette convention garantit la cohérence entre les systèmes de mouvement, de
terrain et de rendu.
