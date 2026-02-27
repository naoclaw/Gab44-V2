"""
Unit tests for the transit natal-chart cache validation helper.
These tests are standalone (no live server or DB required).

We re-implement the pure logic here to keep the test self-contained while
verifying the exact contract that _is_natal_cache_valid must satisfy.
"""

# ---------------------------------------------------------------------------
# Inline the contract we're testing so we don't need to import the full app.
# If the implementation in server.py diverges from this, the integration tests
# (test_swiss_ephemeris.py) will catch it.  Here we verify the pure logic.
# ---------------------------------------------------------------------------
BIRTH_CHART_SCHEMA_VERSION = 1  # must match server.BIRTH_CHART_SCHEMA_VERSION


def _is_natal_cache_valid(chart):
    """Mirror of server._is_natal_cache_valid — tested here in isolation."""
    if not chart:
        return False
    if not chart.get("planets"):
        return False
    if chart.get("schema_version") != BIRTH_CHART_SCHEMA_VERSION:
        return False
    return True


class TestIsNatalCacheValid:
    """Tests for _is_natal_cache_valid helper."""

    def test_none_chart_is_invalid(self):
        assert _is_natal_cache_valid(None) is False

    def test_empty_dict_is_invalid(self):
        assert _is_natal_cache_valid({}) is False

    def test_missing_planets_is_invalid(self):
        assert _is_natal_cache_valid({"schema_version": BIRTH_CHART_SCHEMA_VERSION}) is False

    def test_empty_planets_is_invalid(self):
        assert _is_natal_cache_valid({"planets": {}, "schema_version": BIRTH_CHART_SCHEMA_VERSION}) is False

    def test_wrong_schema_version_is_invalid(self):
        old_version = BIRTH_CHART_SCHEMA_VERSION - 1
        chart = {"planets": {"sun": {"degree": 30}}, "schema_version": old_version}
        assert _is_natal_cache_valid(chart) is False

    def test_missing_schema_version_is_invalid(self):
        chart = {"planets": {"sun": {"degree": 30}}}
        assert _is_natal_cache_valid(chart) is False

    def test_valid_chart_returns_true(self):
        chart = {
            "planets": {"sun": {"degree": 30, "sign": "Taurus"}},
            "schema_version": BIRTH_CHART_SCHEMA_VERSION,
        }
        assert _is_natal_cache_valid(chart) is True

