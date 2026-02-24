"""
Gab44 Numerology Engine
========================
Calculates numerological profiles using the Pythagorean method.

Numbers calculated:
- Life Path Number (from birth date)
- Expression Number (from full name)
- Soul Urge Number (from vowels in name)
- Personality Number (from consonants in name)
- Birthday Number (from birth day)
- Personal Year Number (from birth date + current year)

Master Numbers (11, 22, 33) are preserved throughout all calculations.
"""

from datetime import datetime


# Pythagorean letter-to-number mapping
PYTHAGOREAN_MAP = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8
}

VOWELS = set('AEIOU')

MASTER_NUMBERS = {11, 22, 33}


def _reduce_to_single_digit(n: int) -> int:
    """Reduce a number to a single digit, preserving Master Numbers (11, 22, 33)."""
    while n > 9 and n not in MASTER_NUMBERS:
        n = sum(int(d) for d in str(n))
    return n


def _digit_sum(n: int) -> int:
    """Sum the digits of a number once."""
    return sum(int(d) for d in str(n))


def _name_to_numbers(name: str) -> list:
    """Convert a name to its Pythagorean number values (letters only)."""
    return [PYTHAGOREAN_MAP[ch] for ch in name.upper() if ch in PYTHAGOREAN_MAP]


def calculate_life_path(birth_date: str) -> dict:
    """
    Calculate Life Path Number from birth date (YYYY-MM-DD).
    Each component (month, day, year) is reduced separately, then summed and reduced.
    """
    dt = datetime.strptime(birth_date, "%Y-%m-%d")
    month = _reduce_to_single_digit(_digit_sum(dt.month))
    day = _reduce_to_single_digit(_digit_sum(dt.day))
    year = _reduce_to_single_digit(sum(int(d) for d in str(dt.year)))

    total = month + day + year
    life_path = _reduce_to_single_digit(total)

    return {
        "number": life_path,
        "breakdown": {
            "month": dt.month,
            "month_reduced": month,
            "day": dt.day,
            "day_reduced": day,
            "year": dt.year,
            "year_reduced": year,
            "total": total,
        },
        "meaning": LIFE_PATH_MEANINGS.get(life_path, ""),
    }


def calculate_expression(full_name: str) -> dict:
    """
    Calculate Expression Number from full name (all letters).
    """
    values = _name_to_numbers(full_name)
    total = sum(values)
    number = _reduce_to_single_digit(total)

    return {
        "number": number,
        "total": total,
        "letter_values": _letter_breakdown(full_name),
        "meaning": EXPRESSION_MEANINGS.get(number, ""),
    }


def calculate_soul_urge(full_name: str) -> dict:
    """
    Calculate Soul Urge Number from vowels in full name.
    """
    values = [PYTHAGOREAN_MAP[ch] for ch in full_name.upper() if ch in VOWELS]
    total = sum(values)
    number = _reduce_to_single_digit(total)

    return {
        "number": number,
        "total": total,
        "vowels": [ch for ch in full_name.upper() if ch in VOWELS],
        "meaning": SOUL_URGE_MEANINGS.get(number, ""),
    }


def calculate_personality(full_name: str) -> dict:
    """
    Calculate Personality Number from consonants in full name.
    """
    values = [
        PYTHAGOREAN_MAP[ch]
        for ch in full_name.upper()
        if ch in PYTHAGOREAN_MAP and ch not in VOWELS
    ]
    total = sum(values)
    number = _reduce_to_single_digit(total)

    return {
        "number": number,
        "total": total,
        "consonants": [
            ch for ch in full_name.upper()
            if ch in PYTHAGOREAN_MAP and ch not in VOWELS
        ],
        "meaning": PERSONALITY_MEANINGS.get(number, ""),
    }


def calculate_birthday(birth_date: str) -> dict:
    """
    Calculate Birthday Number from the day of birth.
    """
    dt = datetime.strptime(birth_date, "%Y-%m-%d")
    number = _reduce_to_single_digit(dt.day)

    return {
        "number": number,
        "day": dt.day,
        "meaning": BIRTHDAY_MEANINGS.get(number, ""),
    }


def calculate_personal_year(birth_date: str, year: int = None) -> dict:
    """
    Calculate Personal Year Number.
    Formula: birth month + birth day + current year, reduced.
    """
    dt = datetime.strptime(birth_date, "%Y-%m-%d")
    if year is None:
        year = datetime.now().year

    month = _reduce_to_single_digit(_digit_sum(dt.month))
    day = _reduce_to_single_digit(_digit_sum(dt.day))
    yr = _reduce_to_single_digit(sum(int(d) for d in str(year)))

    total = month + day + yr
    number = _reduce_to_single_digit(total)

    return {
        "number": number,
        "year": year,
        "meaning": PERSONAL_YEAR_MEANINGS.get(number, ""),
    }


