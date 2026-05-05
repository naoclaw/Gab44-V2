"""Markdown formatters for outbound Telegram messages.

Telegram's MarkdownV2 has unforgiving escape rules; we use plain Markdown
(legacy) which is more lenient and renders fine for our needs. Outputs are
always shorter than the 4096-character message cap.
"""
from __future__ import annotations

from typing import Iterable


def format_chart(chart: dict) -> str:
    sun = chart.get("planets", {}).get("Sun", {})
    moon = chart.get("planets", {}).get("Moon", {})
    asc = chart.get("ascendant", {})

    lines = [
        "*Your natal chart* ✨",
        "",
        f"☀️ *Sun* — {sun.get('sign', '—')} {sun.get('degree', '?'):.1f}° in House {sun.get('house', '—')}",
        f"🌙 *Moon* — {moon.get('sign', '—')} {moon.get('degree', '?'):.1f}° in House {moon.get('house', '—')}",
        f"⬆️ *Rising* — {asc.get('sign', '—')} {asc.get('degree', '?'):.1f}°",
    ]
    return "\n".join(lines)


def format_daily_guidance(guidance: dict) -> str:
    energy = guidance.get("overall_energy", "—")
    focus = _bullets(guidance.get("focus_areas", []))
    actions = _bullets(guidance.get("action_items", []))
    transits = _bullets(guidance.get("transit_highlights", []))

    return (
        "*Today's guidance* 🌅\n\n"
        f"*Energy:* {energy}\n\n"
        f"*Focus*\n{focus}\n\n"
        f"*Try*\n{actions}\n\n"
        f"*Transits*\n{transits}"
    )


def format_transits(transits: dict) -> str:
    items = transits.get("transits", [])[:5]
    if not items:
        return "_No upcoming transits in the visible window._"

    lines = ["*Upcoming transits* 🌌", ""]
    for t in items:
        lines.append(
            f"• *{t.get('transiting_planet')}* {t.get('aspect')} natal "
            f"*{t.get('natal_planet')}* — exact in ~{t.get('days_until_exact', '?')} days"
        )
    return "\n".join(lines)


def chunk(text: str, limit: int = 4000) -> list[str]:
    """Split a long message at paragraph boundaries to fit Telegram's 4096 cap."""
    if len(text) <= limit:
        return [text]
    chunks: list[str] = []
    current = ""
    for paragraph in text.split("\n\n"):
        if len(current) + len(paragraph) + 2 > limit:
            chunks.append(current.rstrip())
            current = ""
        current += paragraph + "\n\n"
    if current.strip():
        chunks.append(current.rstrip())
    return chunks


def _bullets(items: Iterable[str]) -> str:
    items = list(items)
    if not items:
        return "—"
    return "\n".join(f"• {item}" for item in items)
