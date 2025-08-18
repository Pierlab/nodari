"""Preset configurations for the war simulation."""
from __future__ import annotations

DEFAULT_SIM_PARAMS = {
    "dispersion": 200.0,
    "unit_size": 5,
    "soldiers_per_dot": 5,
    "bodyguard_size": 5,
    "vision_radius_m": 100.0,
    "movement_blocking": True,
}

RIVER_WIDTH_PRESETS = [(2, 5), (4, 8), (8, 14)]
MOUNTAIN_PRESETS = [
    {"total_area_pct": 5, "threshold": 0.75},
    {"total_area_pct": 10, "threshold": 0.65},
    {"total_area_pct": 20, "threshold": 0.55},
]
FOREST_LAYOUTS = [
    {"total_area_pct": 10, "clusters": 6, "cluster_spread": 0.6},
    {"total_area_pct": 30, "clusters": 2, "cluster_spread": 0.2},
]
