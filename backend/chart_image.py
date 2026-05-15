"""
Gab44 birth-chart visual generator.

Renders a natal chart wheel (PNG) and a 1080x1080 share card directly
with Pillow — no SVG / cairo / system deps beyond a TrueType font.

Two render targets:
  render_wheel(...)       -> a clean square natal-wheel PNG (1200x1200)
  render_share_card(...)  -> 1080x1080 social-shareable card with wheel,
                             big-three summary, name, birth info, branding

The chart dict expected matches what /api/chart/me returns:
    {
        "sun_sign", "moon_sign", "rising_sign",
        "planets": { "Sun": {"longitude": float, "sign": str, "retrograde": bool, ...}, ... },
        "houses":  { 1: {"cusp": float, ...}, ..., "ascendant": {"longitude": float}, "midheaven": {...} },
        "aspects": [ {"planet1", "planet2", "aspect", "orb", "type"}, ... ]
    }
"""

from __future__ import annotations

import io
import math
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

# ---------- font discovery ----------
# DejaVu ships on every container we deploy to (Railway/Vercel base images
# both include it). Pillow's truetype loader is happy with absolute paths.
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def _font(size: int, bold: bool = False, serif: bool = False) -> ImageFont.FreeTypeFont:
    path = (
        FONT_SERIF_BOLD if (serif and bold)
        else FONT_SERIF if serif
        else FONT_BOLD if bold
        else FONT_REGULAR
    )
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


# ---------- glyph tables ----------
SIGN_ORDER = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_GLYPH = {
    "Aries": "♈", "Taurus": "♉", "Gemini": "♊", "Cancer": "♋",
    "Leo": "♌", "Virgo": "♍", "Libra": "♎", "Scorpio": "♏",
    "Sagittarius": "♐", "Capricorn": "♑", "Aquarius": "♒", "Pisces": "♓",
}

# Planet keys in chart docs from astro_calculator.py are lowercase
# (sun, moon, mercury, ...). Glyph table mirrors that.
PLANET_GLYPH = {
    "sun": "☉", "moon": "☽", "mercury": "☿", "venus": "♀",
    "mars": "♂", "jupiter": "♃", "saturn": "♄", "uranus": "♅",
    "neptune": "♆", "pluto": "♇", "north_node": "☊", "chiron": "⚷",
}

# Display labels for the planet glyphs above
PLANET_LABEL = {
    "sun": "Sun", "moon": "Moon", "mercury": "Mercury", "venus": "Venus",
    "mars": "Mars", "jupiter": "Jupiter", "saturn": "Saturn",
    "uranus": "Uranus", "neptune": "Neptune", "pluto": "Pluto",
    "north_node": "North Node", "chiron": "Chiron",
}

# Element-tinted segment fills behind the zodiac ring
ELEMENT_FILL = {
    "Fire": (255, 107, 107, 70),   # warm red
    "Earth": (110, 180, 130, 70),  # green
    "Air": (255, 230, 109, 70),    # yellow
    "Water": (52, 152, 219, 70),   # blue
}

ELEMENT_OF = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
}

# Aspect colors. Hard aspects red, soft aspects blue, minor faint.
# Keys are lowercased to match astro_calculator's aspect names.
ASPECT_STYLE = {
    "conjunction": None,  # same point, not drawn
    "opposition":  ((220, 80, 80, 180), 2),
    "trine":       ((90, 160, 230, 170), 2),
    "square":      ((220, 80, 80, 160), 2),
    "sextile":     ((90, 160, 230, 130), 1),
    "quincunx":    ((180, 180, 180, 90), 1),
    "semi-sextile":((180, 180, 180, 70), 1),
    "semisextile": ((180, 180, 180, 70), 1),
}

GOLD = (245, 197, 96)        # accent
GOLD_DIM = (245, 197, 96, 90)
WHITE = (245, 245, 245)
WHITE_DIM = (245, 245, 245, 140)
BG_DARK_TOP = (15, 15, 22)
BG_DARK_MID = (26, 26, 46)
BG_DARK_BOT = (22, 33, 62)


# ---------- coordinate helpers ----------

