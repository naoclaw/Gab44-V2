"""
Gab44 City Geocoding
=====================
Hybrid geocoding: Mapbox API when MAPBOX_ACCESS_TOKEN is set, otherwise
falls back to a static database of 327 major world cities.

Each city includes:
- name: City name
- country: Country name
- latitude: Decimal degrees (positive = North)
- longitude: Decimal degrees (positive = East)
- timezone: IANA timezone identifier
"""

import os
import logging

import requests

logger = logging.getLogger(__name__)

MAPBOX_ACCESS_TOKEN = os.environ.get("MAPBOX_ACCESS_TOKEN", "")

CITIES = [
    # =========================================================================
    # North America — USA
    # =========================================================================
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
    {"name": "Austin", "country": "USA", "latitude": 30.2672, "longitude": -97.7431, "timezone": "America/Chicago"},
    {"name": "Nashville", "country": "USA", "latitude": 36.1627, "longitude": -86.7816, "timezone": "America/Chicago"},
    {"name": "Charlotte", "country": "USA", "latitude": 35.2271, "longitude": -80.8431, "timezone": "America/New_York"},
    {"name": "Minneapolis", "country": "USA", "latitude": 44.9778, "longitude": -93.2650, "timezone": "America/Chicago"},
    {"name": "Detroit", "country": "USA", "latitude": 42.3314, "longitude": -83.0458, "timezone": "America/Detroit"},
    {"name": "New Orleans", "country": "USA", "latitude": 29.9511, "longitude": -90.0715, "timezone": "America/Chicago"},
    {"name": "Honolulu", "country": "USA", "latitude": 21.3069, "longitude": -157.8583, "timezone": "Pacific/Honolulu"},
    {"name": "Anchorage", "country": "USA", "latitude": 61.2181, "longitude": -149.9003, "timezone": "America/Anchorage"},
    {"name": "Salt Lake City", "country": "USA", "latitude": 40.7608, "longitude": -111.8910, "timezone": "America/Denver"},
    {"name": "Indianapolis", "country": "USA", "latitude": 39.7684, "longitude": -86.1581, "timezone": "America/Indiana/Indianapolis"},
    {"name": "Columbus", "country": "USA", "latitude": 39.9612, "longitude": -82.9988, "timezone": "America/New_York"},
    {"name": "Jacksonville", "country": "USA", "latitude": 30.3322, "longitude": -81.6557, "timezone": "America/New_York"},
    {"name": "Memphis", "country": "USA", "latitude": 35.1495, "longitude": -90.0490, "timezone": "America/Chicago"},
    {"name": "Oklahoma City", "country": "USA", "latitude": 35.4676, "longitude": -97.5164, "timezone": "America/Chicago"},
    {"name": "Raleigh", "country": "USA", "latitude": 35.7796, "longitude": -78.6382, "timezone": "America/New_York"},
    {"name": "Milwaukee", "country": "USA", "latitude": 43.0389, "longitude": -87.9065, "timezone": "America/Chicago"},
    {"name": "Tampa", "country": "USA", "latitude": 27.9506, "longitude": -82.4572, "timezone": "America/New_York"},
    {"name": "Baltimore", "country": "USA", "latitude": 39.2904, "longitude": -76.6122, "timezone": "America/New_York"},
    {"name": "St. Louis", "country": "USA", "latitude": 38.6270, "longitude": -90.1994, "timezone": "America/Chicago"},
    {"name": "Cincinnati", "country": "USA", "latitude": 39.1031, "longitude": -84.5120, "timezone": "America/New_York"},
    {"name": "Pittsburgh", "country": "USA", "latitude": 40.4406, "longitude": -79.9959, "timezone": "America/New_York"},
    {"name": "Kansas City", "country": "USA", "latitude": 39.0997, "longitude": -94.5786, "timezone": "America/Chicago"},
    {"name": "Sacramento", "country": "USA", "latitude": 38.5816, "longitude": -121.4944, "timezone": "America/Los_Angeles"},
    {"name": "Orlando", "country": "USA", "latitude": 28.5383, "longitude": -81.3792, "timezone": "America/New_York"},
    {"name": "Cleveland", "country": "USA", "latitude": 41.4993, "longitude": -81.6944, "timezone": "America/New_York"},
    {"name": "Louisville", "country": "USA", "latitude": 38.2527, "longitude": -85.7585, "timezone": "America/Kentucky/Louisville"},
    {"name": "Richmond", "country": "USA", "latitude": 37.5407, "longitude": -77.4360, "timezone": "America/New_York"},
    {"name": "Virginia Beach", "country": "USA", "latitude": 36.8529, "longitude": -75.9780, "timezone": "America/New_York"},
    {"name": "Tucson", "country": "USA", "latitude": 32.2226, "longitude": -110.9747, "timezone": "America/Phoenix"},
    {"name": "Albuquerque", "country": "USA", "latitude": 35.0844, "longitude": -106.6504, "timezone": "America/Denver"},
    {"name": "Omaha", "country": "USA", "latitude": 41.2565, "longitude": -95.9345, "timezone": "America/Chicago"},
    {"name": "Tulsa", "country": "USA", "latitude": 36.1540, "longitude": -95.9928, "timezone": "America/Chicago"},
    {"name": "El Paso", "country": "USA", "latitude": 31.7619, "longitude": -106.4850, "timezone": "America/Denver"},
    {"name": "Fresno", "country": "USA", "latitude": 36.7378, "longitude": -119.7871, "timezone": "America/Los_Angeles"},
    {"name": "Boise", "country": "USA", "latitude": 43.6150, "longitude": -116.2023, "timezone": "America/Boise"},
    {"name": "Little Rock", "country": "USA", "latitude": 34.7465, "longitude": -92.2896, "timezone": "America/Chicago"},

    # =========================================================================
    # North America — Canada
    # =========================================================================
    {"name": "Toronto", "country": "Canada", "latitude": 43.6532, "longitude": -79.3832, "timezone": "America/Toronto"},
    {"name": "Vancouver", "country": "Canada", "latitude": 49.2827, "longitude": -123.1207, "timezone": "America/Vancouver"},
    {"name": "Montreal", "country": "Canada", "latitude": 45.5017, "longitude": -73.5673, "timezone": "America/Montreal"},
    {"name": "Calgary", "country": "Canada", "latitude": 51.0447, "longitude": -114.0719, "timezone": "America/Edmonton"},
    {"name": "Edmonton", "country": "Canada", "latitude": 53.5461, "longitude": -113.4938, "timezone": "America/Edmonton"},
    {"name": "Ottawa", "country": "Canada", "latitude": 45.4215, "longitude": -75.6972, "timezone": "America/Toronto"},
    {"name": "Winnipeg", "country": "Canada", "latitude": 49.8951, "longitude": -97.1384, "timezone": "America/Winnipeg"},
    {"name": "Halifax", "country": "Canada", "latitude": 44.6488, "longitude": -63.5752, "timezone": "America/Halifax"},
    {"name": "Quebec City", "country": "Canada", "latitude": 46.8139, "longitude": -71.2080, "timezone": "America/Toronto"},

    # =========================================================================
    # North America — Mexico & Central America
    # =========================================================================
    {"name": "Mexico City", "country": "Mexico", "latitude": 19.4326, "longitude": -99.1332, "timezone": "America/Mexico_City"},
    {"name": "Guadalajara", "country": "Mexico", "latitude": 20.6597, "longitude": -103.3496, "timezone": "America/Mexico_City"},
    {"name": "Monterrey", "country": "Mexico", "latitude": 25.6866, "longitude": -100.3161, "timezone": "America/Monterrey"},
    {"name": "Cancún", "country": "Mexico", "latitude": 21.1619, "longitude": -86.8515, "timezone": "America/Cancun"},
    {"name": "Guatemala City", "country": "Guatemala", "latitude": 14.6349, "longitude": -90.5069, "timezone": "America/Guatemala"},
    {"name": "San Salvador", "country": "El Salvador", "latitude": 13.6929, "longitude": -89.2182, "timezone": "America/El_Salvador"},
    {"name": "Tegucigalpa", "country": "Honduras", "latitude": 14.0723, "longitude": -87.1921, "timezone": "America/Tegucigalpa"},
    {"name": "Managua", "country": "Nicaragua", "latitude": 12.1150, "longitude": -86.2362, "timezone": "America/Managua"},
    {"name": "San José", "country": "Costa Rica", "latitude": 9.9281, "longitude": -84.0907, "timezone": "America/Costa_Rica"},
    {"name": "Panama City", "country": "Panama", "latitude": 8.9824, "longitude": -79.5199, "timezone": "America/Panama"},

    # =========================================================================
    # Caribbean
    # =========================================================================
    {"name": "Havana", "country": "Cuba", "latitude": 23.1136, "longitude": -82.3666, "timezone": "America/Havana"},
    {"name": "San Juan", "country": "Puerto Rico", "latitude": 18.4655, "longitude": -66.1057, "timezone": "America/Puerto_Rico"},
    {"name": "Kingston", "country": "Jamaica", "latitude": 18.0179, "longitude": -76.8099, "timezone": "America/Jamaica"},
    {"name": "Santo Domingo", "country": "Dominican Republic", "latitude": 18.4861, "longitude": -69.9312, "timezone": "America/Santo_Domingo"},
    {"name": "Port-au-Prince", "country": "Haiti", "latitude": 18.5944, "longitude": -72.3074, "timezone": "America/Port-au-Prince"},
    {"name": "Nassau", "country": "Bahamas", "latitude": 25.0343, "longitude": -77.3963, "timezone": "America/Nassau"},
    {"name": "Bridgetown", "country": "Barbados", "latitude": 13.1132, "longitude": -59.5988, "timezone": "America/Barbados"},
    {"name": "Port of Spain", "country": "Trinidad and Tobago", "latitude": 10.6596, "longitude": -61.5086, "timezone": "America/Port_of_Spain"},
    {"name": "Willemstad", "country": "Curaçao", "latitude": 12.1696, "longitude": -68.9900, "timezone": "America/Curacao"},

    # =========================================================================
    # South America
    # =========================================================================
    {"name": "São Paulo", "country": "Brazil", "latitude": -23.5505, "longitude": -46.6333, "timezone": "America/Sao_Paulo"},
    {"name": "Buenos Aires", "country": "Argentina", "latitude": -34.6037, "longitude": -58.3816, "timezone": "America/Argentina/Buenos_Aires"},
    {"name": "Rio de Janeiro", "country": "Brazil", "latitude": -22.9068, "longitude": -43.1729, "timezone": "America/Sao_Paulo"},
    {"name": "Bogotá", "country": "Colombia", "latitude": 4.7110, "longitude": -74.0721, "timezone": "America/Bogota"},
    {"name": "Lima", "country": "Peru", "latitude": -12.0464, "longitude": -77.0428, "timezone": "America/Lima"},
    {"name": "Santiago", "country": "Chile", "latitude": -33.4489, "longitude": -70.6693, "timezone": "America/Santiago"},
    {"name": "Medellín", "country": "Colombia", "latitude": 6.2476, "longitude": -75.5658, "timezone": "America/Bogota"},
    {"name": "Cali", "country": "Colombia", "latitude": 3.4516, "longitude": -76.5320, "timezone": "America/Bogota"},
    {"name": "Quito", "country": "Ecuador", "latitude": -0.1807, "longitude": -78.4678, "timezone": "America/Guayaquil"},
    {"name": "Guayaquil", "country": "Ecuador", "latitude": -2.1710, "longitude": -79.9224, "timezone": "America/Guayaquil"},
    {"name": "Caracas", "country": "Venezuela", "latitude": 10.4806, "longitude": -66.9036, "timezone": "America/Caracas"},
    {"name": "Montevideo", "country": "Uruguay", "latitude": -34.9011, "longitude": -56.1645, "timezone": "America/Montevideo"},
    {"name": "Asunción", "country": "Paraguay", "latitude": -25.2637, "longitude": -57.5759, "timezone": "America/Asuncion"},
    {"name": "La Paz", "country": "Bolivia", "latitude": -16.4897, "longitude": -68.1193, "timezone": "America/La_Paz"},
    {"name": "Recife", "country": "Brazil", "latitude": -8.0476, "longitude": -34.8770, "timezone": "America/Recife"},
    {"name": "Brasília", "country": "Brazil", "latitude": -15.7975, "longitude": -47.8919, "timezone": "America/Sao_Paulo"},
    {"name": "Curitiba", "country": "Brazil", "latitude": -25.4284, "longitude": -49.2733, "timezone": "America/Sao_Paulo"},
    {"name": "Belo Horizonte", "country": "Brazil", "latitude": -19.9167, "longitude": -43.9345, "timezone": "America/Sao_Paulo"},
    {"name": "Fortaleza", "country": "Brazil", "latitude": -3.7172, "longitude": -38.5433, "timezone": "America/Fortaleza"},
    {"name": "Salvador", "country": "Brazil", "latitude": -12.9714, "longitude": -38.5124, "timezone": "America/Bahia"},

    # =========================================================================
    # Europe — Western
    # =========================================================================
    {"name": "London", "country": "UK", "latitude": 51.5074, "longitude": -0.1278, "timezone": "Europe/London"},
    {"name": "Paris", "country": "France", "latitude": 48.8566, "longitude": 2.3522, "timezone": "Europe/Paris"},
    {"name": "Berlin", "country": "Germany", "latitude": 52.5200, "longitude": 13.4050, "timezone": "Europe/Berlin"},
    {"name": "Madrid", "country": "Spain", "latitude": 40.4168, "longitude": -3.7038, "timezone": "Europe/Madrid"},
    {"name": "Rome", "country": "Italy", "latitude": 41.9028, "longitude": 12.4964, "timezone": "Europe/Rome"},
    {"name": "Amsterdam", "country": "Netherlands", "latitude": 52.3676, "longitude": 4.9041, "timezone": "Europe/Amsterdam"},
    {"name": "Brussels", "country": "Belgium", "latitude": 50.8503, "longitude": 4.3517, "timezone": "Europe/Brussels"},
    {"name": "Vienna", "country": "Austria", "latitude": 48.2082, "longitude": 16.3738, "timezone": "Europe/Vienna"},
    {"name": "Zurich", "country": "Switzerland", "latitude": 47.3769, "longitude": 8.5417, "timezone": "Europe/Zurich"},
    {"name": "Lisbon", "country": "Portugal", "latitude": 38.7223, "longitude": -9.1393, "timezone": "Europe/Lisbon"},
    {"name": "Dublin", "country": "Ireland", "latitude": 53.3498, "longitude": -6.2603, "timezone": "Europe/Dublin"},
    {"name": "Barcelona", "country": "Spain", "latitude": 41.3851, "longitude": 2.1734, "timezone": "Europe/Madrid"},
    {"name": "Milan", "country": "Italy", "latitude": 45.4642, "longitude": 9.1900, "timezone": "Europe/Rome"},
    {"name": "Naples", "country": "Italy", "latitude": 40.8518, "longitude": 14.2681, "timezone": "Europe/Rome"},
    {"name": "Florence", "country": "Italy", "latitude": 43.7696, "longitude": 11.2558, "timezone": "Europe/Rome"},
    {"name": "Venice", "country": "Italy", "latitude": 45.4408, "longitude": 12.3155, "timezone": "Europe/Rome"},
    {"name": "Munich", "country": "Germany", "latitude": 48.1351, "longitude": 11.5820, "timezone": "Europe/Berlin"},
    {"name": "Frankfurt", "country": "Germany", "latitude": 50.1109, "longitude": 8.6821, "timezone": "Europe/Berlin"},
    {"name": "Hamburg", "country": "Germany", "latitude": 53.5511, "longitude": 9.9937, "timezone": "Europe/Berlin"},
    {"name": "Cologne", "country": "Germany", "latitude": 50.9375, "longitude": 6.9603, "timezone": "Europe/Berlin"},
    {"name": "Lyon", "country": "France", "latitude": 45.7640, "longitude": 4.8357, "timezone": "Europe/Paris"},
    {"name": "Marseille", "country": "France", "latitude": 43.2965, "longitude": 5.3698, "timezone": "Europe/Paris"},
    {"name": "Nice", "country": "France", "latitude": 43.7102, "longitude": 7.2620, "timezone": "Europe/Paris"},
    {"name": "Toulouse", "country": "France", "latitude": 43.6047, "longitude": 1.4442, "timezone": "Europe/Paris"},
    {"name": "Bordeaux", "country": "France", "latitude": 44.8378, "longitude": -0.5792, "timezone": "Europe/Paris"},
    {"name": "Seville", "country": "Spain", "latitude": 37.3891, "longitude": -5.9845, "timezone": "Europe/Madrid"},
    {"name": "Valencia", "country": "Spain", "latitude": 39.4699, "longitude": -0.3763, "timezone": "Europe/Madrid"},
    {"name": "Bilbao", "country": "Spain", "latitude": 43.2630, "longitude": -2.9350, "timezone": "Europe/Madrid"},
    {"name": "Porto", "country": "Portugal", "latitude": 41.1579, "longitude": -8.6291, "timezone": "Europe/Lisbon"},
    {"name": "Antwerp", "country": "Belgium", "latitude": 51.2194, "longitude": 4.4025, "timezone": "Europe/Brussels"},
    {"name": "Ghent", "country": "Belgium", "latitude": 51.0543, "longitude": 3.7174, "timezone": "Europe/Brussels"},
    {"name": "Geneva", "country": "Switzerland", "latitude": 46.2044, "longitude": 6.1432, "timezone": "Europe/Zurich"},
    {"name": "Basel", "country": "Switzerland", "latitude": 47.5596, "longitude": 7.5886, "timezone": "Europe/Zurich"},
    {"name": "Bern", "country": "Switzerland", "latitude": 46.9480, "longitude": 7.4474, "timezone": "Europe/Zurich"},
    {"name": "Luxembourg City", "country": "Luxembourg", "latitude": 49.6117, "longitude": 6.1319, "timezone": "Europe/Luxembourg"},
    {"name": "Monaco", "country": "Monaco", "latitude": 43.7384, "longitude": 7.4246, "timezone": "Europe/Monaco"},
    {"name": "Andorra la Vella", "country": "Andorra", "latitude": 42.5063, "longitude": 1.5218, "timezone": "Europe/Andorra"},

    # =========================================================================
    # Europe — British Isles
    # =========================================================================
    {"name": "Edinburgh", "country": "UK", "latitude": 55.9533, "longitude": -3.1883, "timezone": "Europe/London"},
    {"name": "Manchester", "country": "UK", "latitude": 53.4808, "longitude": -2.2426, "timezone": "Europe/London"},
    {"name": "Birmingham", "country": "UK", "latitude": 52.4862, "longitude": -1.8904, "timezone": "Europe/London"},
    {"name": "Glasgow", "country": "UK", "latitude": 55.8642, "longitude": -4.2518, "timezone": "Europe/London"},
    {"name": "Liverpool", "country": "UK", "latitude": 53.4084, "longitude": -2.9916, "timezone": "Europe/London"},
    {"name": "Bristol", "country": "UK", "latitude": 51.4545, "longitude": -2.5879, "timezone": "Europe/London"},
    {"name": "Leeds", "country": "UK", "latitude": 53.8008, "longitude": -1.5491, "timezone": "Europe/London"},
    {"name": "Cardiff", "country": "UK", "latitude": 51.4816, "longitude": -3.1791, "timezone": "Europe/London"},
    {"name": "Belfast", "country": "UK", "latitude": 54.5973, "longitude": -5.9301, "timezone": "Europe/London"},

    # =========================================================================
    # Europe — Nordics & Baltics
    # =========================================================================
    {"name": "Stockholm", "country": "Sweden", "latitude": 59.3293, "longitude": 18.0686, "timezone": "Europe/Stockholm"},
    {"name": "Copenhagen", "country": "Denmark", "latitude": 55.6761, "longitude": 12.5683, "timezone": "Europe/Copenhagen"},
    {"name": "Oslo", "country": "Norway", "latitude": 59.9139, "longitude": 10.7522, "timezone": "Europe/Oslo"},
    {"name": "Helsinki", "country": "Finland", "latitude": 60.1699, "longitude": 24.9384, "timezone": "Europe/Helsinki"},
    {"name": "Reykjavik", "country": "Iceland", "latitude": 64.1466, "longitude": -21.9426, "timezone": "Atlantic/Reykjavik"},
    {"name": "Gothenburg", "country": "Sweden", "latitude": 57.7089, "longitude": 11.9746, "timezone": "Europe/Stockholm"},
    {"name": "Malmö", "country": "Sweden", "latitude": 55.6049, "longitude": 13.0038, "timezone": "Europe/Stockholm"},
    {"name": "Turku", "country": "Finland", "latitude": 60.4518, "longitude": 22.2666, "timezone": "Europe/Helsinki"},
    {"name": "Vilnius", "country": "Lithuania", "latitude": 54.6872, "longitude": 25.2797, "timezone": "Europe/Vilnius"},
    {"name": "Riga", "country": "Latvia", "latitude": 56.9496, "longitude": 24.1052, "timezone": "Europe/Riga"},
    {"name": "Tallinn", "country": "Estonia", "latitude": 59.4370, "longitude": 24.7536, "timezone": "Europe/Tallinn"},

    # =========================================================================
    # Europe — Central & Eastern
    # =========================================================================
    {"name": "Warsaw", "country": "Poland", "latitude": 52.2297, "longitude": 21.0122, "timezone": "Europe/Warsaw"},
    {"name": "Prague", "country": "Czech Republic", "latitude": 50.0755, "longitude": 14.4378, "timezone": "Europe/Prague"},
    {"name": "Budapest", "country": "Hungary", "latitude": 47.4979, "longitude": 19.0402, "timezone": "Europe/Budapest"},
    {"name": "Bucharest", "country": "Romania", "latitude": 44.4268, "longitude": 26.1025, "timezone": "Europe/Bucharest"},
    {"name": "Innsbruck", "country": "Austria", "latitude": 47.2692, "longitude": 11.4041, "timezone": "Europe/Vienna"},
    {"name": "Salzburg", "country": "Austria", "latitude": 47.8095, "longitude": 13.0550, "timezone": "Europe/Vienna"},
    {"name": "Graz", "country": "Austria", "latitude": 47.0707, "longitude": 15.4395, "timezone": "Europe/Vienna"},
    {"name": "Krakow", "country": "Poland", "latitude": 50.0647, "longitude": 19.9450, "timezone": "Europe/Warsaw"},
    {"name": "Gdansk", "country": "Poland", "latitude": 54.3520, "longitude": 18.6466, "timezone": "Europe/Warsaw"},
    {"name": "Wroclaw", "country": "Poland", "latitude": 51.1079, "longitude": 17.0385, "timezone": "Europe/Warsaw"},
    {"name": "Bratislava", "country": "Slovakia", "latitude": 48.1486, "longitude": 17.1077, "timezone": "Europe/Bratislava"},
    {"name": "Ljubljana", "country": "Slovenia", "latitude": 46.0569, "longitude": 14.5058, "timezone": "Europe/Ljubljana"},
    {"name": "Minsk", "country": "Belarus", "latitude": 53.9006, "longitude": 27.5590, "timezone": "Europe/Minsk"},

    # =========================================================================
    # Europe — Balkans & Southeast
    # =========================================================================
    {"name": "Athens", "country": "Greece", "latitude": 37.9838, "longitude": 23.7275, "timezone": "Europe/Athens"},
    {"name": "Istanbul", "country": "Turkey", "latitude": 41.0082, "longitude": 28.9784, "timezone": "Europe/Istanbul"},
    {"name": "Zagreb", "country": "Croatia", "latitude": 45.8150, "longitude": 15.9819, "timezone": "Europe/Zagreb"},
    {"name": "Belgrade", "country": "Serbia", "latitude": 44.7866, "longitude": 20.4489, "timezone": "Europe/Belgrade"},
    {"name": "Sofia", "country": "Bulgaria", "latitude": 42.6977, "longitude": 23.3219, "timezone": "Europe/Sofia"},
    {"name": "Skopje", "country": "North Macedonia", "latitude": 41.9973, "longitude": 21.4280, "timezone": "Europe/Skopje"},
    {"name": "Tirana", "country": "Albania", "latitude": 41.3275, "longitude": 19.8187, "timezone": "Europe/Tirane"},
    {"name": "Podgorica", "country": "Montenegro", "latitude": 42.4304, "longitude": 19.2594, "timezone": "Europe/Podgorica"},
    {"name": "Sarajevo", "country": "Bosnia and Herzegovina", "latitude": 43.8563, "longitude": 18.4131, "timezone": "Europe/Sarajevo"},
    {"name": "Nicosia", "country": "Cyprus", "latitude": 35.1856, "longitude": 33.3823, "timezone": "Asia/Nicosia"},
    {"name": "Valletta", "country": "Malta", "latitude": 35.8989, "longitude": 14.5146, "timezone": "Europe/Malta"},

    # =========================================================================
    # Europe — Eastern (Russia, Ukraine, Caucasus)
    # =========================================================================
    {"name": "Moscow", "country": "Russia", "latitude": 55.7558, "longitude": 37.6173, "timezone": "Europe/Moscow"},
    {"name": "St. Petersburg", "country": "Russia", "latitude": 59.9343, "longitude": 30.3351, "timezone": "Europe/Moscow"},
    {"name": "Kyiv", "country": "Ukraine", "latitude": 50.4501, "longitude": 30.5234, "timezone": "Europe/Kyiv"},
    {"name": "Lviv", "country": "Ukraine", "latitude": 49.8397, "longitude": 24.0297, "timezone": "Europe/Kyiv"},
    {"name": "Odessa", "country": "Ukraine", "latitude": 46.4825, "longitude": 30.7233, "timezone": "Europe/Kyiv"},
    {"name": "Tbilisi", "country": "Georgia", "latitude": 41.7151, "longitude": 44.8271, "timezone": "Asia/Tbilisi"},
    {"name": "Yerevan", "country": "Armenia", "latitude": 40.1792, "longitude": 44.4991, "timezone": "Asia/Yerevan"},
    {"name": "Baku", "country": "Azerbaijan", "latitude": 40.4093, "longitude": 49.8671, "timezone": "Asia/Baku"},

    # =========================================================================
    # Middle East
    # =========================================================================
    {"name": "Dubai", "country": "UAE", "latitude": 25.2048, "longitude": 55.2708, "timezone": "Asia/Dubai"},
    {"name": "Riyadh", "country": "Saudi Arabia", "latitude": 24.7136, "longitude": 46.6753, "timezone": "Asia/Riyadh"},
    {"name": "Tel Aviv", "country": "Israel", "latitude": 32.0853, "longitude": 34.7818, "timezone": "Asia/Jerusalem"},
    {"name": "Doha", "country": "Qatar", "latitude": 25.2854, "longitude": 51.5310, "timezone": "Asia/Qatar"},
    {"name": "Kuwait City", "country": "Kuwait", "latitude": 29.3759, "longitude": 47.9774, "timezone": "Asia/Kuwait"},
    {"name": "Muscat", "country": "Oman", "latitude": 23.5880, "longitude": 58.3829, "timezone": "Asia/Muscat"},
    {"name": "Manama", "country": "Bahrain", "latitude": 26.2285, "longitude": 50.5860, "timezone": "Asia/Bahrain"},
    {"name": "Amman", "country": "Jordan", "latitude": 31.9454, "longitude": 35.9284, "timezone": "Asia/Amman"},
    {"name": "Beirut", "country": "Lebanon", "latitude": 33.8938, "longitude": 35.5018, "timezone": "Asia/Beirut"},
    {"name": "Damascus", "country": "Syria", "latitude": 33.5138, "longitude": 36.2765, "timezone": "Asia/Damascus"},
    {"name": "Baghdad", "country": "Iraq", "latitude": 33.3152, "longitude": 44.3661, "timezone": "Asia/Baghdad"},
    {"name": "Tehran", "country": "Iran", "latitude": 35.6892, "longitude": 51.3890, "timezone": "Asia/Tehran"},
    {"name": "Isfahan", "country": "Iran", "latitude": 32.6546, "longitude": 51.6680, "timezone": "Asia/Tehran"},
    {"name": "Tabriz", "country": "Iran", "latitude": 38.0800, "longitude": 46.2919, "timezone": "Asia/Tehran"},
    {"name": "Ankara", "country": "Turkey", "latitude": 39.9334, "longitude": 32.8597, "timezone": "Europe/Istanbul"},
    {"name": "Izmir", "country": "Turkey", "latitude": 38.4237, "longitude": 27.1428, "timezone": "Europe/Istanbul"},

    # =========================================================================
    # Central Asia
    # =========================================================================
    {"name": "Tashkent", "country": "Uzbekistan", "latitude": 41.2995, "longitude": 69.2401, "timezone": "Asia/Tashkent"},
    {"name": "Almaty", "country": "Kazakhstan", "latitude": 43.2220, "longitude": 76.8512, "timezone": "Asia/Almaty"},
    {"name": "Astana", "country": "Kazakhstan", "latitude": 51.1694, "longitude": 71.4491, "timezone": "Asia/Almaty"},
    {"name": "Bishkek", "country": "Kyrgyzstan", "latitude": 42.8746, "longitude": 74.5698, "timezone": "Asia/Bishkek"},
    {"name": "Dushanbe", "country": "Tajikistan", "latitude": 38.5598, "longitude": 68.7740, "timezone": "Asia/Dushanbe"},
    {"name": "Ashgabat", "country": "Turkmenistan", "latitude": 37.9601, "longitude": 58.3261, "timezone": "Asia/Ashgabat"},
    {"name": "Ulaanbaatar", "country": "Mongolia", "latitude": 47.8864, "longitude": 106.9057, "timezone": "Asia/Ulaanbaatar"},
    {"name": "Kabul", "country": "Afghanistan", "latitude": 34.5553, "longitude": 69.2075, "timezone": "Asia/Kabul"},

    # =========================================================================
    # South Asia
    # =========================================================================
    {"name": "Mumbai", "country": "India", "latitude": 19.0760, "longitude": 72.8777, "timezone": "Asia/Kolkata"},
    {"name": "Delhi", "country": "India", "latitude": 28.7041, "longitude": 77.1025, "timezone": "Asia/Kolkata"},
    {"name": "Bangalore", "country": "India", "latitude": 12.9716, "longitude": 77.5946, "timezone": "Asia/Kolkata"},
    {"name": "Chennai", "country": "India", "latitude": 13.0827, "longitude": 80.2707, "timezone": "Asia/Kolkata"},
    {"name": "Hyderabad", "country": "India", "latitude": 17.3850, "longitude": 78.4867, "timezone": "Asia/Kolkata"},
    {"name": "Kolkata", "country": "India", "latitude": 22.5726, "longitude": 88.3639, "timezone": "Asia/Kolkata"},
    {"name": "Ahmedabad", "country": "India", "latitude": 23.0225, "longitude": 72.5714, "timezone": "Asia/Kolkata"},
    {"name": "Pune", "country": "India", "latitude": 18.5204, "longitude": 73.8567, "timezone": "Asia/Kolkata"},
    {"name": "Jaipur", "country": "India", "latitude": 26.9124, "longitude": 75.7873, "timezone": "Asia/Kolkata"},
    {"name": "Lucknow", "country": "India", "latitude": 26.8467, "longitude": 80.9462, "timezone": "Asia/Kolkata"},
    {"name": "Chandigarh", "country": "India", "latitude": 30.7333, "longitude": 76.7794, "timezone": "Asia/Kolkata"},
    {"name": "Kochi", "country": "India", "latitude": 9.9312, "longitude": 76.2673, "timezone": "Asia/Kolkata"},
    {"name": "Surat", "country": "India", "latitude": 21.1702, "longitude": 72.8311, "timezone": "Asia/Kolkata"},
    {"name": "Karachi", "country": "Pakistan", "latitude": 24.8607, "longitude": 67.0011, "timezone": "Asia/Karachi"},
    {"name": "Lahore", "country": "Pakistan", "latitude": 31.5204, "longitude": 74.3587, "timezone": "Asia/Karachi"},
    {"name": "Islamabad", "country": "Pakistan", "latitude": 33.6844, "longitude": 73.0479, "timezone": "Asia/Karachi"},
    {"name": "Peshawar", "country": "Pakistan", "latitude": 34.0151, "longitude": 71.5249, "timezone": "Asia/Karachi"},
    {"name": "Dhaka", "country": "Bangladesh", "latitude": 23.8103, "longitude": 90.4125, "timezone": "Asia/Dhaka"},
    {"name": "Chittagong", "country": "Bangladesh", "latitude": 22.3569, "longitude": 91.7832, "timezone": "Asia/Dhaka"},
    {"name": "Colombo", "country": "Sri Lanka", "latitude": 6.9271, "longitude": 79.8612, "timezone": "Asia/Colombo"},
    {"name": "Kathmandu", "country": "Nepal", "latitude": 27.7172, "longitude": 85.3240, "timezone": "Asia/Kathmandu"},
    {"name": "Thimphu", "country": "Bhutan", "latitude": 27.4728, "longitude": 89.6390, "timezone": "Asia/Thimphu"},

    # =========================================================================
    # East Asia
    # =========================================================================
    {"name": "Tokyo", "country": "Japan", "latitude": 35.6762, "longitude": 139.6503, "timezone": "Asia/Tokyo"},
    {"name": "Beijing", "country": "China", "latitude": 39.9042, "longitude": 116.4074, "timezone": "Asia/Shanghai"},
    {"name": "Shanghai", "country": "China", "latitude": 31.2304, "longitude": 121.4737, "timezone": "Asia/Shanghai"},
    {"name": "Hong Kong", "country": "China", "latitude": 22.3193, "longitude": 114.1694, "timezone": "Asia/Hong_Kong"},
    {"name": "Seoul", "country": "South Korea", "latitude": 37.5665, "longitude": 126.9780, "timezone": "Asia/Seoul"},
    {"name": "Taipei", "country": "Taiwan", "latitude": 25.0330, "longitude": 121.5654, "timezone": "Asia/Taipei"},
    {"name": "Osaka", "country": "Japan", "latitude": 34.6937, "longitude": 135.5023, "timezone": "Asia/Tokyo"},
    {"name": "Kyoto", "country": "Japan", "latitude": 35.0116, "longitude": 135.7681, "timezone": "Asia/Tokyo"},
    {"name": "Nagoya", "country": "Japan", "latitude": 35.1815, "longitude": 136.9066, "timezone": "Asia/Tokyo"},
    {"name": "Sapporo", "country": "Japan", "latitude": 43.0618, "longitude": 141.3545, "timezone": "Asia/Tokyo"},
    {"name": "Fukuoka", "country": "Japan", "latitude": 33.5904, "longitude": 130.4017, "timezone": "Asia/Tokyo"},
    {"name": "Guangzhou", "country": "China", "latitude": 23.1291, "longitude": 113.2644, "timezone": "Asia/Shanghai"},
    {"name": "Shenzhen", "country": "China", "latitude": 22.5431, "longitude": 114.0579, "timezone": "Asia/Shanghai"},
    {"name": "Chengdu", "country": "China", "latitude": 30.5728, "longitude": 104.0668, "timezone": "Asia/Shanghai"},
    {"name": "Wuhan", "country": "China", "latitude": 30.5928, "longitude": 114.3055, "timezone": "Asia/Shanghai"},
    {"name": "Nanjing", "country": "China", "latitude": 32.0603, "longitude": 118.7969, "timezone": "Asia/Shanghai"},
    {"name": "Xi'an", "country": "China", "latitude": 34.3416, "longitude": 108.9398, "timezone": "Asia/Shanghai"},
    {"name": "Hangzhou", "country": "China", "latitude": 30.2741, "longitude": 120.1551, "timezone": "Asia/Shanghai"},
    {"name": "Busan", "country": "South Korea", "latitude": 35.1796, "longitude": 129.0756, "timezone": "Asia/Seoul"},
    {"name": "Incheon", "country": "South Korea", "latitude": 37.4563, "longitude": 126.7052, "timezone": "Asia/Seoul"},
    {"name": "Kaohsiung", "country": "Taiwan", "latitude": 22.6273, "longitude": 120.3014, "timezone": "Asia/Taipei"},
    {"name": "Macau", "country": "China", "latitude": 22.1987, "longitude": 113.5439, "timezone": "Asia/Macau"},

    # =========================================================================
    # Southeast Asia
    # =========================================================================
    {"name": "Bangkok", "country": "Thailand", "latitude": 13.7563, "longitude": 100.5018, "timezone": "Asia/Bangkok"},
    {"name": "Singapore", "country": "Singapore", "latitude": 1.3521, "longitude": 103.8198, "timezone": "Asia/Singapore"},
    {"name": "Jakarta", "country": "Indonesia", "latitude": -6.2088, "longitude": 106.8456, "timezone": "Asia/Jakarta"},
    {"name": "Kuala Lumpur", "country": "Malaysia", "latitude": 3.1390, "longitude": 101.6869, "timezone": "Asia/Kuala_Lumpur"},
    {"name": "Manila", "country": "Philippines", "latitude": 14.5995, "longitude": 120.9842, "timezone": "Asia/Manila"},
    {"name": "Hanoi", "country": "Vietnam", "latitude": 21.0278, "longitude": 105.8342, "timezone": "Asia/Ho_Chi_Minh"},
    {"name": "Ho Chi Minh City", "country": "Vietnam", "latitude": 10.8231, "longitude": 106.6297, "timezone": "Asia/Ho_Chi_Minh"},
    {"name": "Phnom Penh", "country": "Cambodia", "latitude": 11.5564, "longitude": 104.9282, "timezone": "Asia/Phnom_Penh"},
    {"name": "Vientiane", "country": "Laos", "latitude": 17.9757, "longitude": 102.6331, "timezone": "Asia/Vientiane"},
    {"name": "Yangon", "country": "Myanmar", "latitude": 16.8661, "longitude": 96.1951, "timezone": "Asia/Yangon"},
    {"name": "Cebu", "country": "Philippines", "latitude": 10.3157, "longitude": 123.8854, "timezone": "Asia/Manila"},
    {"name": "Surabaya", "country": "Indonesia", "latitude": -7.2575, "longitude": 112.7521, "timezone": "Asia/Jakarta"},
    {"name": "Denpasar", "country": "Indonesia", "latitude": -8.6705, "longitude": 115.2126, "timezone": "Asia/Makassar"},
    {"name": "Chiang Mai", "country": "Thailand", "latitude": 18.7883, "longitude": 98.9853, "timezone": "Asia/Bangkok"},
    {"name": "Phuket", "country": "Thailand", "latitude": 7.8804, "longitude": 98.3923, "timezone": "Asia/Bangkok"},

    # =========================================================================
    # Africa — North
    # =========================================================================
    {"name": "Cairo", "country": "Egypt", "latitude": 30.0444, "longitude": 31.2357, "timezone": "Africa/Cairo"},
    {"name": "Casablanca", "country": "Morocco", "latitude": 33.5731, "longitude": -7.5898, "timezone": "Africa/Casablanca"},
    {"name": "Tunis", "country": "Tunisia", "latitude": 36.8065, "longitude": 10.1815, "timezone": "Africa/Tunis"},
    {"name": "Algiers", "country": "Algeria", "latitude": 36.7538, "longitude": 3.0588, "timezone": "Africa/Algiers"},
    {"name": "Tripoli", "country": "Libya", "latitude": 32.8872, "longitude": 13.1913, "timezone": "Africa/Tripoli"},
    {"name": "Khartoum", "country": "Sudan", "latitude": 15.5007, "longitude": 32.5599, "timezone": "Africa/Khartoum"},

    # =========================================================================
    # Africa — West
    # =========================================================================
    {"name": "Lagos", "country": "Nigeria", "latitude": 6.5244, "longitude": 3.3792, "timezone": "Africa/Lagos"},
    {"name": "Accra", "country": "Ghana", "latitude": 5.6037, "longitude": -0.1870, "timezone": "Africa/Accra"},
    {"name": "Abidjan", "country": "Côte d'Ivoire", "latitude": 5.3600, "longitude": -4.0083, "timezone": "Africa/Abidjan"},
    {"name": "Dakar", "country": "Senegal", "latitude": 14.7167, "longitude": -17.4677, "timezone": "Africa/Dakar"},
    {"name": "Bamako", "country": "Mali", "latitude": 12.6392, "longitude": -8.0029, "timezone": "Africa/Bamako"},
    {"name": "Ouagadougou", "country": "Burkina Faso", "latitude": 12.3714, "longitude": -1.5197, "timezone": "Africa/Ouagadougou"},
    {"name": "Niamey", "country": "Niger", "latitude": 13.5127, "longitude": 2.1128, "timezone": "Africa/Niamey"},
    {"name": "Conakry", "country": "Guinea", "latitude": 9.6412, "longitude": -13.5784, "timezone": "Africa/Conakry"},
    {"name": "Freetown", "country": "Sierra Leone", "latitude": 8.4657, "longitude": -13.2317, "timezone": "Africa/Freetown"},
    {"name": "Monrovia", "country": "Liberia", "latitude": 6.2907, "longitude": -10.7605, "timezone": "Africa/Monrovia"},

    # =========================================================================
    # Africa — Central
    # =========================================================================
    {"name": "Kinshasa", "country": "DR Congo", "latitude": -4.4419, "longitude": 15.2663, "timezone": "Africa/Kinshasa"},
    {"name": "Brazzaville", "country": "Congo", "latitude": -4.2634, "longitude": 15.2429, "timezone": "Africa/Brazzaville"},
    {"name": "Douala", "country": "Cameroon", "latitude": 4.0511, "longitude": 9.7679, "timezone": "Africa/Douala"},
    {"name": "Yaoundé", "country": "Cameroon", "latitude": 3.8480, "longitude": 11.5021, "timezone": "Africa/Douala"},
    {"name": "N'Djamena", "country": "Chad", "latitude": 12.1348, "longitude": 15.0557, "timezone": "Africa/Ndjamena"},
    {"name": "Libreville", "country": "Gabon", "latitude": 0.4162, "longitude": 9.4673, "timezone": "Africa/Libreville"},

    # =========================================================================
    # Africa — East
    # =========================================================================
    {"name": "Nairobi", "country": "Kenya", "latitude": -1.2921, "longitude": 36.8219, "timezone": "Africa/Nairobi"},
    {"name": "Addis Ababa", "country": "Ethiopia", "latitude": 9.0250, "longitude": 38.7469, "timezone": "Africa/Addis_Ababa"},
    {"name": "Dar es Salaam", "country": "Tanzania", "latitude": -6.7924, "longitude": 39.2083, "timezone": "Africa/Dar_es_Salaam"},
    {"name": "Kampala", "country": "Uganda", "latitude": 0.3476, "longitude": 32.5825, "timezone": "Africa/Kampala"},
    {"name": "Kigali", "country": "Rwanda", "latitude": -1.9403, "longitude": 29.8739, "timezone": "Africa/Kigali"},
    {"name": "Zanzibar", "country": "Tanzania", "latitude": -6.1659, "longitude": 39.2026, "timezone": "Africa/Dar_es_Salaam"},
    {"name": "Antananarivo", "country": "Madagascar", "latitude": -18.8792, "longitude": 47.5079, "timezone": "Indian/Antananarivo"},
    {"name": "Port Louis", "country": "Mauritius", "latitude": -20.1609, "longitude": 57.5012, "timezone": "Indian/Mauritius"},

    # =========================================================================
    # Africa — Southern
    # =========================================================================
    {"name": "Johannesburg", "country": "South Africa", "latitude": -26.2041, "longitude": 28.0473, "timezone": "Africa/Johannesburg"},
    {"name": "Cape Town", "country": "South Africa", "latitude": -33.9249, "longitude": 18.4241, "timezone": "Africa/Johannesburg"},
    {"name": "Lusaka", "country": "Zambia", "latitude": -15.3875, "longitude": 28.3228, "timezone": "Africa/Lusaka"},
    {"name": "Harare", "country": "Zimbabwe", "latitude": -17.8252, "longitude": 31.0335, "timezone": "Africa/Harare"},
    {"name": "Maputo", "country": "Mozambique", "latitude": -25.9692, "longitude": 32.5732, "timezone": "Africa/Maputo"},
    {"name": "Luanda", "country": "Angola", "latitude": -8.8390, "longitude": 13.2894, "timezone": "Africa/Luanda"},
    {"name": "Windhoek", "country": "Namibia", "latitude": -22.5609, "longitude": 17.0658, "timezone": "Africa/Windhoek"},
    {"name": "Gaborone", "country": "Botswana", "latitude": -24.6282, "longitude": 25.9231, "timezone": "Africa/Gaborone"},

    # =========================================================================
    # Oceania & Pacific
    # =========================================================================
    {"name": "Sydney", "country": "Australia", "latitude": -33.8688, "longitude": 151.2093, "timezone": "Australia/Sydney"},
    {"name": "Melbourne", "country": "Australia", "latitude": -37.8136, "longitude": 144.9631, "timezone": "Australia/Melbourne"},
    {"name": "Brisbane", "country": "Australia", "latitude": -27.4698, "longitude": 153.0251, "timezone": "Australia/Brisbane"},
    {"name": "Perth", "country": "Australia", "latitude": -31.9505, "longitude": 115.8605, "timezone": "Australia/Perth"},
    {"name": "Auckland", "country": "New Zealand", "latitude": -36.8485, "longitude": 174.7633, "timezone": "Pacific/Auckland"},
    {"name": "Adelaide", "country": "Australia", "latitude": -34.9285, "longitude": 138.6007, "timezone": "Australia/Adelaide"},
    {"name": "Canberra", "country": "Australia", "latitude": -35.2809, "longitude": 149.1300, "timezone": "Australia/Sydney"},
    {"name": "Gold Coast", "country": "Australia", "latitude": -28.0167, "longitude": 153.4000, "timezone": "Australia/Brisbane"},
    {"name": "Wellington", "country": "New Zealand", "latitude": -41.2866, "longitude": 174.7756, "timezone": "Pacific/Auckland"},
    {"name": "Christchurch", "country": "New Zealand", "latitude": -43.5321, "longitude": 172.6362, "timezone": "Pacific/Auckland"},
    {"name": "Suva", "country": "Fiji", "latitude": -18.1416, "longitude": 178.4419, "timezone": "Pacific/Fiji"},
    {"name": "Apia", "country": "Samoa", "latitude": -13.8333, "longitude": -171.7500, "timezone": "Pacific/Apia"},
    {"name": "Nouméa", "country": "New Caledonia", "latitude": -22.2558, "longitude": 166.4505, "timezone": "Pacific/Noumea"},
    {"name": "Port Moresby", "country": "Papua New Guinea", "latitude": -6.3149, "longitude": 143.9556, "timezone": "Pacific/Port_Moresby"},
    {"name": "Papeete", "country": "French Polynesia", "latitude": -17.5516, "longitude": -149.5585, "timezone": "Pacific/Tahiti"},
]


