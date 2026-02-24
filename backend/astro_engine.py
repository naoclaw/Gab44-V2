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
    """Calculate the shortest angular distance between two longitudes."""
    diff = abs(a - b) % 360
    return min(diff, 360 - diff)


def parse_birth_datetime(birth_date: str, birth_time: str = None) -> float:
    """Convert birth date/time strings to Julian Day."""
    parts = birth_date.split("-")
    year = int(parts[0])
    month = int(parts[1])
    day = int(parts[2])

    hour = 12.0  # Default to noon if no time provided
    if birth_time:
        time_parts = birth_time.split(":")
        hour = float(time_parts[0]) + float(time_parts[1]) / 60.0

    return swe.julday(year, month, day, hour)


# ============== Core Calculations ==============

def calculate_planet_positions(jd: float) -> dict:
    """Calculate positions of all planets for a given Julian Day."""
    positions = {}

    for planet_id, name in PLANETS:
        result = swe.calc_ut(jd, planet_id)
        lng = result[0][0]
        lat = result[0][1]
        speed = result[0][3]

        positions[name] = {
            "longitude": round(lng, 4),
            "latitude": round(lat, 4),
            "speed": round(speed, 4),
            "retrograde": speed < 0,
            "sign": longitude_to_sign(lng),
            "degree": round(longitude_to_degree_in_sign(lng), 2),
            "formatted": format_position(lng),
        }

    # Add North Node
    result = swe.calc_ut(jd, NODE_ID)
    lng = result[0][0]
    positions["North Node"] = {
        "longitude": round(lng, 4),
        "latitude": 0,
        "speed": round(result[0][3], 4),
        "retrograde": True,  # Node is always retrograde
        "sign": longitude_to_sign(lng),
        "degree": round(longitude_to_degree_in_sign(lng), 2),
        "formatted": format_position(lng),
    }

    return positions


def calculate_houses(jd: float, latitude: float, longitude: float, system: str = "P") -> dict:
    """
    Calculate house cusps using the specified house system.
    Default is Placidus ('P'). Other options: 'K' (Koch), 'W' (Whole Sign), etc.
    """
    cusps, ascmc = swe.houses(jd, latitude, longitude, system.encode())

    houses = {}
    for i in range(12):
        house_num = i + 1
        lng = cusps[i]
        houses[str(house_num)] = {
            "cusp": round(lng, 4),
            "sign": longitude_to_sign(lng),
            "degree": round(longitude_to_degree_in_sign(lng), 2),
            "formatted": format_position(lng),
            "meaning": HOUSE_MEANINGS[house_num],
        }

    # Add angles
    houses["ASC"] = round(ascmc[0], 4)
    houses["MC"] = round(ascmc[1], 4)
    houses["DSC"] = round((ascmc[0] + 180) % 360, 4)
    houses["IC"] = round((ascmc[1] + 180) % 360, 4)

    return houses, list(cusps)


def calculate_aspects(positions: dict) -> list:
    """Calculate aspects between all planet pairs."""
    aspects = []
    planet_names = list(positions.keys())

    for i in range(len(planet_names)):
        for j in range(i + 1, len(planet_names)):
            name1 = planet_names[i]
            name2 = planet_names[j]
            lng1 = positions[name1]["longitude"]
            lng2 = positions[name2]["longitude"]

            diff = angle_diff(lng1, lng2)

            for aspect_name, aspect_info in ASPECTS.items():
                orb = abs(diff - aspect_info["angle"])
                if orb <= aspect_info["orb"]:
                    strength = round(1 - (orb / aspect_info["orb"]), 2)
                    aspects.append({
                        "planet1": name1,
                        "planet2": name2,
                        "aspect": aspect_name,
                        "angle": aspect_info["angle"],
                        "orb": round(orb, 2),
                        "strength": strength,
                        "type": aspect_info["type"],
                        "applying": _is_applying(positions[name1], positions[name2], aspect_info["angle"]),
                    })

    # Sort by strength descending
    aspects.sort(key=lambda a: a["strength"], reverse=True)
    return aspects


def _is_applying(pos1: dict, pos2: dict, target_angle: float) -> bool:
    """Determine if an aspect is applying (getting tighter) or separating."""
    speed1 = pos1.get("speed", 0)
    speed2 = pos2.get("speed", 0)
    lng1 = pos1["longitude"]
    lng2 = pos2["longitude"]

    current_diff = angle_diff(lng1, lng2)

    # Simulate a tiny time step
    future_diff = angle_diff(lng1 + speed1 * 0.1, lng2 + speed2 * 0.1)
    future_orb = abs(future_diff - target_angle)
    current_orb = abs(current_diff - target_angle)

    return future_orb < current_orb


