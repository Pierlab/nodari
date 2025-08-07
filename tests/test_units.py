from core.units import km_to_m, m_to_km, kmh_to_mps, mps_to_kmh, sqkm_to_sqm, sqm_to_sqkm


def test_distance_conversions():
    assert km_to_m(1.2) == 1200
    assert m_to_km(750) == 0.75


def test_speed_conversions():
    assert kmh_to_mps(36) == 10
    assert mps_to_kmh(10) == 36


def test_area_conversions():
    assert sqkm_to_sqm(2) == 2_000_000
    assert sqm_to_sqkm(50_000) == 0.05
