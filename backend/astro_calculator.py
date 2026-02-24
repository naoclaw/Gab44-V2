"""
Swiss Ephemeris Astrology Calculator
Provides accurate planetary positions and house calculations for natal charts
"""
import swisseph as swe
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import math
import requests
import logging
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:
    from timezonefinder import TimezoneFinder as _TimezoneFinder
    _tf = _TimezoneFinder()
except ImportError:
    _tf = None
    logging.warning("timezonefinder not installed — birth times will be assumed UTC")

_NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
_NOMINATIM_USER_AGENT = "Gab44-Astrology/2.0"

# Success-only geocoding cache (avoids wiping all entries on transient failures)
_geocode_cache: Dict[str, Tuple[float, float]] = {}

# Initialize Swiss Ephemeris - use built-in ephemeris (Moshier, less accurate but no files needed)
swe.set_ephe_path('')

# Zodiac signs
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Planet constants
PLANETS = {
    swe.SUN: "sun",
    swe.MOON: "moon",
    swe.MERCURY: "mercury",
    swe.VENUS: "venus",
    swe.MARS: "mars",
    swe.JUPITER: "jupiter",
    swe.SATURN: "saturn",
    swe.URANUS: "uranus",
    swe.NEPTUNE: "neptune",
    swe.PLUTO: "pluto",
}

# Additional points — True Node is standard for natal charts
NORTH_NODE = swe.TRUE_NODE
CHIRON = swe.CHIRON

# Aspect definitions (degree, name, orb, harmony)
ASPECTS = [
    (0, "conjunction", 8, 0.9),
    (60, "sextile", 6, 0.8),
    (90, "square", 8, 0.4),
    (120, "trine", 8, 0.95),
    (180, "opposition", 8, 0.5),
]


def degree_to_sign(degree: float) -> Tuple[str, float, int]:
    """Convert ecliptic degree to sign, degree within sign, and house number"""
    sign_num = int(degree // 30)
    sign_degree = degree % 30
    return SIGNS[sign_num % 12], sign_degree, sign_num + 1


def parse_birth_datetime(birth_date: str, birth_time: Optional[str] = None) -> datetime:
    """Parse birth date and time strings into datetime object"""
    if birth_time:
        try:
            dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            dt = datetime.strptime(birth_date, "%Y-%m-%d")
            dt = dt.replace(hour=12)  # Default to noon if time parsing fails
    else:
        dt = datetime.strptime(birth_date, "%Y-%m-%d")
        dt = dt.replace(hour=12)  # Default to noon if no time provided
    return dt


def datetime_to_julian(dt: datetime) -> float:
    """Convert a UTC (or UT-equivalent) datetime to Julian Day number."""
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)


def local_to_utc(dt: datetime, latitude: float, longitude: float) -> datetime:
    """Convert a naive local birth datetime to UTC using the birth location's timezone.

    Falls back to treating the datetime as UTC when location is unavailable or
    timezone lookup fails (no data loss — just a known limitation).
    """
    if _tf is None or (latitude == 0.0 and longitude == 0.0):
        return dt  # No location data — treat as UTC
    try:
        tz_name = _tf.timezone_at(lat=latitude, lng=longitude)
        if not tz_name:
            return dt
        local_tz = ZoneInfo(tz_name)
        local_dt = dt.replace(tzinfo=local_tz)
        utc_dt = local_dt.astimezone(ZoneInfo("UTC"))
        return utc_dt.replace(tzinfo=None)  # Return naive UTC for swe.julday
    except (ZoneInfoNotFoundError, Exception) as exc:
        logging.warning("Timezone conversion failed for (%.4f, %.4f): %s", latitude, longitude, exc)
        return dt


