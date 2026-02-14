"""
Swiss Ephemeris Integration Tests
Tests for accurate planetary positions, house calculations, aspects, patterns, and transits
"""
import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
TEST_CREDENTIALS = {
    "email": "nchobah@gmail.com",
    "password": "admin123"
}

# Expected values for user nchobah@gmail.com (birth: 1994-04-23, Khemisset, Morocco)
EXPECTED_USER_DATA = {
    "birth_date": "1994-04-23",
    "birth_place": "khemisset",
    "sun_sign": "Taurus",
    "moon_sign": "Virgo",
    "rising_sign": "Taurus"
}

@pytest.fixture(scope="module")
def auth_token():
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=TEST_CREDENTIALS
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture(scope="module")
def user_chart(auth_token):
    """Get user's birth chart with Swiss Ephemeris (force recalculate)"""
    response = requests.get(
        f"{BASE_URL}/api/chart/me?recalculate=true",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200, f"Chart fetch failed: {response.text}"
    return response.json()


class TestSwissEphemerisChart:
    """Tests for Swiss Ephemeris chart calculations"""
    
    def test_calculation_method_is_swiss_ephemeris(self, user_chart):
        """Verify chart uses Swiss Ephemeris calculation"""
        assert user_chart.get("calculation_method") == "Swiss Ephemeris"
        print(f"✓ Calculation method: {user_chart.get('calculation_method')}")
    
    def test_sun_sign_accurate(self, user_chart):
        """Verify Sun sign is accurately calculated"""
        assert user_chart.get("sun_sign") == EXPECTED_USER_DATA["sun_sign"]
        print(f"✓ Sun sign: {user_chart.get('sun_sign')} (expected: {EXPECTED_USER_DATA['sun_sign']})")
    
    def test_moon_sign_accurate(self, user_chart):
        """Verify Moon sign is accurately calculated"""
        assert user_chart.get("moon_sign") == EXPECTED_USER_DATA["moon_sign"]
        print(f"✓ Moon sign: {user_chart.get('moon_sign')} (expected: {EXPECTED_USER_DATA['moon_sign']})")
    
    def test_rising_sign_accurate(self, user_chart):
        """Verify Rising sign is accurately calculated"""
        assert user_chart.get("rising_sign") == EXPECTED_USER_DATA["rising_sign"]
        print(f"✓ Rising sign: {user_chart.get('rising_sign')} (expected: {EXPECTED_USER_DATA['rising_sign']})")
    
    def test_julian_day_calculated(self, user_chart):
        """Verify Julian Day is present"""
        julian_day = user_chart.get("julian_day")
        assert julian_day is not None
        assert isinstance(julian_day, (int, float))
        assert julian_day > 2449000  # Should be after 1993
        print(f"✓ Julian Day: {julian_day}")
    
    def test_all_planets_present(self, user_chart):
        """Verify all planets are calculated"""
        planets = user_chart.get("planets", {})
        expected_planets = ["sun", "moon", "mercury", "venus", "mars", 
                          "jupiter", "saturn", "uranus", "neptune", "pluto"]
        for planet in expected_planets:
            assert planet in planets, f"Missing planet: {planet}"
        print(f"✓ All {len(expected_planets)} planets present")
    
    def test_planets_have_required_fields(self, user_chart):
        """Verify planets have sign, degree, sign_degree, and house"""
        planets = user_chart.get("planets", {})
        for planet_name, data in planets.items():
            assert "sign" in data, f"{planet_name} missing sign"
            assert "degree" in data, f"{planet_name} missing degree"
            assert "sign_degree" in data, f"{planet_name} missing sign_degree"
            assert "house" in data, f"{planet_name} missing house"
            
            # Validate ranges
            assert 0 <= data["degree"] <= 360, f"{planet_name} degree out of range"
            assert 0 <= data["sign_degree"] <= 30, f"{planet_name} sign_degree out of range"
            assert 1 <= data["house"] <= 12, f"{planet_name} house out of range"
        print(f"✓ All planets have required fields with valid ranges")
    
    def test_additional_points_present(self, user_chart):
        """Verify North Node, South Node, and Chiron are calculated"""
        planets = user_chart.get("planets", {})
        assert "north_node" in planets, "Missing North Node"
        assert "south_node" in planets, "Missing South Node"
        assert "chiron" in planets, "Missing Chiron"
        print(f"✓ Additional points (nodes, chiron) present")
    
    def test_nodes_are_opposite(self, user_chart):
        """Verify North and South nodes are exactly opposite"""
        planets = user_chart.get("planets", {})
        north_degree = planets.get("north_node", {}).get("degree", 0)
        south_degree = planets.get("south_node", {}).get("degree", 0)
        
        # Should be exactly 180 degrees apart
        diff = abs(north_degree - south_degree)
        if diff > 180:
            diff = 360 - diff
        assert abs(diff - 180) < 0.1, f"Nodes not opposite: {north_degree} vs {south_degree}"
        print(f"✓ Nodes are opposite: N {north_degree}° vs S {south_degree}°")


class TestHouseCusps:
    """Tests for Placidus house system calculations"""
    
    def test_houses_present(self, user_chart):
        """Verify 12 houses are present"""
        houses = user_chart.get("houses", {})
        assert len(houses) == 12, f"Expected 12 houses, got {len(houses)}"
        print(f"✓ All 12 houses present")
    
    def test_houses_have_required_fields(self, user_chart):
        """Verify houses have degree, sign, sign_degree"""
        houses = user_chart.get("houses", {})
        for house_num, data in houses.items():
            assert isinstance(data, dict), f"House {house_num} should be object"
            assert "sign" in data, f"House {house_num} missing sign"
            assert "degree" in data, f"House {house_num} missing degree"
            assert "sign_degree" in data, f"House {house_num} missing sign_degree"
        print(f"✓ All houses have required fields")
    
    def test_first_house_matches_ascendant(self, user_chart):
        """Verify House 1 cusp equals Ascendant"""
        houses = user_chart.get("houses", {})
        ascendant = user_chart.get("ascendant", {})
        
        house1 = houses.get("1", {})
        assert house1.get("sign") == ascendant.get("sign"), "House 1 sign should match Ascendant"
        assert abs(house1.get("degree", 0) - ascendant.get("degree", 0)) < 0.1, "House 1 degree should match Ascendant"
        print(f"✓ House 1 ({house1.get('sign')}) matches Ascendant ({ascendant.get('sign')})")
    
    def test_ascendant_present(self, user_chart):
        """Verify Ascendant data is present"""
        ascendant = user_chart.get("ascendant", {})
        assert "sign" in ascendant
        assert "degree" in ascendant
        assert "sign_degree" in ascendant
        print(f"✓ Ascendant: {ascendant.get('sign')} {ascendant.get('sign_degree')}°")
    
    def test_midheaven_present(self, user_chart):
        """Verify Midheaven (MC) data is present"""
        midheaven = user_chart.get("midheaven", {})
        assert "sign" in midheaven
        assert "degree" in midheaven
        print(f"✓ Midheaven: {midheaven.get('sign')} {midheaven.get('sign_degree', '?')}°")


class TestAspects:
    """Tests for aspect calculations"""
    
    def test_aspects_present(self, user_chart):
        """Verify aspects are calculated"""
        aspects = user_chart.get("aspects", [])
        assert len(aspects) > 0, "No aspects found"
        print(f"✓ Found {len(aspects)} aspects")
    
    def test_aspects_have_required_fields(self, user_chart):
        """Verify aspects have all required fields"""
        aspects = user_chart.get("aspects", [])
        for aspect in aspects[:10]:  # Check first 10
            assert "planet1" in aspect, "Missing planet1"
            assert "planet2" in aspect, "Missing planet2"
            assert "aspect" in aspect, "Missing aspect type"
            assert "orb" in aspect, "Missing orb"
            assert "strength" in aspect, "Missing strength"
        print(f"✓ Aspects have required fields")
    
    def test_aspect_types_valid(self, user_chart):
        """Verify aspect types are valid"""
        aspects = user_chart.get("aspects", [])
        valid_types = ["conjunction", "sextile", "square", "trine", "opposition"]
        for aspect in aspects:
            assert aspect.get("aspect") in valid_types, f"Invalid aspect: {aspect.get('aspect')}"
        print(f"✓ All aspect types valid")
    
    def test_grand_trine_detected(self, user_chart):
        """Verify Grand Trine pattern is detected for Earth signs"""
        patterns = user_chart.get("patterns", [])
        # User has Moon in Virgo, Venus in Taurus, Uranus in Capricorn - all Earth
        grand_trines = [p for p in patterns if "Grand Trine" in p]
        assert len(grand_trines) > 0, "Grand Trine should be detected"
        print(f"✓ Grand Trine detected: {grand_trines}")
    
    def test_stellium_detected(self, user_chart):
        """Verify Stellium patterns are detected"""
        patterns = user_chart.get("patterns", [])
        stelliums = [p for p in patterns if "Stellium" in p]
        # User should have Stellium in Taurus (Sun, Venus, Ascendant)
        assert len(stelliums) > 0, "At least one stellium should be detected"
        print(f"✓ Stelliums detected: {stelliums}")


class TestTransits:
    """Tests for current transit calculations"""
    
    def test_transits_endpoint_works(self, auth_token):
        """Verify transits endpoint returns data"""
        response = requests.get(
            f"{BASE_URL}/api/transits/upcoming",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200, f"Transits failed: {response.text}"
        transits = response.json()
        assert len(transits) > 0, "No transits returned"
        print(f"✓ Transits endpoint returned {len(transits)} transits")
    
    def test_transits_have_required_fields(self, auth_token):
        """Verify transits have all required fields"""
        response = requests.get(
            f"{BASE_URL}/api/transits/upcoming",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        transits = response.json()
        
        for transit in transits[:5]:
            assert "transit_type" in transit, "Missing transit_type"
            assert "planet" in transit, "Missing planet"
            assert "aspect" in transit, "Missing aspect"
            assert "natal_planet" in transit, "Missing natal_planet"
            assert "interpretation" in transit, "Missing interpretation"
            assert "orb" in transit, "Missing orb"
            assert "strength" in transit, "Missing strength"
        print(f"✓ Transits have all required fields")
    
    def test_transits_from_outer_planets(self, auth_token):
        """Verify transits are from outer planets"""
        response = requests.get(
            f"{BASE_URL}/api/transits/upcoming",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        transits = response.json()
        
        outer_planets = ["jupiter", "saturn", "uranus", "neptune", "pluto"]
        for transit in transits:
            planet = transit.get("planet", "").lower()
            if planet != "general":
                assert planet in outer_planets, f"Transit from non-outer planet: {planet}"
        print(f"✓ Transits are from outer planets")
    
    def test_transits_have_sign_info(self, auth_token):
        """Verify transits include sign information"""
        response = requests.get(
            f"{BASE_URL}/api/transits/upcoming",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        transits = response.json()
        
        for transit in transits[:5]:
            if transit.get("planet") != "General":
                assert "transit_sign" in transit, f"Missing transit_sign for {transit.get('planet')}"
        print(f"✓ Transits include sign information")


class TestCoordinatesLookup:
    """Tests for city coordinates lookup"""
    
    def test_khemisset_coordinates(self):
        """Verify Khemisset, Morocco coordinates are correct"""
        # Import from backend
        import sys
        sys.path.insert(0, '/app/backend')
        from astro_calculator import get_coordinates
        
        coords = get_coordinates("khemisset")
        assert coords == (33.8242, -6.0662), f"Wrong coords for Khemisset: {coords}"
        print(f"✓ Khemisset coordinates: {coords}")
    
    def test_partial_match_works(self):
        """Verify partial city name matching works"""
        import sys
        sys.path.insert(0, '/app/backend')
        from astro_calculator import get_coordinates
        
        # Should still find khemisset with full location
        coords = get_coordinates("khemisset, morocco")
        assert coords[0] != 0.0 and coords[1] != 0.0, "Partial match should work"
        print(f"✓ Partial match works: khemisset, morocco -> {coords}")
    
    def test_unknown_city_returns_default(self):
        """Verify unknown cities return (0.0, 0.0)"""
        import sys
        sys.path.insert(0, '/app/backend')
        from astro_calculator import get_coordinates
        
        coords = get_coordinates("unknown_city_xyz_123")
        assert coords == (0.0, 0.0), f"Unknown city should return (0.0, 0.0), got {coords}"
        print(f"✓ Unknown city returns default: {coords}")


class TestCompatibilitySwissEphemeris:
    """Tests for compatibility using Swiss Ephemeris"""
    
    def test_compatibility_uses_swiss_ephemeris(self, auth_token):
        """Verify compatibility calculates both charts with Swiss Ephemeris"""
        response = requests.post(
            f"{BASE_URL}/api/compatibility/analyze",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "partner_name": "TEST_SwissEphemeris_Partner",
                "partner_birth_date": "1992-08-15",  # Should be Leo
                "partner_birth_time": "14:00",
                "partner_birth_place": "London"
            }
        )
        assert response.status_code == 200, f"Compatibility failed: {response.text}"
        data = response.json()
        
        # Partner should have accurate sun sign
        assert data.get("partner_sun_sign") == "Leo", f"Wrong sun sign: {data.get('partner_sun_sign')}"
        print(f"✓ Partner sun sign calculated correctly: {data.get('partner_sun_sign')}")
    
    def test_synastry_aspects_calculated(self, auth_token):
        """Verify synastry aspects are calculated from real positions"""
        response = requests.post(
            f"{BASE_URL}/api/compatibility/analyze",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "partner_name": "TEST_Synastry_Partner",
                "partner_birth_date": "1990-12-25",
                "partner_birth_time": "09:00",
                "partner_birth_place": "New York"
            }
        )
        data = response.json()
        
        aspects = data.get("synastry_aspects", [])
        assert len(aspects) > 0, "No synastry aspects calculated"
        
        for aspect in aspects[:5]:
            assert "person1_planet" in aspect
            assert "person2_planet" in aspect
            assert "aspect_type" in aspect
            assert "orb" in aspect
        print(f"✓ {len(aspects)} synastry aspects calculated")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