def detect_patterns(positions: dict, aspects: list) -> list:
    """Detect chart patterns (stelliums, grand trines, T-squares, etc.)."""
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
            patterns.append(f"Stellium in {sign} ({', '.join(planets)})")

    # Element balance
    element_counts = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    for name, pos in positions.items():
        if name == "North Node":
            continue
        element = ELEMENTS.get(pos["sign"], "")
        if element:
            element_counts[element] += 1

    dominant = max(element_counts, key=element_counts.get)
    if element_counts[dominant] >= 4:
        patterns.append(f"Dominant {dominant} element ({element_counts[dominant]} planets)")

    lacking = [e for e, c in element_counts.items() if c == 0]
    for element in lacking:
        patterns.append(f"Lacking {element} element")

    # Modality balance
    modality_counts = {"Cardinal": 0, "Fixed": 0, "Mutable": 0}
    for name, pos in positions.items():
        if name == "North Node":
            continue
        modality = MODALITIES.get(pos["sign"], "")
        if modality:
            modality_counts[modality] += 1

    dominant_mod = max(modality_counts, key=modality_counts.get)
    if modality_counts[dominant_mod] >= 4:
        patterns.append(f"Dominant {dominant_mod} modality ({modality_counts[dominant_mod]} planets)")

    # Grand Trine detection (three planets all trine each other)
    trine_aspects = [a for a in aspects if a["aspect"] == "Trine" and a["strength"] >= 0.5]
    _detect_grand_trine(trine_aspects, patterns)

    # T-Square detection
    _detect_t_square(aspects, patterns)

    return patterns


def _detect_grand_trine(trine_aspects: list, patterns: list):
    """Check for grand trines in the trine aspects."""
    planets_in_trines = set()
    for a in trine_aspects:
        planets_in_trines.add(a["planet1"])
        planets_in_trines.add(a["planet2"])

    planet_list = list(planets_in_trines)
    for i in range(len(planet_list)):
        for j in range(i + 1, len(planet_list)):
            for k in range(j + 1, len(planet_list)):
                p1, p2, p3 = planet_list[i], planet_list[j], planet_list[k]
                pairs = {(p1, p2), (p1, p3), (p2, p3)}
                found = 0
                for a in trine_aspects:
                    if (a["planet1"], a["planet2"]) in pairs or (a["planet2"], a["planet1"]) in pairs:
                        found += 1
                if found >= 3:
                    patterns.append(f"Grand Trine ({p1}, {p2}, {p3})")
                    return  # Only report the first one


def _detect_t_square(aspects: list, patterns: list):
    """Check for T-squares (two squares and an opposition)."""
    squares = [a for a in aspects if a["aspect"] == "Square" and a["strength"] >= 0.4]
    oppositions = [a for a in aspects if a["aspect"] == "Opposition" and a["strength"] >= 0.4]

    for opp in oppositions:
        p1, p2 = opp["planet1"], opp["planet2"]
        for sq in squares:
            apex = None
            if sq["planet1"] == p1 or sq["planet2"] == p1:
                other = sq["planet2"] if sq["planet1"] == p1 else sq["planet1"]
                # Check if the other planet also squares p2
                for sq2 in squares:
                    if (sq2["planet1"] == other and sq2["planet2"] == p2) or \
                       (sq2["planet1"] == p2 and sq2["planet2"] == other):
                        apex = other
                        break
            if apex:
                patterns.append(f"T-Square ({p1} opp {p2}, apex {apex})")
                return


# ============== Public API ==============

def calculate_natal_chart(
    birth_date: str,
    birth_time: str = None,
    latitude: float = 0.0,
    longitude: float = 0.0,
) -> dict:
    """
    Calculate a complete natal chart.

    Args:
        birth_date: "YYYY-MM-DD"
        birth_time: "HH:MM" (optional, defaults to noon)
        latitude: Birth location latitude
        longitude: Birth location longitude

    Returns:
        Complete natal chart with planets, houses, aspects, and patterns.
    """
    jd = parse_birth_datetime(birth_date, birth_time)

    # Calculate planet positions
    positions = calculate_planet_positions(jd)

    # Calculate houses (requires birth location)
    has_location = latitude != 0.0 or longitude != 0.0
    houses = {}
    cusps = []
    if has_location:
        houses, cusps = calculate_houses(jd, latitude, longitude)

        # Assign house numbers to planets
        for name in positions:
            positions[name]["house"] = find_house(positions[name]["longitude"], cusps)
    else:
        # Without location, use Whole Sign houses from 0° Aries
        for i in range(1, 13):
            houses[str(i)] = {
                "cusp": (i - 1) * 30,
                "sign": ZODIAC_SIGNS[i - 1],
                "degree": 0,
                "formatted": f"0° {ZODIAC_SIGNS[i - 1]} 0'",
                "meaning": HOUSE_MEANINGS[i],
            }

    # Calculate aspects
    aspects = calculate_aspects(positions)

    # Detect patterns
    patterns = detect_patterns(positions, aspects)

    # Build the chart
    sun_sign = positions["Sun"]["sign"]
    moon_sign = positions["Moon"]["sign"]
    rising_sign = longitude_to_sign(houses.get("ASC", 0)) if "ASC" in houses else sun_sign

    return {
        "sun_sign": sun_sign,
        "moon_sign": moon_sign,
        "rising_sign": rising_sign,
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
    jd_now = swe.julday(now.year, now.month, now.day, now.hour + now.minute / 60.0)

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