def calculate_planetary_positions(jd: float) -> Dict[str, Dict]:
    """Calculate positions for all planets at given Julian Day"""
    positions = {}
    
    for planet_id, planet_name in PLANETS.items():
        try:
            # calc_ut returns (longitude, latitude, distance, speed_lon, speed_lat, speed_dist)
            result, flag = swe.calc_ut(jd, planet_id)
            longitude = result[0]
            sign, sign_degree, house = degree_to_sign(longitude)
            
            positions[planet_name] = {
                "degree": round(longitude, 2),
                "sign": sign,
                "sign_degree": round(sign_degree, 2),
                "retrograde": result[3] < 0,  # Negative speed = retrograde
                "speed": round(result[3], 4),   # degrees/day — needed for applying aspects
                "house": None  # Assigned later by assign_houses_to_planets
            }
        except Exception as e:
            print(f"Error calculating {planet_name}: {e}")
            continue
    
    # Calculate North Node (Rahu)
    try:
        result, flag = swe.calc_ut(jd, NORTH_NODE)
        longitude = result[0]
        sign, sign_degree, house = degree_to_sign(longitude)
        positions["north_node"] = {
            "degree": round(longitude, 2),
            "sign": sign,
            "sign_degree": round(sign_degree, 2),
            "house": None
        }
        # South Node (Ketu) is opposite
        south_lon = (longitude + 180) % 360
        south_sign, south_degree, south_house = degree_to_sign(south_lon)
        positions["south_node"] = {
            "degree": round(south_lon, 2),
            "sign": south_sign,
            "sign_degree": round(south_degree, 2),
            "house": None
        }
    except Exception as e:
        print(f"Error calculating nodes: {e}")
    
    # Calculate Chiron
    try:
        result, flag = swe.calc_ut(jd, CHIRON)
        longitude = result[0]
        sign, sign_degree, house = degree_to_sign(longitude)
        positions["chiron"] = {
            "degree": round(longitude, 2),
            "sign": sign,
            "sign_degree": round(sign_degree, 2),
            "house": None
        }
    except Exception as e:
        print(f"Error calculating Chiron: {e}")
    
    return positions


def calculate_houses(jd: float, latitude: float, longitude: float, house_system: str = 'P') -> Dict:
    """
    Calculate house cusps and angles (ASC, MC, etc.)
    House systems: P=Placidus, K=Koch, O=Porphyry, R=Regiomontanus, C=Campanus, E=Equal, W=Whole Sign
    """
    try:
        # swe.houses returns (cusps[12], ascmc[10])
        cusps, ascmc = swe.houses(jd, latitude, longitude, house_system.encode())
        
        # Extract key points
        asc_degree = ascmc[0]
        mc_degree = ascmc[1]
        
        asc_sign, asc_sign_degree, _ = degree_to_sign(asc_degree)
        mc_sign, mc_sign_degree, _ = degree_to_sign(mc_degree)
        
        # Calculate IC and DC
        ic_degree = (mc_degree + 180) % 360
        dc_degree = (asc_degree + 180) % 360
        ic_sign, ic_sign_degree, _ = degree_to_sign(ic_degree)
        dc_sign, dc_sign_degree, _ = degree_to_sign(dc_degree)
        
        houses = {}
        for i, cusp in enumerate(cusps):
            sign, sign_degree, _ = degree_to_sign(cusp)
            houses[str(i + 1)] = {
                "degree": round(cusp, 2),
                "sign": sign,
                "sign_degree": round(sign_degree, 2)
            }
        
        return {
            "cusps": houses,
            "ascendant": {
                "degree": round(asc_degree, 2),
                "sign": asc_sign,
                "sign_degree": round(asc_sign_degree, 2)
            },
            "midheaven": {
                "degree": round(mc_degree, 2),
                "sign": mc_sign,
                "sign_degree": round(mc_sign_degree, 2)
            },
            "descendant": {
                "degree": round(dc_degree, 2),
                "sign": dc_sign
            },
            "ic": {
                "degree": round(ic_degree, 2),
                "sign": ic_sign
            }
        }
    except Exception as e:
        print(f"Error calculating houses: {e}")
        return {}