def _letter_breakdown(name: str) -> list:
    """Return letter-by-letter Pythagorean breakdown."""
    result = []
    for ch in name.upper():
        if ch in PYTHAGOREAN_MAP:
            result.append({"letter": ch, "value": PYTHAGOREAN_MAP[ch]})
        elif ch == ' ':
            result.append({"letter": " ", "value": 0})
    return result


def calculate_full_profile(full_name: str, birth_date: str) -> dict:
    """
    Calculate the complete numerology profile.
    """
    return {
        "name": full_name,
        "birth_date": birth_date,
        "life_path": calculate_life_path(birth_date),
        "expression": calculate_expression(full_name),
        "soul_urge": calculate_soul_urge(full_name),
        "personality": calculate_personality(full_name),
        "birthday": calculate_birthday(birth_date),
        "personal_year": calculate_personal_year(birth_date),
    }


# ================= Meanings =================

LIFE_PATH_MEANINGS = {
    1: "The Leader — Independent, ambitious, and pioneering. You are here to develop individuality and self-reliance. Trust your instincts and lead with courage.",
    2: "The Diplomat — Cooperative, sensitive, and balanced. You are here to bring harmony and partnership. Your strength lies in patience and understanding.",
    3: "The Communicator — Creative, expressive, and joyful. You are here to inspire and uplift others through your words and artistic gifts.",
    4: "The Builder — Practical, disciplined, and hardworking. You are here to create lasting structures and foundations. Stability is your superpower.",
    5: "The Adventurer — Dynamic, versatile, and freedom-loving. You are here to experience life fully and embrace change as your teacher.",
    6: "The Nurturer — Responsible, caring, and community-minded. You are here to serve, heal, and create beauty in the lives of those around you.",
    7: "The Seeker — Analytical, introspective, and spiritual. You are here to seek truth and wisdom. Solitude and study fuel your deepest growth.",
    8: "The Powerhouse — Ambitious, authoritative, and materially focused. You are here to master the material world and use abundance for good.",
    9: "The Humanitarian — Compassionate, idealistic, and wise. You are here to serve humanity and complete karmic cycles with grace.",
    11: "Master Number 11: The Visionary — Highly intuitive, inspiring, and spiritually aware. You carry a higher vibration and are here to illuminate and uplift.",
    22: "Master Number 22: The Master Builder — Visionary and practical. You can turn the most ambitious dreams into reality. You build for the benefit of all.",
    33: "Master Number 33: The Master Teacher — The most spiritually evolved path. You embody selfless love and are here to raise the consciousness of humanity.",
}

EXPRESSION_MEANINGS = {
    1: "Your natural talents lean toward leadership, originality, and independence. You express yourself best when pioneering new paths.",
    2: "You are naturally diplomatic, cooperative, and detail-oriented. Your talents shine in partnerships and supportive roles.",
    3: "Your expression is creative, communicative, and joyful. You have natural gifts in writing, speaking, and the arts.",
    4: "You express through structure, reliability, and hard work. Building systems and creating order comes naturally to you.",
    5: "Your expression is versatile, adventurous, and magnetic. You thrive on variety and communicate with charisma.",
    6: "You express through nurturing, responsibility, and harmony. Home, family, and community are central to your purpose.",
    7: "Your expression is intellectual, analytical, and spiritual. Research, investigation, and deep thinking are your strengths.",
    8: "You express through ambition, authority, and material mastery. Business acumen and executive ability come naturally.",
    9: "Your expression is humanitarian, compassionate, and artistic. You inspire others through selfless service and creative vision.",
    11: "Master Expression 11: Highly intuitive and inspirational. You express through vision, spiritual insight, and creative genius.",
    22: "Master Expression 22: You have the ability to manifest grand visions into reality. A natural architect of large-scale endeavors.",
    33: "Master Expression 33: You express through profound compassion and teaching. Your influence uplifts and heals on a deep level.",
}

