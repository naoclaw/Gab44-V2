"""
Gab44 Astrology Engine
=======================
Swiss Ephemeris wrapper for real natal chart and transit calculations.

Uses pyswisseph (Swiss Ephemeris) with the built-in Moshier ephemeris
for planetary positions, house cusps, and aspect calculations.
"""

import swisseph as swe
from datetime import datetime, timezone, timedelta
import math

# Use built-in Moshier ephemeris (no external data files needed)
swe.set_ephe_path("")

# ============== Constants ==============

PLANETS = [
    (swe.SUN, "Sun"),
    (swe.MOON, "Moon"),
    (swe.MERCURY, "Mercury"),
    (swe.VENUS, "Venus"),
    (swe.MARS, "Mars"),
    (swe.JUPITER, "Jupiter"),
    (swe.SATURN, "Saturn"),
    (swe.URANUS, "Uranus"),
    (swe.NEPTUNE, "Neptune"),
    (swe.PLUTO, "Pluto"),
]

# True North Node (Mean Node)
NODE_ID = swe.MEAN_NODE

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

ELEMENTS = {
    "Aries": "Fire", "Taurus": "Earth", "Gemini": "Air", "Cancer": "Water",
    "Leo": "Fire", "Virgo": "Earth", "Libra": "Air", "Scorpio": "Water",
    "Sagittarius": "Fire", "Capricorn": "Earth", "Aquarius": "Air", "Pisces": "Water",
}

MODALITIES = {
    "Aries": "Cardinal", "Taurus": "Fixed", "Gemini": "Mutable",
    "Cancer": "Cardinal", "Leo": "Fixed", "Virgo": "Mutable",
    "Libra": "Cardinal", "Scorpio": "Fixed", "Sagittarius": "Mutable",
    "Capricorn": "Cardinal", "Aquarius": "Fixed", "Pisces": "Mutable",
}

# Major aspects with orbs (in degrees)
ASPECTS = {
    "Conjunction": {"angle": 0, "orb": 8, "type": "major"},
    "Opposition": {"angle": 180, "orb": 8, "type": "major"},
    "Trine": {"angle": 120, "orb": 8, "type": "major"},
    "Square": {"angle": 90, "orb": 7, "type": "major"},
    "Sextile": {"angle": 60, "orb": 6, "type": "major"},
    "Quincunx": {"angle": 150, "orb": 3, "type": "minor"},
    "Semi-Sextile": {"angle": 30, "orb": 2, "type": "minor"},
}

HOUSE_MEANINGS = {
    1: "Self & Identity",
    2: "Values & Resources",
    3: "Communication & Learning",
    4: "Home & Family",
    5: "Creativity & Romance",
    6: "Health & Service",
    7: "Partnerships & Marriage",
    8: "Transformation & Shared Resources",
    9: "Philosophy & Travel",
    10: "Career & Public Image",
    11: "Community & Aspirations",
    12: "Spirituality & Unconscious",
}


# ============== Helper Functions ==============

def longitude_to_sign(longitude: float) -> str:
    """Convert ecliptic longitude to zodiac sign."""
    idx = int(longitude / 30) % 12
    return ZODIAC_SIGNS[idx]


def longitude_to_degree_in_sign(longitude: float) -> float:
    """Convert ecliptic longitude to degree within its sign (0-30)."""
    return longitude % 30


def format_position(longitude: float) -> str:
    """Format longitude as '15° Aries 23\\'."""
    sign = longitude_to_sign(longitude)
    deg_in_sign = longitude_to_degree_in_sign(longitude)
    degrees = int(deg_in_sign)
    minutes = int((deg_in_sign - degrees) * 60)
    return f"{degrees}° {sign} {minutes}'"


def find_house(longitude: float, cusps: list) -> int:
    """Determine which house a planet falls in given house cusps."""
    for i in range(12):
        cusp_start = cusps[i]
        cusp_end = cusps[(i + 1) % 12]

        if cusp_start < cusp_end:
            if cusp_start <= longitude < cusp_end:
                return i + 1
        else:
            # Wraps around 0°
            if longitude >= cusp_start or longitude < cusp_end:
                return i + 1

    return 1  # Fallback


def angle_diff(a: float, b: float) -> float:
    """Calculate the smallest angular difference between two longitudes."""
    diff = abs(a - b) % 360
    return min(diff, 360 - diff)


# ============== Core Calculations ==============