def calculate_aspects(positions: Dict[str, Dict], orb_factor: float = 1.0) -> List[Dict]:
    """Calculate aspects between planets"""
    aspects = []
    planet_names = list(positions.keys())
    
    for i, p1_name in enumerate(planet_names):
        for p2_name in planet_names[i + 1:]:
            p1 = positions[p1_name]
            p2 = positions[p2_name]
            
            # Calculate angular difference
            diff = abs(p1["degree"] - p2["degree"])
            if diff > 180:
                diff = 360 - diff
            
            # Check against each aspect
            for aspect_angle, aspect_name, max_orb, harmony in ASPECTS:
                orb = abs(diff - aspect_angle)
                effective_orb = max_orb * orb_factor
                
                if orb <= effective_orb:
                    strength = 1 - (orb / effective_orb)
                    # Applying: project 1 hour ahead using each planet's speed
                    # If future orb is smaller the aspect is applying (converging)
                    p1_next = (p1["degree"] + p1.get("speed", 0) / 24) % 360
                    p2_next = (p2["degree"] + p2.get("speed", 0) / 24) % 360
                    future_diff = abs(p1_next - p2_next)
                    if future_diff > 180:
                        future_diff = 360 - future_diff
                    future_orb = abs(future_diff - aspect_angle)
                    aspects.append({
                        "planet1": p1_name,
                        "planet2": p2_name,
                        "aspect": aspect_name,
                        "orb": round(orb, 2),
                        "strength": round(strength, 2),
                        "harmony": harmony,
                        "applying": future_orb < orb
                    })
                    break
    
    # Sort by strength
    return sorted(aspects, key=lambda x: x["strength"], reverse=True)


def detect_patterns(aspects: List[Dict], positions: Dict[str, Dict]) -> List[str]:
    """Detect major chart patterns like Grand Trines, T-Squares, etc."""
    patterns = []
    
    # Group aspects by type
    trines = [a for a in aspects if a["aspect"] == "trine" and a["strength"] > 0.5]
    squares = [a for a in aspects if a["aspect"] == "square" and a["strength"] > 0.5]
    oppositions = [a for a in aspects if a["aspect"] == "opposition" and a["strength"] > 0.5]
    
    # Check for Grand Trine (3 planets in trine to each other)
    if len(trines) >= 3:
        trine_planets = set()
        for t in trines:
            trine_planets.add(t["planet1"])
            trine_planets.add(t["planet2"])
        
        # Check if any 3 planets form a closed trine
        for p1 in trine_planets:
            for p2 in trine_planets:
                for p3 in trine_planets:
                    if p1 != p2 and p2 != p3 and p1 != p3:
                        # Check if all three are in trine
                        has_all = (
                            any(t for t in trines if (t["planet1"] == p1 and t["planet2"] == p2) or (t["planet1"] == p2 and t["planet2"] == p1)) and
                            any(t for t in trines if (t["planet1"] == p2 and t["planet2"] == p3) or (t["planet1"] == p3 and t["planet2"] == p2)) and
                            any(t for t in trines if (t["planet1"] == p1 and t["planet2"] == p3) or (t["planet1"] == p3 and t["planet2"] == p1))
                        )
                        if has_all:
                            # Get element
                            element = get_element(positions[p1]["sign"])
                            if f"Grand Trine ({element})" not in patterns:
                                patterns.append(f"Grand Trine ({element})")
    
    # Check for T-Square (2 planets in opposition, both square to a third)
    for opp in oppositions:
        p1, p2 = opp["planet1"], opp["planet2"]
        for sq in squares:
            apex = None
            if sq["planet1"] in [p1, p2]:
                apex = sq["planet2"]
            elif sq["planet2"] in [p1, p2]:
                apex = sq["planet1"]
            
            if apex:
                # Check if apex squares both opposition planets
                other_sq = [s for s in squares if 
                           (s["planet1"] == apex or s["planet2"] == apex) and
                           s != sq]
                if any(s for s in other_sq if s["planet1"] in [p1, p2] or s["planet2"] in [p1, p2]):
                    pattern = f"T-Square (apex: {apex})"
                    if pattern not in patterns:
                        patterns.append(pattern)
    
    # Check for Stellium (3+ planets in same sign)
    sign_counts = {}
    for planet, data in positions.items():
        sign = data["sign"]
        if sign not in sign_counts:
            sign_counts[sign] = []
        sign_counts[sign].append(planet)
    
    for sign, planets in sign_counts.items():
        if len(planets) >= 3:
            patterns.append(f"Stellium in {sign}")
    
    return patterns


def get_element(sign: str) -> str:
    """Get the element for a zodiac sign"""
    elements = {
        "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
        "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
        "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
        "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"
    }
    return elements.get(sign, "Unknown")