def _cosmic_background(w: int, h: int) -> Image.Image:
    """Vertical 3-stop gradient mimicking the brand cosmic-page-bg."""
    img = Image.new("RGB", (w, h), BG_DARK_TOP)
    px = img.load()
    for y in range(h):
        t = y / max(h - 1, 1)
        if t < 0.5:
            k = t / 0.5
            r = int(BG_DARK_TOP[0] + (BG_DARK_MID[0] - BG_DARK_TOP[0]) * k)
            g = int(BG_DARK_TOP[1] + (BG_DARK_MID[1] - BG_DARK_TOP[1]) * k)
            b = int(BG_DARK_TOP[2] + (BG_DARK_MID[2] - BG_DARK_TOP[2]) * k)
        else:
            k = (t - 0.5) / 0.5
            r = int(BG_DARK_MID[0] + (BG_DARK_BOT[0] - BG_DARK_MID[0]) * k)
            g = int(BG_DARK_MID[1] + (BG_DARK_BOT[1] - BG_DARK_MID[1]) * k)
            b = int(BG_DARK_MID[2] + (BG_DARK_BOT[2] - BG_DARK_MID[2]) * k)
        for x in range(w):
            px[x, y] = (r, g, b)
    return img


def _sprinkle_stars(img: Image.Image, count: int = 80, seed: int = 7) -> None:
    """Deterministic faint star field (no randomness across runs)."""
    import random
    rng = random.Random(seed)
    draw = ImageDraw.Draw(img, "RGBA")
    w, h = img.size
    for _ in range(count):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, h - 1)
        a = rng.randint(40, 140)
        r = rng.choice([1, 1, 1, 2])
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, a))


def _to_canvas_angle_rad(planet_lng: float, asc_lng: float) -> float:
    """Convert ecliptic longitude to a math-convention angle (radians, CCW from +x).

    Standard wheel layout: ascendant on the LEFT, zodiac running counterclockwise.
    canvas_angle_deg = 180 + (planet_lng - asc_lng), so:
      planet at asc_lng -> 180° (left)
      planet at asc_lng+90 -> 270° (bottom = IC)
      planet at asc_lng+180 -> 0° (right = DSC)
      planet at asc_lng+270 -> 90° (top = MC)
    """
    deg = (180.0 + (planet_lng - asc_lng)) % 360.0
    return math.radians(deg)


def _polar(cx: float, cy: float, r: float, theta: float) -> tuple[float, float]:
    """Math-convention polar -> Pillow pixel (y axis flipped)."""
    return cx + r * math.cos(theta), cy - r * math.sin(theta)