def calculate_planet_positions(jd: float):
    """
    Calculate positions for all planets at a given Julian Day.
    Returns dict: { "Sun": {"longitude": ..., "sign": ..., ...}, ... }
    """
    positions = {}

    for planet_id, planet_name in PLANETS:
        result = swe.calc_ut(jd, planet_id)
        longitude = result[0][0]
        latitude = result[0][1]
        speed = result[0][3]

        positions[planet_name] = {
            "longitude": round(longitude, 4),
            "latitude": round(latitude, 4),
            "speed": round(speed, 4),
            "sign": longitude_to_sign(longitude),
            "degree_in_sign": round(longitude_to_degree_in_sign(longitude), 2),
            "formatted": format_position(longitude),
            "retrograde": speed < 0,
        }

    # North Node
    node_result = swe.calc_ut(jd, NODE_ID)
    node_lng = node_result[0][0]
    positions["North Node"] = {
        "longitude": round(node_lng, 4),
        "latitude": 0.0,
        "speed": round(node_result[0][3], 4),
        "sign": longitude_to_sign(node_lng),
        "degree_in_sign": round(longitude_to_degree_in_sign(node_lng), 2),
        "formatted": format_position(node_lng),
        "retrograde": True,  # North Node is always retrograde in mean calculation
    }

    return positions


def calculate_houses(jd: float, latitude: float, longitude: float, system: str = "P"):
    """
    Calculate house cusps using Placidus (default) or other systems.
    Returns dict: { 1: {"cusp": ..., "sign": ...}, ... }
    """
    cusps, ascmc = swe.houses(jd, latitude, longitude, system.encode())

    houses = {}
    for i in range(12):
        cusp_lng = cusps[i]
        houses[i + 1] = {
            "cusp": round(cusp_lng, 4),
            "sign": longitude_to_sign(cusp_lng),
            "degree": round(longitude_to_degree_in_sign(cusp_lng), 2),
            "formatted": format_position(cusp_lng),
            "meaning": HOUSE_MEANINGS.get(i + 1, ""),
        }

    # Ascendant and Midheaven from ascmc
    houses["ascendant"] = {
        "longitude": round(ascmc[0], 4),
        "sign": longitude_to_sign(ascmc[0]),
        "formatted": format_position(ascmc[0]),
    }
    houses["midheaven"] = {
        "longitude": round(ascmc[1], 4),
        "sign": longitude_to_sign(ascmc[1]),
        "formatted": format_position(ascmc[1]),
    }

    return houses, [cusps[i] for i in range(12)]


def calculate_aspects(positions: dict) -> list:
    """
    Calculate aspects between all planet pairs.
    Returns list of aspect dicts.
    """
    aspects = []
    planet_names = list(positions.keys())

    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            p1_name = planet_names[i]
            p2_name = planet_names[j]
            p1_lng = positions[p1_name]["longitude"]
            p2_lng = positions[p2_name]["longitude"]

            diff = angle_diff(p1_lng, p2_lng)

            for aspect_name, aspect_info in ASPECTS.items():
                orb = abs(diff - aspect_info["angle"])
                if orb <= aspect_info["orb"]:
                    aspects.append({
                        "planet1": p1_name,
                        "planet2": p2_name,
                        "aspect": aspect_name,
                        "angle": aspect_info["angle"],
                        "orb": round(orb, 2),
                        "type": aspect_info["type"],
                        "strength": round(1 - (orb / aspect_info["orb"]), 2),
                    })

    # Sort by strength
    aspects.sort(key=lambda a: a["strength"], reverse=True)
    return aspects


