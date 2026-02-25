"""
Unit tests for birth-chart cache validation logic.

These tests exercise _is_valid_natal_cache and the BIRTH_CHART_SCHEMA_VERSION
constant in isolation, without requiring a running server or database.
"""

import sys
import os
import unittest

# ---------------------------------------------------------------------------
# Inline the validation logic here so the tests don't require the full
# server module (which needs live env-vars / MongoDB / etc.).
# The implementation below must stay in sync with backend/server.py.
# ---------------------------------------------------------------------------

BIRTH_CHART_SCHEMA_VERSION = 1


def _is_valid_natal_cache(chart: dict) -> bool:
    """Return True only when the cached chart matches the current schema version
    and contains the longitude-keyed planet structure expected by
    calculate_current_transits."""
    if not chart:
        return False
    if chart.get("schema_version") != BIRTH_CHART_SCHEMA_VERSION:
        return False
    planets = chart.get("planets")
    if not planets or not isinstance(planets, dict):
        return False
    for planet_data in planets.values():
        if not isinstance(planet_data, dict) or "longitude" not in planet_data:
            return False
    return True


# ---------------------------------------------------------------------------
# Helper to build a minimal valid planet entry
# ---------------------------------------------------------------------------
def _make_planet(longitude: float = 45.0) -> dict:
    return {
        "longitude": longitude,
        "latitude": 0.0,
        "speed": 1.0,
        "retrograde": False,
        "sign": "Taurus",
        "degree": 15.0,
        "formatted": "15° Taurus 0'",
    }


def _make_valid_chart() -> dict:
    return {
        "user_id": "user-abc",
        "schema_version": BIRTH_CHART_SCHEMA_VERSION,
        "planets": {
            "Sun": _make_planet(45.0),
            "Moon": _make_planet(120.0),
        },
        "computed_at": "2026-01-01T00:00:00+00:00",
    }


class TestIsValidNatalCache(unittest.TestCase):

    def test_valid_chart_passes(self):
        self.assertTrue(_is_valid_natal_cache(_make_valid_chart()))

    def test_none_is_invalid(self):
        self.assertFalse(_is_valid_natal_cache(None))

    def test_empty_dict_is_invalid(self):
        self.assertFalse(_is_valid_natal_cache({}))

    def test_missing_schema_version_is_invalid(self):
        chart = _make_valid_chart()
        del chart["schema_version"]
        self.assertFalse(_is_valid_natal_cache(chart))

    def test_wrong_schema_version_is_invalid(self):
        chart = _make_valid_chart()
        chart["schema_version"] = BIRTH_CHART_SCHEMA_VERSION - 1
        self.assertFalse(_is_valid_natal_cache(chart))

    def test_missing_planets_key_is_invalid(self):
        chart = _make_valid_chart()
        del chart["planets"]
        self.assertFalse(_is_valid_natal_cache(chart))

    def test_empty_planets_dict_is_invalid(self):
        chart = _make_valid_chart()
        chart["planets"] = {}
        self.assertFalse(_is_valid_natal_cache(chart))

    def test_planets_not_dict_is_invalid(self):
        chart = _make_valid_chart()
        chart["planets"] = ["Sun", "Moon"]
        self.assertFalse(_is_valid_natal_cache(chart))

    def test_planet_missing_longitude_is_invalid(self):
        chart = _make_valid_chart()
        bad_planet = _make_planet()
        del bad_planet["longitude"]
        chart["planets"]["Sun"] = bad_planet
        self.assertFalse(_is_valid_natal_cache(chart))

    def test_planet_entry_not_a_dict_is_invalid(self):
        chart = _make_valid_chart()
        chart["planets"]["Sun"] = 45.0  # old-style raw longitude value
        self.assertFalse(_is_valid_natal_cache(chart))


if __name__ == "__main__":
    unittest.main()
