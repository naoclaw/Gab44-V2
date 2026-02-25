"""
Gab44 Gematria Engine
======================
Calculates gematria values using two systems:

1. Chaldean (Babylonian) — A=1..H=8, no 9 (sacred number skipped)
2. English Ordinal — A=1..Z=26

Provides letter-by-letter breakdown and numerical significance.
"""


# Chaldean values: 1-8 (9 is sacred, not assigned to any letter)
CHALDEAN_MAP = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 8, 'G': 3, 'H': 5,
    'I': 1, 'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 7, 'P': 8,
    'Q': 1, 'R': 2, 'S': 3, 'T': 4, 'U': 6, 'V': 6, 'W': 6, 'X': 5,
    'Y': 1, 'Z': 7
}

# English Ordinal: A=1..Z=26
ORDINAL_MAP = {chr(65 + i): i + 1 for i in range(26)}


def _reduce_to_single(n: int) -> int:
    """Reduce to a single digit (no master number preservation for gematria)."""
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def _letter_breakdown(text: str, system_map: dict) -> list:
    """Return letter-by-letter breakdown for a given mapping."""
    result = []
    for ch in text.upper():
        if ch in system_map:
            result.append({"letter": ch, "value": system_map[ch]})
        elif ch == ' ':
            result.append({"letter": " ", "value": 0})
    return result


def _word_values(text: str, system_map: dict) -> list:
    """Calculate per-word totals."""
    words = text.split()
    result = []
    for word in words:
        values = [system_map.get(ch, 0) for ch in word.upper() if ch in system_map]
        total = sum(values)
        result.append({
            "word": word,
            "total": total,
            "reduced": _reduce_to_single(total),
        })
    return result


def calculate_chaldean(text: str) -> dict:
    """
    Calculate Chaldean gematria for a text string.
    """
    letters = _letter_breakdown(text, CHALDEAN_MAP)
    total = sum(item["value"] for item in letters)
    reduced = _reduce_to_single(total)
    words = _word_values(text, CHALDEAN_MAP)

    return {
        "system": "chaldean",
        "text": text,
        "total": total,
        "reduced": reduced,
        "letters": letters,
        "words": words,
        "significance": CHALDEAN_SIGNIFICANCE.get(reduced, ""),
    }


def calculate_ordinal(text: str) -> dict:
    """
    Calculate English Ordinal gematria for a text string.
    """
    letters = _letter_breakdown(text, ORDINAL_MAP)
    total = sum(item["value"] for item in letters)
    reduced = _reduce_to_single(total)
    words = _word_values(text, ORDINAL_MAP)

    return {
        "system": "english_ordinal",
        "text": text,
        "total": total,
        "reduced": reduced,
        "letters": letters,
        "words": words,
        "significance": ORDINAL_SIGNIFICANCE.get(reduced, ""),
    }


def calculate_all(text: str) -> dict:
    """
    Calculate both Chaldean and English Ordinal gematria.
    """
    return {
        "text": text,
        "chaldean": calculate_chaldean(text),
        "english_ordinal": calculate_ordinal(text),
    }


# ================= Significance =================

CHALDEAN_SIGNIFICANCE = {
    1: "The Sun — Leadership, independence, new beginnings. A powerful initiator energy.",
    2: "The Moon — Intuition, partnerships, sensitivity. Receptive and diplomatic.",
    3: "Jupiter — Expansion, creativity, self-expression. Growth through communication.",
    4: "Uranus — Stability, structure, unconventional paths. Building with innovation.",
    5: "Mercury — Change, communication, adaptability. Quick-thinking and versatile.",
    6: "Venus — Love, harmony, responsibility. Beauty and nurturing energy.",
    7: "Neptune — Spirituality, wisdom, introspection. The mystic seeker.",
    8: "Saturn — Power, authority, material success. Mastery through discipline.",
    9: "Mars — Completion, humanitarianism, universal love. The sacred number of endings.",
}

ORDINAL_SIGNIFICANCE = {
    1: "Unity, beginnings, the individual self. The seed of all numbers.",
    2: "Duality, balance, cooperation. The bridge between opposing forces.",
    3: "Trinity, creativity, divine expression. The number of manifestation.",
    4: "Foundation, order, the material world. Stability and endurance.",
    5: "Change, freedom, the five senses. Dynamic transformation.",
    6: "Harmony, love, domestic bliss. The number of the heart.",
    7: "Mystery, spirit, inner wisdom. The seeker of hidden truth.",
    8: "Infinity, power, karmic balance. Material and spiritual mastery.",
    9: "Completion, universal consciousness, selflessness. The end of a cycle.",
}
