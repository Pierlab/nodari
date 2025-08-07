"""Utility functions for distance and speed units."""
from __future__ import annotations

METERS_PER_KILOMETER = 1000.0
SECONDS_PER_HOUR = 3600.0


def km_to_m(km: float) -> float:
    """Convert kilometers to meters."""
    return km * METERS_PER_KILOMETER


def m_to_km(m: float) -> float:
    """Convert meters to kilometers."""
    return m / METERS_PER_KILOMETER


def kmh_to_mps(kmh: float) -> float:
    """Convert kilometers per hour to meters per second."""
    return kmh * METERS_PER_KILOMETER / SECONDS_PER_HOUR


def mps_to_kmh(mps: float) -> float:
    """Convert meters per second to kilometers per hour."""
    return mps * SECONDS_PER_HOUR / METERS_PER_KILOMETER


def sqkm_to_sqm(km2: float) -> float:
    """Convert square kilometers to square meters."""
    return km2 * (METERS_PER_KILOMETER ** 2)


def sqm_to_sqkm(m2: float) -> float:
    """Convert square meters to square kilometers."""
    return m2 / (METERS_PER_KILOMETER ** 2)