def get_modality(sign: str) -> str:
    """Get the modality for a zodiac sign"""
    modalities = {
        "Aries": "Cardinal", "Cancer": "Cardinal", "Libra": "Cardinal", "Capricorn": "Cardinal",
        "Taurus": "Fixed", "Leo": "Fixed", "Scorpio": "Fixed", "Aquarius": "Fixed",
        "Gemini": "Mutable", "Virgo": "Mutable", "Sagittarius": "Mutable", "Pisces": "Mutable"
    }
    return modalities.get(sign, "Unknown")


def assign_houses_to_planets(positions: Dict[str, Dict], houses: Dict) -> Dict[str, Dict]:
    """Assign house placements to planets based on house cusps"""
    if not houses or "cusps" not in houses:
        return positions
    
    cusps = houses["cusps"]
    cusp_degrees = [cusps[str(i+1)]["degree"] for i in range(12)]
    
    for planet_name, planet_data in positions.items():
        planet_degree = planet_data["degree"]
        
        # Find which house the planet is in
        for i in range(12):
            cusp_start = cusp_degrees[i]
            cusp_end = cusp_degrees[(i + 1) % 12]
            
            # Handle wrap-around at 0 degrees
            if cusp_end < cusp_start:  # Crosses 0 Aries
                if planet_degree >= cusp_start or planet_degree < cusp_end:
                    positions[planet_name]["house"] = i + 1
                    break
            else:
                if cusp_start <= planet_degree < cusp_end:
                    positions[planet_name]["house"] = i + 1
                    break
    
    return positions


# ---------------------------------------------------------------------------
# Pythagorean Numerology Engine
# ---------------------------------------------------------------------------

# Pythagorean letter-to-digit mapping
_PYTH_MAP: Dict[str, int] = {
    'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9,
    'j': 1, 'k': 2, 'l': 3, 'm': 4, 'n': 5, 'o': 6, 'p': 7, 'q': 8, 'r': 9,
    's': 1, 't': 2, 'u': 3, 'v': 4, 'w': 5, 'x': 6, 'y': 7, 'z': 8,
}
_VOWELS = set('aeiou')

# Master numbers are never reduced further
_MASTER_NUMBERS = {11, 22, 33}

_NUMBER_MEANINGS: Dict[int, Dict[str, str]] = {
    1:  {"keyword": "Leadership",    "theme": "Independence, pioneering drive, original thinking"},
    2:  {"keyword": "Partnership",   "theme": "Diplomacy, intuition, cooperation, sensitivity"},
    3:  {"keyword": "Expression",    "theme": "Creativity, joy, communication, social magnetism"},
    4:  {"keyword": "Foundation",    "theme": "Hard work, discipline, stability, practical mastery"},
    5:  {"keyword": "Freedom",       "theme": "Adventure, adaptability, change, sensory experience"},
    6:  {"keyword": "Harmony",       "theme": "Nurturing, responsibility, beauty, domestic love"},
    7:  {"keyword": "Wisdom",        "theme": "Introspection, analysis, spiritual seeking, truth"},
    8:  {"keyword": "Abundance",     "theme": "Ambition, authority, material mastery, karma"},
    9:  {"keyword": "Completion",    "theme": "Compassion, universal love, humanitarian service"},
    11: {"keyword": "Illumination",  "theme": "Spiritual messenger, visionary insight, nervous intensity"},
    22: {"keyword": "Master Builder","theme": "Manifesting grand visions, disciplined idealism"},
    33: {"keyword": "Master Teacher","theme": "Selfless service, Christ-like compassion, healing"},
}


def _reduce(n: int, preserve_masters: bool = True) -> int:
    """Reduce n to a single digit, preserving master numbers when requested."""
    while n > 9 and (not preserve_masters or n not in _MASTER_NUMBERS):
        n = sum(int(d) for d in str(n))
    return n


def _name_to_digits(name: str) -> List[int]:
    """Convert alphabetic characters in a name to Pythagorean digits."""
    return [_PYTH_MAP[c] for c in name.lower() if c in _PYTH_MAP]


