"""Common terrain tile codes and helpers."""
from __future__ import annotations

from typing import Dict

# Mapping between human readable terrain names and numeric codes used in grids.
TILE_CODES: Dict[str, int] = {
    "plain": 0,
    "forest": 1,
    "hill": 2,
    "water": 3,
    "mountain": 4,
    "swamp": 5,
    "desert": 6,
    "road": 7,
}

# Reverse lookup table
TILE_NAMES: Dict[int, str] = {code: name for name, code in TILE_CODES.items()}