def detect_patterns(positions: dict, aspects: list) -> list:
    """Detect chart patterns like stelliums, grand trines, T-squares."""
    patterns = []

    # Stellium detection: 3+ planets in the same sign
    sign_counts = {}
    for name, pos in positions.items():
        sign = pos["sign"]
        if sign not in sign_counts:
            sign_counts[sign] = []
        sign_counts[sign].append(name)

    for sign, planets in sign_counts.items():
        if len(planets) >= 3:
            patterns.append(f"Stellium in {sign}: {', '.join(planets)}")

    # Element dominance
    element_counts = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    for name, pos in positions.items():
        if name == "North Node":
            continue
        element = ELEMENTS.get(pos["sign"], "")
        if element:
            element_counts[element] += 1

    dominant = max(element_counts, key=element_counts.get)
    if element_counts[dominant] >= 4:
        patterns.append(f"Strong {dominant} element dominance ({element_counts[dominant]} planets)")

    # Modality dominance
    modality_counts = {"Cardinal": 0, "Fixed": 0, "Mutable": 0}
    for name, pos in positions.items():
        if name == "North Node":
            continue
        modality = MODALITIES.get(pos["sign"], "")
        if modality:
            modality_counts[modality] += 1

    dominant_mod = max(modality_counts, key=modality_counts.get)
    if modality_counts[dominant_mod] >= 4:
        patterns.append(f"Strong {dominant_mod} modality ({modality_counts[dominant_mod]} planets)")

    # Grand Trine detection (simplified)
    trines = [a for a in aspects if a["aspect"] == "Trine" and a["strength"] > 0.5]
    trine_planets = set()
    for t in trines:
        trine_planets.add(t["planet1"])
        trine_planets.add(t["planet2"])
    if len(trine_planets) >= 3:
        # Check if 3 planets form a triangle of trines
        for p1 in trine_planets:
            for p2 in trine_planets:
                for p3 in trine_planets:
                    if p1 < p2 < p3:
                        has_t12 = any(
                            t for t in trines
                            if (t["planet1"] == p1 and t["planet2"] == p2)
                            or (t["planet1"] == p2 and t["planet2"] == p1)
                        )
                        has_t23 = any(
                            t for t in trines
                            if (t["planet1"] == p2 and t["planet2"] == p3)
                            or (t["planet1"] == p3 and t["planet2"] == p2)
                        )
                        has_t13 = any(
                            t for t in trines
                            if (t["planet1"] == p1 and t["planet2"] == p3)
                            or (t["planet1"] == p3 and t["planet2"] == p1)
                        )
                        if has_t12 and has_t23 and has_t13:
                            patterns.append(f"Grand Trine: {p1}, {p2}, {p3}")

    # T-Square detection (simplified)
    squares = [a for a in aspects if a["aspect"] == "Square" and a["strength"] > 0.5]
    oppositions = [a for a in aspects if a["aspect"] == "Opposition" and a["strength"] > 0.5]
    for opp in oppositions:
        for sq1 in squares:
            for sq2 in squares:
                apex = None
                if sq1["planet1"] == sq2["planet1"] and sq1["planet1"] not in [opp["planet1"], opp["planet2"]]:
                    if set([sq1["planet2"], sq2["planet2"]]) == set([opp["planet1"], opp["planet2"]]):
                        apex = sq1["planet1"]
                if apex:
                    patterns.append(f"T-Square: {opp['planet1']} opposite {opp['planet2']}, apex {apex}")

    return patterns


# ============== Main Entry Points ==============

def calculate_natal_chart(
    birth_date: str,
    birth_time: str = None,
    latitude: float = None,
    longitude: float = None,
) -> dict:
    """
    Calculate a complete natal chart.

    Parameters:
        birth_date: "YYYY-MM-DD"
        birth_time: "HH:MM" (optional — if None, noon is used)
        latitude: Birth location latitude (optional)
        longitude: Birth location longitude (optional)

    Returns a dict with planets, houses, aspects, and patterns.
    """
    # Parse date/time
    dt = datetime.strptime(birth_date, "%Y-%m-%d")

    hour = 12.0  # Default to noon if no birth time
    if birth_time and birth_time.strip():
        try:
            parts = birth_time.strip().split(":")
            hour = int(parts[0]) + int(parts[1]) / 60.0
            if len(parts) > 2:
                hour += int(parts[2]) / 3600.0
        except (ValueError, IndexError):
            hour = 12.0

    # Calculate Julian Day (UTC assumed — timezone conversion is a TODO)
    jd = swe.julday(dt.year, dt.month, dt.day, hour)

    # Planetary positions
    positions = calculate_planet_positions(jd)

    # Houses (only if we have coordinates)
    houses = {}
    cusp_list = None
    has_location = latitude is not None and longitude is not None
    if has_location:
        houses, cusp_list = calculate_houses(jd, latitude, longitude)

        # Add house placement to each planet
        for name, pos in positions.items():
            pos["house"] = find_house(pos["longitude"], cusp_list)

    # Aspects
    aspects = calculate_aspects(positions)

    # Patterns
    patterns = detect_patterns(positions, aspects)

    return {
        "planets": positions,
        "houses": houses,
        "aspects": aspects,
        "patterns": patterns,
        "has_birth_time": birth_time is not None and birth_time != "",
        "has_birth_location": has_location,
        "julian_day": jd,
    }