def _number_info(n: int) -> Dict[str, str]:
    return _NUMBER_MEANINGS.get(n, {"keyword": "Unknown", "theme": ""})


def calculate_numerology(name: str, birth_date: str) -> Dict:
    """
    Calculate a complete Pythagorean numerology profile.

    Args:
        name:       Full birth name (as on birth certificate for accuracy)
        birth_date: YYYY-MM-DD

    Returns:
        Dict with life_path, expression, soul_urge, personality, birthday,
        personal_year, first_name_number, last_name_number, and meanings.
    """
    # --- Life Path Number (from birth date) ---
    try:
        dt = datetime.strptime(birth_date, "%Y-%m-%d")
        # Reduce each component separately before summing (standard method)
        month_r = _reduce(dt.month)
        day_r = _reduce(dt.day)
        year_r = _reduce(sum(int(d) for d in str(dt.year)))
        life_path = _reduce(month_r + day_r + year_r)
        birthday_num = _reduce(dt.day)
    except ValueError:
        life_path = 0
        birthday_num = 0
        dt = None

    # --- Personal Year Number (changes each birthday) ---
    if dt:
        today = datetime.now()
        py_raw = _reduce(dt.month) + _reduce(dt.day) + _reduce(sum(int(d) for d in str(today.year)))
        personal_year = _reduce(py_raw)
    else:
        personal_year = 0

    # --- Name-based numbers ---
    name_clean = name.strip()
    all_digits  = _name_to_digits(name_clean)
    vowel_digits = [_PYTH_MAP[c] for c in name_clean.lower() if c in _VOWELS and c in _PYTH_MAP]
    cons_digits  = [_PYTH_MAP[c] for c in name_clean.lower() if c.isalpha() and c not in _VOWELS and c in _PYTH_MAP]

    expression   = _reduce(sum(all_digits))    if all_digits   else 0
    soul_urge    = _reduce(sum(vowel_digits))  if vowel_digits else 0
    personality  = _reduce(sum(cons_digits))   if cons_digits  else 0

    # First / Last name numbers (split on whitespace)
    parts = name_clean.split()
    first_name_num = _reduce(sum(_name_to_digits(parts[0])))  if parts       else 0
    last_name_num  = _reduce(sum(_name_to_digits(parts[-1]))) if len(parts) > 1 else first_name_num

    return {
        "life_path":        {"number": life_path,      **_number_info(life_path)},
        "expression":       {"number": expression,     **_number_info(expression)},
        "soul_urge":        {"number": soul_urge,      **_number_info(soul_urge)},
        "personality":      {"number": personality,    **_number_info(personality)},
        "birthday":         {"number": birthday_num,   **_number_info(birthday_num)},
        "personal_year":    {"number": personal_year,  **_number_info(personal_year)},
        "first_name":       {"number": first_name_num, **_number_info(first_name_num)},
        "last_name":        {"number": last_name_num,  **_number_info(last_name_num)},
    }


def calculate_natal_chart(
    birth_date: str,
    birth_time: Optional[str] = None,
    latitude: float = 0.0,
    longitude: float = 0.0
) -> Dict:
    """
    Calculate a complete natal chart
    
    Args:
        birth_date: Date in YYYY-MM-DD format
        birth_time: Time in HH:MM format (optional, defaults to noon)
        latitude: Birth location latitude in degrees
        longitude: Birth location longitude in degrees
    
    Returns:
        Complete chart data including planets, houses, aspects, and patterns
    """
    # Parse datetime; convert from local time at birth location to UTC
    dt = parse_birth_datetime(birth_date, birth_time)
    if latitude != 0.0 or longitude != 0.0:
        dt = local_to_utc(dt, latitude, longitude)
    jd = datetime_to_julian(dt)
    
    # Calculate planetary positions
    positions = calculate_planetary_positions(jd)
    
    # Calculate houses if we have coordinates
    houses = {}
    if latitude != 0.0 or longitude != 0.0:
        houses = calculate_houses(jd, latitude, longitude)
        positions = assign_houses_to_planets(positions, houses)
    
    # Calculate aspects
    aspects = calculate_aspects(positions)
    
    # Detect patterns
    patterns = detect_patterns(aspects, positions)
    
    # Get sun and moon signs for quick reference
    sun_sign = positions.get("sun", {}).get("sign", "Unknown")
    moon_sign = positions.get("moon", {}).get("sign", "Unknown")
    rising_sign = houses.get("ascendant", {}).get("sign", "Unknown") if houses else "Unknown"
    
    return {
        "sun_sign": sun_sign,
        "moon_sign": moon_sign,
        "rising_sign": rising_sign,
        "planets": positions,
        "houses": houses.get("cusps", {}),
        "ascendant": houses.get("ascendant", {}),
        "midheaven": houses.get("midheaven", {}),
        "aspects": aspects[:20],  # Top 20 aspects
        "patterns": patterns,
        "calculation_method": "Swiss Ephemeris",
        "julian_day": round(jd, 4)
    }