SOUL_URGE_MEANINGS = {
    1: "Your heart desires independence, achievement, and to be first. You are driven by a need to lead and stand on your own.",
    2: "Your heart desires love, partnership, and peace. You long for deep emotional connections and harmony.",
    3: "Your heart desires joy, self-expression, and creativity. You crave outlets for your imagination and social connections.",
    4: "Your heart desires stability, order, and accomplishment. You find fulfillment in building something lasting.",
    5: "Your heart desires freedom, adventure, and sensory experience. You long for variety and resist being confined.",
    6: "Your heart desires love, family, and to be of service. Creating a beautiful, harmonious home fulfills you deeply.",
    7: "Your heart desires knowledge, solitude, and spiritual truth. Inner peace comes through understanding life's mysteries.",
    8: "Your heart desires success, recognition, and financial abundance. You are driven to achieve and have authority.",
    9: "Your heart desires to make the world a better place. Compassion, idealism, and universal love guide your inner life.",
    11: "Master Soul Urge 11: Your heart yearns for spiritual enlightenment and to inspire others through intuitive wisdom.",
    22: "Master Soul Urge 22: Your deepest desire is to build something of lasting, global significance.",
    33: "Master Soul Urge 33: Your heart seeks to heal and uplift humanity through unconditional love and selfless service.",
}

PERSONALITY_MEANINGS = {
    1: "Others see you as confident, independent, and assertive. You project strength and originality.",
    2: "Others see you as gentle, approachable, and cooperative. You project warmth and tact.",
    3: "Others see you as charming, witty, and creative. You project enthusiasm and social ease.",
    4: "Others see you as reliable, practical, and grounded. You project stability and trustworthiness.",
    5: "Others see you as dynamic, attractive, and adventurous. You project excitement and magnetism.",
    6: "Others see you as caring, responsible, and warm. You project a nurturing, welcoming presence.",
    7: "Others see you as mysterious, intellectual, and reserved. You project depth and quiet authority.",
    8: "Others see you as powerful, successful, and authoritative. You project confidence and competence.",
    9: "Others see you as compassionate, wise, and worldly. You project a sense of having lived and learned.",
    11: "Master Personality 11: Others see you as deeply intuitive and inspiring. You have an almost otherworldly presence.",
    22: "Master Personality 22: Others see you as capable of achieving the extraordinary. You project mastery and vision.",
    33: "Master Personality 33: Others see you as a beacon of compassion and wisdom. Your presence heals.",
}

BIRTHDAY_MEANINGS = {
    1: "Born on the 1st — You are an innovator and a natural-born leader. Independence defines you.",
    2: "Born on the 2nd — You are a peacemaker with a gift for cooperation and diplomacy.",
    3: "Born on the 3rd — You are naturally creative and expressive. Communication is your forte.",
    4: "Born on the 4th — You are practical, hardworking, and build strong foundations.",
    5: "Born on the 5th — You are versatile, adventurous, and thrive on change.",
    6: "Born on the 6th — You are nurturing, responsible, and drawn to home and family.",
    7: "Born on the 7th — You are analytical, introspective, and spiritually inclined.",
    8: "Born on the 8th — You are ambitious, authoritative, and have strong business sense.",
    9: "Born on the 9th — You are compassionate, idealistic, and drawn to humanitarian causes.",
    11: "Born on the 11th — Master Number: You have heightened intuition and inspirational gifts.",
    22: "Born on the 22nd — Master Number: You are a master builder with the ability to manifest great visions.",
    33: "Born on the 33rd — Master Number: Extremely rare. You embody the highest form of nurturing and teaching.",
}

PERSONAL_YEAR_MEANINGS = {
    1: "A year of new beginnings. Plant seeds, start projects, and assert your independence. Your initiative is rewarded.",
    2: "A year of patience and partnerships. Cooperate, wait for timing, and nurture relationships. Slow and steady wins.",
    3: "A year of creativity and self-expression. Socialize, create, and let your joy shine. Inspiration flows freely.",
    4: "A year of hard work and building. Lay foundations, organize, and commit to your goals. Discipline is key.",
    5: "A year of change and freedom. Embrace new experiences, travel, and release what no longer serves you.",
    6: "A year of home, family, and responsibility. Deepen relationships, beautify your space, and serve your community.",
    7: "A year of introspection and spiritual growth. Study, meditate, and seek deeper understanding. Quality over quantity.",
    8: "A year of power and abundance. Financial opportunities arise. Step into authority and manage resources wisely.",
    9: "A year of completion and release. Let go of what's finished, forgive, and prepare for the next cycle.",
    11: "A Master Year of spiritual awakening. Heightened intuition guides you. Trust your inner vision.",
    22: "A Master Year of manifesting dreams. Build something significant that serves the greater good.",
    33: "A Master Year of compassionate service. Your capacity to heal and uplift others reaches its peak.",
}