def calculate_current_transits(
    natal_positions: dict,
    natal_date: str = None,
) -> list:
    """
    Calculate current planetary transits relative to natal positions.

    Returns a list of active transit activations.
    """
    now = datetime.now(timezone.utc)
    jd_now = swe.julday(now.year, now.month, now.day, now.hour + now.minute / 60.0 + now.second / 3600.0)

    current = calculate_planet_positions(jd_now)

    transits = []

    # Outer planets transiting natal positions (most significant)
    transit_planets = ["Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    natal_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

    for t_name in transit_planets:
        if t_name not in current:
            continue
        t_lng = current[t_name]["longitude"]
        t_retrograde = current[t_name]["retrograde"]

        for n_name in natal_planets:
            if n_name not in natal_positions:
                continue
            n_lng = natal_positions[n_name]["longitude"]

            diff = angle_diff(t_lng, n_lng)

            for aspect_name, aspect_info in ASPECTS.items():
                if aspect_info["type"] != "major":
                    continue
                orb = abs(diff - aspect_info["angle"])
                max_orb = aspect_info["orb"] * 0.6  # Tighter orbs for transits

                if orb <= max_orb:
                    strength = round(1 - (orb / max_orb), 2)

                    # Estimate dates (rough: based on planet speed)
                    speed = abs(current[t_name]["speed"]) or 0.01
                    days_to_exact = orb / speed
                    days_duration = max_orb / speed

                    interpretation = _transit_interpretation(t_name, aspect_name, n_name)
                    actions = _transit_actions(t_name, aspect_name, n_name)

                    transits.append({
                        "transit_type": f"{t_name} {aspect_name} natal {n_name}",
                        "planet": t_name,
                        "aspect": aspect_name,
                        "natal_planet": n_name,
                        "start_date": (now - timedelta(days=days_duration)).strftime("%Y-%m-%d"),
                        "peak_date": now.strftime("%Y-%m-%d"),
                        "end_date": (now + timedelta(days=days_duration)).strftime("%Y-%m-%d"),
                        "strength": strength,
                        "orb": round(orb, 2),
                        "retrograde": t_retrograde,
                        "interpretation": interpretation,
                        "action_items": actions,
                    })

    # Sort by strength
    transits.sort(key=lambda t: t["strength"], reverse=True)
    return transits[:10]  # Return top 10 most significant


def _transit_interpretation(transit: str, aspect: str, natal: str) -> str:
    """Generate a brief interpretation of a transit."""
    interpretations = {
        ("Jupiter", "Conjunction"): f"Jupiter conjoins your natal {natal}, bringing expansion, luck, and growth opportunities in the areas {natal} governs.",
        ("Jupiter", "Trine"): f"Jupiter trines your natal {natal}, creating a flowing period of ease and opportunity.",
        ("Jupiter", "Square"): f"Jupiter squares your natal {natal}, bringing growth through creative tension and overreach.",
        ("Jupiter", "Opposition"): f"Jupiter opposes your natal {natal}, bringing perspective through others and potential excess.",
        ("Jupiter", "Sextile"): f"Jupiter sextiles your natal {natal}, opening subtle doors of opportunity.",
        ("Saturn", "Conjunction"): f"Saturn conjoins your natal {natal}, demanding structure, discipline, and maturation.",
        ("Saturn", "Trine"): f"Saturn trines your natal {natal}, supporting steady, reliable progress.",
        ("Saturn", "Square"): f"Saturn squares your natal {natal}, testing your foundations and requiring adjustments.",
        ("Saturn", "Opposition"): f"Saturn opposes your natal {natal}, bringing accountability and relationship tests.",
        ("Saturn", "Sextile"): f"Saturn sextiles your natal {natal}, offering structured growth opportunities.",
        ("Uranus", "Conjunction"): f"Uranus conjoins your natal {natal}, bringing sudden breakthroughs and liberation.",
        ("Uranus", "Trine"): f"Uranus trines your natal {natal}, inspiring innovation without disruption.",
        ("Uranus", "Square"): f"Uranus squares your natal {natal}, creating restless energy demanding change.",
        ("Uranus", "Opposition"): f"Uranus opposes your natal {natal}, triggering awakening through external events.",
        ("Neptune", "Conjunction"): f"Neptune conjoins your natal {natal}, dissolving boundaries and enhancing intuition.",
        ("Neptune", "Trine"): f"Neptune trines your natal {natal}, deepening spiritual connection and creativity.",
        ("Neptune", "Square"): f"Neptune squares your natal {natal}, creating confusion that invites surrender and faith.",
        ("Pluto", "Conjunction"): f"Pluto conjoins your natal {natal}, initiating deep transformation and empowerment.",
        ("Pluto", "Trine"): f"Pluto trines your natal {natal}, supporting powerful personal evolution.",
        ("Pluto", "Square"): f"Pluto squares your natal {natal}, intensifying power dynamics and requiring release.",
    }

    key = (transit, aspect)
    return interpretations.get(key, f"{transit} {aspect} your natal {natal}, bringing dynamic energy for growth.")


def _transit_actions(transit: str, aspect: str, natal: str) -> list:
    """Generate action items for a transit."""
    base_actions = {
        "Jupiter": ["Expand your horizons", "Say yes to new opportunities", "Be mindful of overcommitting"],
        "Saturn": ["Build strong foundations", "Practice patience and discipline", "Honor your commitments"],
        "Uranus": ["Embrace change and innovation", "Break free from limiting patterns", "Trust your unique vision"],
        "Neptune": ["Trust your intuition", "Engage in creative or spiritual practices", "Set clear boundaries"],
        "Pluto": ["Release what no longer serves you", "Embrace transformation", "Reclaim your personal power"],
    }

    return base_actions.get(transit, ["Stay aware of this transit's energy", "Journal your experiences"])