def calculate_current_transits(natal_positions: Dict[str, Dict]) -> List[Dict]:
    """Calculate current transits to natal chart"""
    now = datetime.now(timezone.utc)
    jd_now = datetime_to_julian(now)
    current_positions = calculate_planetary_positions(jd_now)
    
    transits = []
    
    # Check transits from outer planets to natal planets
    transit_planets = ["jupiter", "saturn", "uranus", "neptune", "pluto"]
    
    for transit_planet in transit_planets:
        if transit_planet not in current_positions:
            continue
        transit_pos = current_positions[transit_planet]
        
        for natal_planet, natal_pos in natal_positions.items():
            # Calculate aspect
            diff = abs(transit_pos["degree"] - natal_pos["degree"])
            if diff > 180:
                diff = 360 - diff
            
            for aspect_angle, aspect_name, max_orb, harmony in ASPECTS:
                orb = abs(diff - aspect_angle)
                if orb <= max_orb:
                    transits.append({
                        "transit_planet": transit_planet,
                        "natal_planet": natal_planet,
                        "aspect": aspect_name,
                        "orb": round(orb, 2),
                        "transit_sign": transit_pos["sign"],
                        "harmony": harmony
                    })
                    break
    
    return sorted(transits, key=lambda x: x["orb"])[:10]