def search_cities(query: str = "", limit: int = 20) -> list:
    """
    Search cities by name or country.
    Returns all cities if query is empty, otherwise filters by case-insensitive match.
    Results are ranked: prefix matches on name first, then contains matches on name,
    then country matches — giving better autocomplete behavior.
    """
    if not query:
        return CITIES[:limit]

    q = query.lower()

    prefix_name = []
    contains_name = []
    country_match = []

    for city in CITIES:
        name_lower = city["name"].lower()
        if name_lower.startswith(q):
            prefix_name.append(city)
        elif q in name_lower:
            contains_name.append(city)
        elif q in city["country"].lower():
            country_match.append(city)

    results = prefix_name + contains_name + country_match
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


# ============== Mapbox Geocoding API ==============


def _mapbox_geocode(query: str, limit: int = 10) -> list:
    """
    Search for places using the Mapbox Geocoding API.
    Returns a list of city dicts in the same format as the static database.
    Only queries for 'place' types (cities/towns) — not street addresses.

    Note: Mapbox geocoding does not return timezone info. The 'timezone' field
    will be empty for API results. Timezone can be derived from coordinates
    when needed (e.g., via timezonefinder or a separate Mapbox Tilequery).
    """
    if not MAPBOX_ACCESS_TOKEN:
        return []

    try:
        url = "https://api.mapbox.com/geocoding/v5/mapbox.places/" + requests.utils.quote(query) + ".json"
        params = {
            "access_token": MAPBOX_ACCESS_TOKEN,
            "types": "place",
            "limit": min(limit, 10),
            "language": "en",
        }
        resp = requests.get(url, params=params, timeout=3)
        resp.raise_for_status()
        data = resp.json()

        results = []
        for feature in data.get("features", []):
            # Extract country from context
            country = ""
            for ctx in feature.get("context", []):
                if ctx.get("id", "").startswith("country"):
                    country = ctx.get("text", "")
                    break

            # Mapbox returns [longitude, latitude]
            coords = feature.get("center", [0, 0])

            results.append({
                "name": feature.get("text", ""),
                "country": country,
                "latitude": round(coords[1], 4),
                "longitude": round(coords[0], 4),
                "timezone": "",  # Mapbox doesn't return timezone in geocoding
            })

        return results
    except Exception as e:
        logger.warning(f"Mapbox geocoding failed: {e}")
        return []


def geocode_search(query: str = "", limit: int = 20) -> list:
    """
    Hybrid city search: uses Mapbox API when available, falls back to static database.
    This is the function the API endpoint should call.
    """
    if not query:
        return CITIES[:limit]

    # If Mapbox is configured, use it for real geocoding
    if MAPBOX_ACCESS_TOKEN:
        results = _mapbox_geocode(query, limit=limit)
        if results:
            return results

    # Fallback to static database
    return search_cities(query, limit=limit)


def geocode_lookup(place_name: str) -> dict | None:
    """
    Look up a single place by name. Returns coordinates.
    Uses Mapbox if available, falls back to static database.
    """
    # Try static database first (fastest, no API call)
    parts = [p.strip() for p in place_name.split(",", 1)]
    city_name = parts[0]
    city_country = parts[1] if len(parts) > 1 else ""
    static = find_city(city_name, city_country)
    if static:
        return static

    # Try Mapbox for places not in our static database
    if MAPBOX_ACCESS_TOKEN:
        results = _mapbox_geocode(place_name, limit=1)
        if results:
            return results[0]

    return None