def _draw_text_centered(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill,
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text((xy[0] - tw / 2 - bbox[0], xy[1] - th / 2 - bbox[1]), text, font=font, fill=fill)


def _measure(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


# ---------- the wheel ----------

def render_wheel(
    chart: dict,
    *,
    size: int = 1200,
    transparent_bg: bool = False,
) -> Image.Image:
    """Render just the natal wheel (square)."""
    cx = cy = size / 2
    if transparent_bg:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    else:
        img = _cosmic_background(size, size).convert("RGBA")
        _sprinkle_stars(img, count=int(size * 0.07))
    draw = ImageDraw.Draw(img, "RGBA")

    # Radii (proportional to size so the function scales)
    r_outer = size * 0.46            # outer rim of zodiac band
    r_zodiac_inner = size * 0.40     # inner rim of zodiac band (above house ring)
    r_house_outer = size * 0.395
    r_house_inner = size * 0.305
    r_planet = size * 0.345          # planets placed roughly mid-house
    r_aspect = size * 0.295          # aspect lines stay inside this circle

    # ascendant longitude is stored under "degree" by astro_calculator
    # (older astro_engine used "longitude") — accept either.
    asc = chart.get("ascendant") or chart.get("houses", {}).get("ascendant") or {}
    asc_lng = float(asc.get("degree") if asc.get("degree") is not None else asc.get("longitude") or 0.0)

    # Zodiac band — element-tinted slices
    for i, sign in enumerate(SIGN_ORDER):
        # Each sign occupies 30° starting at sign_lng = i*30
        # Translate to canvas range; arc() expects degrees clockwise from EAST(+x).
        a_start = (180.0 + (i * 30.0 - asc_lng)) % 360.0
        a_end = (180.0 + ((i + 1) * 30.0 - asc_lng)) % 360.0
        # Pillow arc: angles measured CW from 3-o'clock (east). Our math angle is CCW.
        # Convert: pillow_deg = (-math_deg) mod 360
        p_start = (-a_end) % 360.0
        p_end = (-a_start) % 360.0
        bbox = (cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer)
        # Filled element wedge between r_zodiac_inner and r_outer using pieslice
        # then punch out the inner circle later. Simplest: stack two pieslices.
        elem = ELEMENT_OF.get(sign, "Air")
        fill = ELEMENT_FILL[elem]
        # Outer pieslice (from center to r_outer)
        draw.pieslice(bbox, p_start, p_end, fill=fill)
    # Punch inner hole back to background
    draw.ellipse(
        (cx - r_zodiac_inner, cy - r_zodiac_inner, cx + r_zodiac_inner, cy + r_zodiac_inner),
        fill=(0, 0, 0, 0),
    )

    # Outer & inner rim circles
    draw.ellipse(
        (cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer),
        outline=GOLD, width=max(2, size // 600),
    )
    draw.ellipse(
        (cx - r_zodiac_inner, cy - r_zodiac_inner, cx + r_zodiac_inner, cy + r_zodiac_inner),
        outline=GOLD_DIM, width=1,
    )

    # Sign-boundary spokes through the zodiac band
    for i in range(12):
        a = math.radians((180.0 + (i * 30.0 - asc_lng)) % 360.0)
        x1, y1 = _polar(cx, cy, r_zodiac_inner, a)
        x2, y2 = _polar(cx, cy, r_outer, a)
        draw.line((x1, y1, x2, y2), fill=GOLD_DIM, width=1)

    # Sign glyphs centered in each band
    sign_font = _font(int(size * 0.038), bold=False)
    r_sign_label = (r_outer + r_zodiac_inner) / 2.0
    for i, sign in enumerate(SIGN_ORDER):
        mid_lng = i * 30.0 + 15.0  # middle of the sign
        theta = _to_canvas_angle_rad(mid_lng, asc_lng)
        sx, sy = _polar(cx, cy, r_sign_label, theta)
        _draw_text_centered(draw, (sx, sy), SIGN_GLYPH[sign], sign_font, GOLD)

    # House ring
    draw.ellipse(
        (cx - r_house_outer, cy - r_house_outer, cx + r_house_outer, cy + r_house_outer),
        outline=(255, 255, 255, 50), width=1,
    )
    draw.ellipse(
        (cx - r_house_inner, cy - r_house_inner, cx + r_house_inner, cy + r_house_inner),
        outline=(255, 255, 255, 70), width=1,
    )

    # House cusps — angular houses (1,4,7,10) drawn bolder.
    # astro_calculator stores cusps under "degree"; older format used "cusp".
    houses = chart.get("houses") or {}

    def _house_cusp(h_num: int) -> Optional[float]:
        h = houses.get(h_num) or houses.get(str(h_num)) or {}
        v = h.get("degree") if h.get("degree") is not None else h.get("cusp")
        return float(v) if v is not None else None

    house_num_font = _font(int(size * 0.020), bold=True)
    for h in range(1, 13):
        cusp = _house_cusp(h)
        if cusp is None:
            continue
        theta = _to_canvas_angle_rad(cusp, asc_lng)
        is_angular = h in (1, 4, 7, 10)
        x1, y1 = _polar(cx, cy, r_house_inner, theta)
        x2, y2 = _polar(cx, cy, r_house_outer, theta)
        draw.line(
            (x1, y1, x2, y2),
            fill=(245, 197, 96, 200) if is_angular else (255, 255, 255, 90),
            width=2 if is_angular else 1,
        )
        next_cusp = _house_cusp((h % 12) + 1)
        if next_cusp is None:
            next_cusp = cusp + 30.0
        delta = (next_cusp - cusp) % 360.0
        mid_lng = (cusp + delta / 2.0) % 360.0
        theta_mid = _to_canvas_angle_rad(mid_lng, asc_lng)
        nx, ny = _polar(cx, cy, (r_house_inner + r_house_outer) / 2.0 - size * 0.005, theta_mid)
        _draw_text_centered(draw, (nx, ny), str(h), house_num_font, WHITE_DIM)

    # ASC / IC / DSC / MC labels just outside the wheel
    angles_label_font = _font(int(size * 0.020), bold=True)
    for label, lng_offset in (("ASC", 0.0), ("IC", 90.0), ("DC", 180.0), ("MC", 270.0)):
        theta = _to_canvas_angle_rad(asc_lng + lng_offset, asc_lng)
        lx, ly = _polar(cx, cy, r_outer + size * 0.025, theta)
        _draw_text_centered(draw, (lx, ly), label, angles_label_font, GOLD)

    # Aspect lines — drawn first so planets sit on top
    aspects = chart.get("aspects") or []
    planets = chart.get("planets") or {}

    def _planet_lng(name: str) -> Optional[float]:
        p = planets.get(name) or planets.get(name.lower()) if name else None
        if not p:
            return None
        v = p.get("degree") if p.get("degree") is not None else p.get("longitude")
        return float(v) if v is not None else None

    def _planet_xy(name: str) -> Optional[tuple[float, float]]:
        lng = _planet_lng(name)
        if lng is None:
            return None
        theta = _to_canvas_angle_rad(lng, asc_lng)
        return _polar(cx, cy, r_aspect, theta)

    for asp in aspects:
        style = ASPECT_STYLE.get(str(asp.get("aspect", "")).lower())
        if not style:
            continue
        color, width = style
        a_xy = _planet_xy(asp.get("planet1"))
        b_xy = _planet_xy(asp.get("planet2"))
        if not a_xy or not b_xy:
            continue
        # Fade by orb tightness: the tighter (smaller orb), the brighter
        orb = float(asp.get("orb", 0.0) or 0.0)
        max_orb = 8.0
        opacity_scale = max(0.35, 1.0 - (orb / max_orb))
        r, g, b, a = color
        col = (r, g, b, int(a * opacity_scale))
        draw.line((*a_xy, *b_xy), fill=col, width=width)

    # Inner aspect-bound circle so the eye reads aspects vs planets clearly
    draw.ellipse(
        (cx - r_aspect, cy - r_aspect, cx + r_aspect, cy + r_aspect),
        outline=(255, 255, 255, 40), width=1,
    )

    # Planets — glyph + degree-in-sign tag
    planet_font = _font(int(size * 0.034), bold=False)
    deg_font = _font(int(size * 0.014), bold=False)

    # Cluster prevention — if two planets are within ~5° they overlap on the
    # ring. Sort by longitude relative to ASC, push later ones outward in tiny
    # alternating offsets.
    placed: list[tuple[str, float, float, float]] = []  # (name, lng, theta, r)
    sorted_names = sorted(
        [n for n in planets.keys() if n in PLANET_GLYPH],
        key=lambda n: ((float(planets[n].get("degree", planets[n].get("longitude", 0.0))) - asc_lng) % 360.0),
    )
    last_theta_deg: Optional[float] = None
    offset_step = size * 0.030
    offset_toggle = 1
    for name in sorted_names:
        lng = _planet_lng(name)
        if lng is None:
            continue
        theta = _to_canvas_angle_rad(lng, asc_lng)
        theta_deg = math.degrees(theta)
        r_use = r_planet
        if last_theta_deg is not None:
            d = abs(((theta_deg - last_theta_deg + 180.0) % 360.0) - 180.0)
            if d < 7.0:
                r_use = r_planet + offset_toggle * offset_step
                offset_toggle *= -1
            else:
                offset_toggle = 1
        placed.append((name, lng, theta, r_use))
        last_theta_deg = theta_deg

    for name, lng, theta, r_use in placed:
        px, py = _polar(cx, cy, r_use, theta)
        glyph = PLANET_GLYPH.get(name, "?")
        # Subtle disc behind the glyph for readability over aspect lines
        disc_r = size * 0.024
        draw.ellipse(
            (px - disc_r, py - disc_r, px + disc_r, py + disc_r),
            fill=(15, 15, 22, 220), outline=GOLD_DIM, width=1,
        )
        _draw_text_centered(draw, (px, py), glyph, planet_font, WHITE)
        # degree-in-sign tag, placed slightly outward
        deg = int(lng % 30)
        retro = planets[name].get("retrograde")
        tag = f"{deg}°" + (" ℞" if retro else "")
        tx, ty = _polar(cx, cy, r_use + size * 0.040, theta)
        _draw_text_centered(draw, (tx, ty), tag, deg_font, WHITE_DIM)

    return img


# ---------- shareable card ----------

def render_share_card(
    chart: dict,
    *,
    user_name: str = "",
    birth_date: str = "",
    birth_place: str = "",
    size: int = 1080,
) -> Image.Image:
    """Render the social share card (1080x1080 by default)."""
    img = _cosmic_background(size, size).convert("RGBA")
    _sprinkle_stars(img, count=int(size * 0.13), seed=11)
    draw = ImageDraw.Draw(img, "RGBA")

    # Header
    title_font = _font(int(size * 0.045), bold=True, serif=True)
    subtitle_font = _font(int(size * 0.022), bold=False)
    label_font = _font(int(size * 0.018), bold=False)
    if user_name:
        _draw_text_centered(
            draw, (size / 2, int(size * 0.085)),
            f"{user_name}'s Cosmic Blueprint", title_font, WHITE,
        )
    else:
        _draw_text_centered(
            draw, (size / 2, int(size * 0.085)),
            "Cosmic Blueprint", title_font, WHITE,
        )
    sub_bits = [b for b in (birth_date, birth_place) if b]
    if sub_bits:
        _draw_text_centered(
            draw, (size / 2, int(size * 0.130)),
            "  ·  ".join(sub_bits),
            subtitle_font, GOLD,
        )

    # Layout:
    #   0% – 14%    header (title + subtitle)
    #   16% – 71%   wheel (55% of canvas)
    #   73% – 88%   big-three strip
    #   88% – 100%  footer (divider, brand)
    wheel_size = int(size * 0.55)
    wheel = render_wheel(chart, size=wheel_size, transparent_bg=True)
    wx = (size - wheel_size) // 2
    wy = int(size * 0.16)
    img.alpha_composite(wheel, (wx, wy))

    # Big-three strip
    big_y = int(size * 0.74)
    sign_glyph_font = _font(int(size * 0.052), bold=False)
    sign_label_font = _font(int(size * 0.022), bold=True)
    role_font = _font(int(size * 0.014), bold=False)
    col_w = size / 3
    for i, (role, sign_key) in enumerate((
        ("Sun", "sun_sign"),
        ("Moon", "moon_sign"),
        ("Rising", "rising_sign"),
    )):
        sign = chart.get(sign_key) or "—"
        cx_col = col_w * (i + 0.5)
        glyph = SIGN_GLYPH.get(sign, "?")
        _draw_text_centered(draw, (cx_col, big_y + int(size * 0.030)), glyph, sign_glyph_font, GOLD)
        _draw_text_centered(draw, (cx_col, big_y + int(size * 0.080)), sign, sign_label_font, WHITE)
        _draw_text_centered(draw, (cx_col, big_y + int(size * 0.108)), role.upper(), role_font, WHITE_DIM)

    # Footer divider + branding
    div_y = int(size * 0.91)
    draw.line(
        (int(size * 0.18), div_y, size - int(size * 0.18), div_y),
        fill=(255, 255, 255, 40), width=1,
    )
    foot_a_font = _font(int(size * 0.014), bold=False)
    foot_b_font = _font(int(size * 0.024), bold=True, serif=True)
    _draw_text_centered(
        draw, (size / 2, div_y + int(size * 0.022)),
        "DISCOVER YOUR COSMIC BLUEPRINT AT", foot_a_font, WHITE_DIM,
    )
    _draw_text_centered(
        draw, (size / 2, div_y + int(size * 0.052)),
        "gab44.com", foot_b_font, GOLD,
    )

    return img


# ---------- output helpers ----------

def to_png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG", optimize=True)
    return buf.getvalue()