# Geocoding helper - maps common cities to coordinates
CITY_COORDINATES = {
    "new york": (40.7128, -74.0060),
    "los angeles": (34.0522, -118.2437),
    "chicago": (41.8781, -87.6298),
    "london": (51.5074, -0.1278),
    "paris": (48.8566, 2.3522),
    "tokyo": (35.6762, 139.6503),
    "sydney": (-33.8688, 151.2093),
    "mumbai": (19.0760, 72.8777),
    "dubai": (25.2048, 55.2708),
    "berlin": (52.5200, 13.4050),
    "toronto": (43.6532, -79.3832),
    "vancouver": (49.2827, -123.1207),
    "moscow": (55.7558, 37.6173),
    "beijing": (39.9042, 116.4074),
    "singapore": (1.3521, 103.8198),
    "hong kong": (22.3193, 114.1694),
    "san francisco": (37.7749, -122.4194),
    "miami": (25.7617, -80.1918),
    "seattle": (47.6062, -122.3321),
    "boston": (42.3601, -71.0589),
    "atlanta": (33.7490, -84.3880),
    "denver": (39.7392, -104.9903),
    "phoenix": (33.4484, -112.0740),
    "houston": (29.7604, -95.3698),
    "dallas": (32.7767, -96.7970),
    "amsterdam": (52.3676, 4.9041),
    "rome": (41.9028, 12.4964),
    "madrid": (40.4168, -3.7038),
    "barcelona": (41.3851, 2.1734),
    "lisbon": (38.7223, -9.1393),
    "cairo": (30.0444, 31.2357),
    "cape town": (-33.9249, 18.4241),
    "melbourne": (-37.8136, 144.9631),
    "auckland": (-36.8485, 174.7633),
    "sao paulo": (-23.5505, -46.6333),
    "buenos aires": (-34.6037, -58.3816),
    "mexico city": (19.4326, -99.1332),
    # Morocco cities
    "casablanca": (33.5731, -7.5898),
    "rabat": (34.0209, -6.8416),
    "marrakech": (31.6295, -7.9811),
    "fez": (34.0181, -5.0078),
    "tangier": (35.7595, -5.8340),
    "agadir": (30.4278, -9.5981),
    "meknes": (33.8935, -5.5547),
    "oujda": (34.6867, -1.9114),
    "kenitra": (34.2610, -6.5802),
    "tetouan": (35.5889, -5.3626),
    "khemisset": (33.8242, -6.0662),
    "morocco": (31.7917, -7.0926),
    # More global cities
    "reading": (40.3356, -75.9269),  # Reading, PA
    "pennsylvania": (40.2732, -76.8867),
    "nashville": (36.1627, -86.7816),
    "las vegas": (36.1699, -115.1398),
    "portland": (45.5051, -122.6750),
    "austin": (30.2672, -97.7431),
    "san diego": (32.7157, -117.1611),
    "philadelphia": (39.9526, -75.1652),
    "detroit": (42.3314, -83.0458),
    "minneapolis": (44.9778, -93.2650),
    "tel aviv": (32.0853, 34.7818),
    "jerusalem": (31.7683, 35.2137),
    "stockholm": (59.3293, 18.0686),
    "oslo": (59.9139, 10.7522),
    "copenhagen": (55.6761, 12.5683),
    "helsinki": (60.1699, 24.9384),
    "vienna": (48.2082, 16.3738),
    "zurich": (47.3769, 8.5417),
    "geneva": (46.2044, 6.1432),
    "milan": (45.4642, 9.1900),
    "munich": (48.1351, 11.5820),
    "prague": (50.0755, 14.4378),
    "warsaw": (52.2297, 21.0122),
    "budapest": (47.4979, 19.0402),
    "athens": (37.9838, 23.7275),
    "istanbul": (41.0082, 28.9784),
    "bangkok": (13.7563, 100.5018),
    "kuala lumpur": (3.1390, 101.6869),
    "jakarta": (6.2088, 106.8456),
    "manila": (14.5995, 120.9842),
    "seoul": (37.5665, 126.9780),
    "taipei": (25.0330, 121.5654),
    "shanghai": (31.2304, 121.4737),
    "guangzhou": (23.1291, 113.2644),
    "shenzhen": (22.5431, 114.0579),
    "delhi": (28.7041, 77.1025),
    "bangalore": (12.9716, 77.5946),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "karachi": (24.8607, 67.0011),
    "lagos": (6.5244, 3.3792),
    "nairobi": (-1.2921, 36.8219),
    "johannesburg": (-26.2041, 28.0473),
}


def _geocode_nominatim(place: str) -> Tuple[float, float]:
    """Call OpenStreetMap Nominatim to look up coordinates for any place name.

    Only successful results are cached.  Transient failures return (0.0, 0.0)
    without caching so a retry on the next request is always possible.
    """
    if place in _geocode_cache:
        return _geocode_cache[place]
    try:
        response = requests.get(
            _NOMINATIM_URL,
            params={"q": place, "format": "json", "limit": 1},
            headers={"User-Agent": _NOMINATIM_USER_AGENT},
            timeout=5,
        )
        response.raise_for_status()
        results = response.json()
        if results:
            coords = (float(results[0]["lat"]), float(results[0]["lon"]))
            _geocode_cache[place] = coords  # Only cache successes
            return coords
        logging.warning("Nominatim returned no results for place: %r", place)
    except (requests.RequestException, ValueError, KeyError) as exc:
        logging.warning("Nominatim geocoding failed for %r: %s", place, exc)
    return (0.0, 0.0)


def get_coordinates(place: str) -> Tuple[float, float]:
    """Get coordinates for a place name.

    Fast-path: static lookup table of 90+ cities.
    Fallback: live Nominatim geocoding (cached per unique place string).
    Returns (0.0, 0.0) only when both sources fail.
    """
    place_lower = place.lower().strip()

    # Check direct match in static table
    if place_lower in CITY_COORDINATES:
        return CITY_COORDINATES[place_lower]

    # Check partial match in static table
    for city, coords in CITY_COORDINATES.items():
        if city in place_lower or place_lower in city:
            return coords

    # Live geocoding fallback via OpenStreetMap Nominatim
    return _geocode_nominatim(place.strip())
