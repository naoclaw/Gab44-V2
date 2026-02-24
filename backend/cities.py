"""
Gab44 Static City Geocoding Database
======================================
~90 major world cities with coordinates and timezone offsets.

Used for birth location selection during registration.
Eliminates the need for an external geocoding API.

Each city includes:
- name: City name
- country: Country name
- latitude: Decimal degrees (positive = North)
- longitude: Decimal degrees (positive = East)
- timezone: IANA timezone identifier
"""

CITIES = [
    # North America
    {"name": "New York", "country": "USA", "latitude": 40.7128, "longitude": -74.0060, "timezone": "America/New_York"},
    {"name": "Los Angeles", "country": "USA", "latitude": 34.0522, "longitude": -118.2437, "timezone": "America/Los_Angeles"},
    {"name": "Chicago", "country": "USA", "latitude": 41.8781, "longitude": -87.6298, "timezone": "America/Chicago"},
    {"name": "Houston", "country": "USA", "latitude": 29.7604, "longitude": -95.3698, "timezone": "America/Chicago"},
    {"name": "Phoenix", "country": "USA", "latitude": 33.4484, "longitude": -112.0740, "timezone": "America/Phoenix"},
    {"name": "Philadelphia", "country": "USA", "latitude": 39.9526, "longitude": -75.1652, "timezone": "America/New_York"},
    {"name": "San Antonio", "country": "USA", "latitude": 29.4241, "longitude": -98.4936, "timezone": "America/Chicago"},
    {"name": "San Diego", "country": "USA", "latitude": 32.7157, "longitude": -117.1611, "timezone": "America/Los_Angeles"},
    {"name": "Dallas", "country": "USA", "latitude": 32.7767, "longitude": -96.7970, "timezone": "America/Chicago"},
    {"name": "San Francisco", "country": "USA", "latitude": 37.7749, "longitude": -122.4194, "timezone": "America/Los_Angeles"},
    {"name": "Seattle", "country": "USA", "latitude": 47.6062, "longitude": -122.3321, "timezone": "America/Los_Angeles"},
    {"name": "Denver", "country": "USA", "latitude": 39.7392, "longitude": -104.9903, "timezone": "America/Denver"},
    {"name": "Boston", "country": "USA", "latitude": 42.3601, "longitude": -71.0589, "timezone": "America/New_York"},
    {"name": "Atlanta", "country": "USA", "latitude": 33.7490, "longitude": -84.3880, "timezone": "America/New_York"},
    {"name": "Miami", "country": "USA", "latitude": 25.7617, "longitude": -80.1918, "timezone": "America/New_York"},
    {"name": "Las Vegas", "country": "USA", "latitude": 36.1699, "longitude": -115.1398, "timezone": "America/Los_Angeles"},
    {"name": "Portland", "country": "USA", "latitude": 45.5152, "longitude": -122.6784, "timezone": "America/Los_Angeles"},
    {"name": "Washington DC", "country": "USA", "latitude": 38.9072, "longitude": -77.0369, "timezone": "America/New_York"},
    {"name": "Toronto", "country": "Canada", "latitude": 43.6532, "longitude": -79.3832, "timezone": "America/Toronto"},
    {"name": "Vancouver", "country": "Canada", "latitude": 49.2827, "longitude": -123.1207, "timezone": "America/Vancouver"},
    {"name": "Montreal", "country": "Canada", "latitude": 45.5017, "longitude": -73.5673, "timezone": "America/Montreal"},
    {"name": "Mexico City", "country": "Mexico", "latitude": 19.4326, "longitude": -99.1332, "timezone": "America/Mexico_City"},

    # Europe
    {"name": "London", "country": "UK", "latitude": 51.5074, "longitude": -0.1278, "timezone": "Europe/London"},
    {"name": "Paris", "country": "France", "latitude": 48.8566, "longitude": 2.3522, "timezone": "Europe/Paris"},
    {"name": "Berlin", "country": "Germany", "latitude": 52.5200, "longitude": 13.4050, "timezone": "Europe/Berlin"},
    {"name": "Madrid", "country": "Spain", "latitude": 40.4168, "longitude": -3.7038, "timezone": "Europe/Madrid"},
    {"name": "Rome", "country": "Italy", "latitude": 41.9028, "longitude": 12.4964, "timezone": "Europe/Rome"},
    {"name": "Amsterdam", "country": "Netherlands", "latitude": 52.3676, "longitude": 4.9041, "timezone": "Europe/Amsterdam"},
    {"name": "Brussels", "country": "Belgium", "latitude": 50.8503, "longitude": 4.3517, "timezone": "Europe/Brussels"},
    {"name": "Vienna", "country": "Austria", "latitude": 48.2082, "longitude": 16.3738, "timezone": "Europe/Vienna"},
    {"name": "Zurich", "country": "Switzerland", "latitude": 47.3769, "longitude": 8.5417, "timezone": "Europe/Zurich"},
    {"name": "Stockholm", "country": "Sweden", "latitude": 59.3293, "longitude": 18.0686, "timezone": "Europe/Stockholm"},
    {"name": "Copenhagen", "country": "Denmark", "latitude": 55.6761, "longitude": 12.5683, "timezone": "Europe/Copenhagen"},
    {"name": "Oslo", "country": "Norway", "latitude": 59.9139, "longitude": 10.7522, "timezone": "Europe/Oslo"},
    {"name": "Helsinki", "country": "Finland", "latitude": 60.1699, "longitude": 24.9384, "timezone": "Europe/Helsinki"},
    {"name": "Lisbon", "country": "Portugal", "latitude": 38.7223, "longitude": -9.1393, "timezone": "Europe/Lisbon"},
    {"name": "Dublin", "country": "Ireland", "latitude": 53.3498, "longitude": -6.2603, "timezone": "Europe/Dublin"},
    {"name": "Warsaw", "country": "Poland", "latitude": 52.2297, "longitude": 21.0122, "timezone": "Europe/Warsaw"},
    {"name": "Prague", "country": "Czech Republic", "latitude": 50.0755, "longitude": 14.4378, "timezone": "Europe/Prague"},
    {"name": "Budapest", "country": "Hungary", "latitude": 47.4979, "longitude": 19.0402, "timezone": "Europe/Budapest"},
    {"name": "Athens", "country": "Greece", "latitude": 37.9838, "longitude": 23.7275, "timezone": "Europe/Athens"},
    {"name": "Istanbul", "country": "Turkey", "latitude": 41.0082, "longitude": 28.9784, "timezone": "Europe/Istanbul"},
    {"name": "Moscow", "country": "Russia", "latitude": 55.7558, "longitude": 37.6173, "timezone": "Europe/Moscow"},
    {"name": "Bucharest", "country": "Romania", "latitude": 44.4268, "longitude": 26.1025, "timezone": "Europe/Bucharest"},
    {"name": "Barcelona", "country": "Spain", "latitude": 41.3851, "longitude": 2.1734, "timezone": "Europe/Madrid"},

    # South America
    {"name": "São Paulo", "country": "Brazil", "latitude": -23.5505, "longitude": -46.6333, "timezone": "America/Sao_Paulo"},
    {"name": "Buenos Aires", "country": "Argentina", "latitude": -34.6037, "longitude": -58.3816, "timezone": "America/Argentina/Buenos_Aires"},
    {"name": "Rio de Janeiro", "country": "Brazil", "latitude": -22.9068, "longitude": -43.1729, "timezone": "America/Sao_Paulo"},
    {"name": "Bogotá", "country": "Colombia", "latitude": 4.7110, "longitude": -74.0721, "timezone": "America/Bogota"},
    {"name": "Lima", "country": "Peru", "latitude": -12.0464, "longitude": -77.0428, "timezone": "America/Lima"},
    {"name": "Santiago", "country": "Chile", "latitude": -33.4489, "longitude": -70.6693, "timezone": "America/Santiago"},

    # Asia
    {"name": "Tokyo", "country": "Japan", "latitude": 35.6762, "longitude": 139.6503, "timezone": "Asia/Tokyo"},
    {"name": "Beijing", "country": "China", "latitude": 39.9042, "longitude": 116.4074, "timezone": "Asia/Shanghai"},
    {"name": "Shanghai", "country": "China", "latitude": 31.2304, "longitude": 121.4737, "timezone": "Asia/Shanghai"},
    {"name": "Hong Kong", "country": "China", "latitude": 22.3193, "longitude": 114.1694, "timezone": "Asia/Hong_Kong"},
    {"name": "Seoul", "country": "South Korea", "latitude": 37.5665, "longitude": 126.9780, "timezone": "Asia/Seoul"},
    {"name": "Mumbai", "country": "India", "latitude": 19.0760, "longitude": 72.8777, "timezone": "Asia/Kolkata"},
    {"name": "Delhi", "country": "India", "latitude": 28.7041, "longitude": 77.1025, "timezone": "Asia/Kolkata"},
    {"name": "Bangalore", "country": "India", "latitude": 12.9716, "longitude": 77.5946, "timezone": "Asia/Kolkata"},
    {"name": "Bangkok", "country": "Thailand", "latitude": 13.7563, "longitude": 100.5018, "timezone": "Asia/Bangkok"},
    {"name": "Singapore", "country": "Singapore", "latitude": 1.3521, "longitude": 103.8198, "timezone": "Asia/Singapore"},
    {"name": "Jakarta", "country": "Indonesia", "latitude": -6.2088, "longitude": 106.8456, "timezone": "Asia/Jakarta"},
    {"name": "Kuala Lumpur", "country": "Malaysia", "latitude": 3.1390, "longitude": 101.6869, "timezone": "Asia/Kuala_Lumpur"},
    {"name": "Dubai", "country": "UAE", "latitude": 25.2048, "longitude": 55.2708, "timezone": "Asia/Dubai"},
    {"name": "Riyadh", "country": "Saudi Arabia", "latitude": 24.7136, "longitude": 46.6753, "timezone": "Asia/Riyadh"},
    {"name": "Tel Aviv", "country": "Israel", "latitude": 32.0853, "longitude": 34.7818, "timezone": "Asia/Jerusalem"},
    {"name": "Taipei", "country": "Taiwan", "latitude": 25.0330, "longitude": 121.5654, "timezone": "Asia/Taipei"},
    {"name": "Manila", "country": "Philippines", "latitude": 14.5995, "longitude": 120.9842, "timezone": "Asia/Manila"},
    {"name": "Hanoi", "country": "Vietnam", "latitude": 21.0278, "longitude": 105.8342, "timezone": "Asia/Ho_Chi_Minh"},
    {"name": "Karachi", "country": "Pakistan", "latitude": 24.8607, "longitude": 67.0011, "timezone": "Asia/Karachi"},

    # Africa
    {"name": "Cairo", "country": "Egypt", "latitude": 30.0444, "longitude": 31.2357, "timezone": "Africa/Cairo"},
    {"name": "Lagos", "country": "Nigeria", "latitude": 6.5244, "longitude": 3.3792, "timezone": "Africa/Lagos"},
    {"name": "Johannesburg", "country": "South Africa", "latitude": -26.2041, "longitude": 28.0473, "timezone": "Africa/Johannesburg"},
    {"name": "Cape Town", "country": "South Africa", "latitude": -33.9249, "longitude": 18.4241, "timezone": "Africa/Johannesburg"},
    {"name": "Nairobi", "country": "Kenya", "latitude": -1.2921, "longitude": 36.8219, "timezone": "Africa/Nairobi"},
    {"name": "Casablanca", "country": "Morocco", "latitude": 33.5731, "longitude": -7.5898, "timezone": "Africa/Casablanca"},
    {"name": "Accra", "country": "Ghana", "latitude": 5.6037, "longitude": -0.1870, "timezone": "Africa/Accra"},
    {"name": "Addis Ababa", "country": "Ethiopia", "latitude": 9.0250, "longitude": 38.7469, "timezone": "Africa/Addis_Ababa"},

    # Oceania
    {"name": "Sydney", "country": "Australia", "latitude": -33.8688, "longitude": 151.2093, "timezone": "Australia/Sydney"},
    {"name": "Melbourne", "country": "Australia", "latitude": -37.8136, "longitude": 144.9631, "timezone": "Australia/Melbourne"},
    {"name": "Brisbane", "country": "Australia", "latitude": -27.4698, "longitude": 153.0251, "timezone": "Australia/Brisbane"},
    {"name": "Perth", "country": "Australia", "latitude": -31.9505, "longitude": 115.8605, "timezone": "Australia/Perth"},
    {"name": "Auckland", "country": "New Zealand", "latitude": -36.8485, "longitude": 174.7633, "timezone": "Pacific/Auckland"},

    # Caribbean & Central America
    {"name": "Havana", "country": "Cuba", "latitude": 23.1136, "longitude": -82.3666, "timezone": "America/Havana"},
    {"name": "San Juan", "country": "Puerto Rico", "latitude": 18.4655, "longitude": -66.1057, "timezone": "America/Puerto_Rico"},
    {"name": "Kingston", "country": "Jamaica", "latitude": 18.0179, "longitude": -76.8099, "timezone": "America/Jamaica"},
    {"name": "Panama City", "country": "Panama", "latitude": 8.9824, "longitude": -79.5199, "timezone": "America/Panama"},
]


def search_cities(query: str = "", limit: int = 20) -> list:
    """
    Search cities by name or country.
    Returns all cities if query is empty, otherwise filters by case-insensitive match.
    """
    if not query:
        return CITIES[:limit]

    q = query.lower()
    results = [
        city for city in CITIES
        if q in city["name"].lower() or q in city["country"].lower()
    ]
    return results[:limit]


def find_city(name: str, country: str = "") -> dict | None:
    """
    Find an exact city match by name (and optionally country).
    Returns the city dict or None.
    """
    name_lower = name.lower()
    country_lower = country.lower() if country else ""

    for city in CITIES:
        if city["name"].lower() == name_lower:
            if not country_lower or city["country"].lower() == country_lower:
                return city
    return None
