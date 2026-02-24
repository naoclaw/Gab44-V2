from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Request, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
import json
import re
import stripe
import requests as _requests
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
from openai import AsyncOpenAI
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from astro_calculator import (
    calculate_natal_chart,
    calculate_current_transits,
    calculate_numerology,
    get_coordinates,
    get_element,
    get_modality
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET')
if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable is required")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days

# OpenAI / LLM Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# Admin emails (set via environment variable)
ADMIN_EMAILS = [e.strip().lower() for e in os.environ.get('ADMIN_EMAILS', '').split(',') if e.strip()]

# Stripe Configuration
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Plan → price (in cents) mapping for inline checkout
STRIPE_PLAN_PRICES = {
    "enthusiast": {"amount": 1999, "name": "Gab44 Enthusiast"},
    "advanced":   {"amount": 4999, "name": "Gab44 Advanced"},
    "professional": {"amount": 9900, "name": "Gab44 Professional"},
}

# OneSignal Configuration
ONESIGNAL_APP_ID = os.environ.get('ONESIGNAL_APP_ID', '')
ONESIGNAL_API_KEY = os.environ.get('ONESIGNAL_API_KEY', '')
ONESIGNAL_API_URL = "https://api.onesignal.com/notifications"

# SendGrid Configuration
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '')

# Separate sender addresses per email type (all must be verified in SendGrid)
EMAIL_NOREPLY   = os.environ.get('EMAIL_NOREPLY',   'noreply@gab44.com')    # system / automated
EMAIL_VERIFY    = os.environ.get('EMAIL_VERIFY',    'verify@gab44.com')     # sign-up & verification
EMAIL_SUPPORT   = os.environ.get('EMAIL_SUPPORT',   'support@gab44.com')    # support replies
EMAIL_MARKETING = os.environ.get('EMAIL_MARKETING', 'hello@gab44.com')      # promotions & newsletters

# Token validity windows
EMAIL_VERIFY_EXPIRY_HOURS = 48
PASSWORD_RESET_EXPIRY_HOURS = 1

# Chat message limits per subscription tier (per calendar day, UTC)
CHAT_DAILY_LIMITS: dict[str, int] = {
    "seeker":       10,
    "enthusiast":   100,
    "advanced":     -1,   # unlimited
    "professional": -1,   # unlimited
}

app = FastAPI(title="Gab44 - Astrology AI Coaching Platform")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# ============== Models ==============

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    birth_name: Optional[str] = None  # Legal birth name for numerology (if different from display name)
    birth_date: str  # YYYY-MM-DD
    birth_time: Optional[str] = None  # HH:MM
    birth_place: str
    birth_latitude: Optional[float] = None
    birth_longitude: Optional[float] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"[0-9!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one digit or special character")
        return v


class UserUpdate(BaseModel):
    name: Optional[str] = None
    birth_name: Optional[str] = None
    birth_date: Optional[str] = None
    birth_time: Optional[str] = None
    birth_place: Optional[str] = None
    birth_latitude: Optional[float] = None
    birth_longitude: Optional[float] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"[0-9!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one digit or special character")
        return v

class UserProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    name: str
    birth_name: Optional[str] = None
    birth_date: str
    birth_time: Optional[str] = None
    birth_place: str
    birth_latitude: Optional[float] = None
    birth_longitude: Optional[float] = None
    sun_sign: Optional[str] = None
    subscription_tier: str = "seeker"
    is_admin: bool = False
    email_verified: bool = False
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

class BirthChart(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    sun_sign: str
    moon_sign: str
    rising_sign: str
    planets: dict
    houses: dict
    aspects: List[dict]
    patterns: List[str]
    created_at: str

class TransitActivation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    transit_type: str
    planet: str
    aspect: str
    natal_planet: str
    start_date: str
    peak_date: str
    end_date: str
    strength: float
    interpretation: str
    action_items: List[str]

class DailyGuidance(BaseModel):
    date: str
    overall_energy: str
    focus_areas: List[str]
    action_items: List[str]
    transit_highlights: List[dict]

# ============== Compatibility Models ==============

class CompatibilityRequest(BaseModel):
    partner_name: str
    partner_birth_date: str  # YYYY-MM-DD
    partner_birth_time: Optional[str] = None
    partner_birth_place: str

class SynastryAspect(BaseModel):
    person1_planet: str
    person2_planet: str
    aspect_type: str
    orb: float
    strength: float
    interpretation: str
    category: str  # romantic, communication, emotional, karmic, growth

class CompatibilityReport(BaseModel):
    id: str
    user_id: str
    partner_name: str
    partner_birth_date: str
    partner_sun_sign: str
    overall_score: float
    category_scores: Dict[str, float]
    synastry_aspects: List[Dict[str, Any]]
    composite_chart: Dict[str, Any]
    strengths: List[str]
    challenges: List[str]
    karmic_themes: List[str]
    growth_opportunities: List[str]
    ai_analysis: str
    created_at: str

# ============== Payment + Notification Models ==============

class CheckoutRequest(BaseModel):
    tier: str  # enthusiast | advanced | professional

class DeviceRegistration(BaseModel):
    player_id: str  # OneSignal player/subscription ID

class NewsletterSubscription(BaseModel):
    email: EmailStr
    name: str = ""

class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

class EmailBlastRequest(BaseModel):
    subject: str
    body_html: str
    tier_filter: str = "all"  # "all" | "seeker" | "enthusiast" | "advanced" | "professional"

# ============== Auth Helpers ==============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: str) -> str:
    expiration = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {"user_id": user_id, "exp": expiration}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id}, {"_id": 0, "password": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Admin status from DB role OR from ADMIN_EMAILS env var (bootstrap)
        user_email = user.get("email", "").lower()
        is_admin_by_role = user.get("role") == "admin"
        is_admin_by_env = user_email in ADMIN_EMAILS
        user["is_admin"] = is_admin_by_role or is_admin_by_env
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """Dependency that requires admin access"""
    if not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# ============== Email Helper (SendGrid) ==============

def send_email(to_email: str, subject: str, html_content: str, from_email: str = None) -> bool:
    """Send an email via SendGrid.
    
    Pass ``from_email`` to override the default sender (EMAIL_NOREPLY).
    Use the purpose-specific constants:
      EMAIL_VERIFY    – account / sign-up emails
      EMAIL_SUPPORT   – support replies
      EMAIL_MARKETING – promotions & newsletters
      EMAIL_NOREPLY   – automated system emails (default)
    """
    if not SENDGRID_API_KEY:
        logging.warning("SENDGRID_API_KEY not configured – email not sent to %s", to_email)
        return False
    sender = from_email or EMAIL_NOREPLY
    try:
        message = Mail(
            from_email=sender,
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        logging.info("Email sent from %s to %s – status %s", sender, to_email, response.status_code)
        return response.status_code in (200, 202)
    except Exception as exc:
        logging.error("SendGrid error sending to %s: %s", to_email, exc)
        return False

# ---------- Email template builders ----------

_EMAIL_BASE = """
<div style="font-family:sans-serif;max-width:520px;margin:auto;padding:32px 24px;
            background:#0a0a0f;color:#e8e0f0;border-radius:16px;">
  {body}
  <hr style="border:none;border-top:1px solid #222;margin:24px 0;" />
  <p style="color:#606080;font-size:12px;margin:0;">
    Gab44 &middot; Astrology AI Coaching &middot;
    <a href="mailto:{support}" style="color:#c9a84c;">{support}</a>
  </p>
</div>
"""

def _email_wrap(body: str) -> str:
    return _EMAIL_BASE.format(body=body, support=EMAIL_SUPPORT)


def build_verification_email(name: str, verify_url: str) -> str:
    """Sign-up verification email — sent from EMAIL_VERIFY."""
    body = f"""
      <h1 style="font-family:Georgia,serif;font-size:28px;margin-bottom:4px;color:#c9a84c;">
        ✨ Welcome to Gab44</h1>
      <p style="color:#9090b0;margin-top:0;">Your cosmic journey starts with one click.</p>
      <p style="margin-top:24px;">Hi {name},</p>
      <p>Please verify your email address so we can keep your account secure and
         send you personalized astrological guidance.</p>
      <a href="{verify_url}"
         style="display:inline-block;margin:24px 0;padding:14px 32px;background:#c9a84c;
                color:#0a0a0f;font-weight:700;border-radius:12px;text-decoration:none;font-size:16px;">
        Verify My Email
      </a>
      <p style="color:#9090b0;font-size:13px;">
        This link expires in {EMAIL_VERIFY_EXPIRY_HOURS}&nbsp;hours. If you didn't create a Gab44 account,
        you can safely ignore this email.</p>
    """
    return _email_wrap(body)


def build_welcome_email(name: str, dashboard_url: str) -> str:
    """Post-verification welcome email — sent from EMAIL_VERIFY."""
    body = f"""
      <h1 style="font-family:Georgia,serif;font-size:28px;margin-bottom:4px;color:#c9a84c;">
        🌟 You're verified, {name}!</h1>
      <p style="color:#9090b0;margin-top:0;">The cosmos is ready to guide you.</p>
      <p style="margin-top:24px;">Your Gab44 account is now fully activated.</p>
      <p>Head to your dashboard to explore your natal chart, daily guidance, and AI coaching.</p>
      <a href="{dashboard_url}"
         style="display:inline-block;margin:24px 0;padding:14px 32px;background:#c9a84c;
                color:#0a0a0f;font-weight:700;border-radius:12px;text-decoration:none;font-size:16px;">
        Go to My Dashboard
      </a>
    """
    return _email_wrap(body)


def build_promotional_email(name: str, headline: str, body_html: str, cta_text: str, cta_url: str) -> str:
    """Generic promotional / newsletter email — sent from EMAIL_MARKETING."""
    body = f"""
      <h1 style="font-family:Georgia,serif;font-size:26px;margin-bottom:4px;color:#c9a84c;">
        {headline}</h1>
      <p style="margin-top:16px;">Hi {name},</p>
      {body_html}
      <a href="{cta_url}"
         style="display:inline-block;margin:24px 0;padding:14px 32px;background:#c9a84c;
                color:#0a0a0f;font-weight:700;border-radius:12px;text-decoration:none;font-size:16px;">
        {cta_text}
      </a>
      <p style="color:#9090b0;font-size:12px;">
        You're receiving this because you signed up for Gab44 updates.
        To unsubscribe, reply with "unsubscribe" to
        <a href="mailto:{EMAIL_MARKETING}" style="color:#c9a84c;">{EMAIL_MARKETING}</a>.
      </p>
    """
    return _email_wrap(body)


def build_support_reply_email(name: str, ticket_subject: str, reply_body: str) -> str:
    """Support reply email — sent from EMAIL_SUPPORT."""
    body = f"""
      <h1 style="font-family:Georgia,serif;font-size:22px;margin-bottom:4px;color:#c9a84c;">
        Re: {ticket_subject}</h1>
      <p style="margin-top:16px;">Hi {name},</p>
      {reply_body}
      <p style="margin-top:24px;">Need more help?
        <a href="mailto:{EMAIL_SUPPORT}" style="color:#c9a84c;">Reply to this email</a>
        and we'll get back to you.</p>
    """
    return _email_wrap(body)


def build_password_reset_email(name: str, reset_url: str) -> str:
    """Password-reset email — sent from EMAIL_NOREPLY."""
    body = f"""
      <h1 style="font-family:Georgia,serif;font-size:26px;margin-bottom:4px;color:#c9a84c;">
        🔑 Reset your password</h1>
      <p style="color:#9090b0;margin-top:0;">A reset was requested for your Gab44 account.</p>
      <p style="margin-top:24px;">Hi {name},</p>
      <p>Click the button below to choose a new password. This link expires in
         <strong>{PASSWORD_RESET_EXPIRY_HOURS}&nbsp;hour</strong>.</p>
      <a href="{reset_url}"
         style="display:inline-block;margin:24px 0;padding:14px 32px;background:#c9a84c;
                color:#0a0a0f;font-weight:700;border-radius:12px;text-decoration:none;font-size:16px;">
        Reset My Password
      </a>
      <p style="color:#9090b0;font-size:13px;">
        If you didn't request a password reset, you can safely ignore this email —
        your password will not change.</p>
    """
    return _email_wrap(body)


# ============== Astrology Helpers ==============

def calculate_sun_sign(birth_date: str) -> str:
    """Calculate sun sign using Swiss Ephemeris for exact accuracy (handles cusp days correctly)."""
    try:
        chart = calculate_natal_chart(birth_date)
        return chart.get("sun_sign", "Unknown")
    except Exception:
        return "Unknown"

def get_sign_element(sign: str) -> str:
    """Get the element for a zodiac sign"""
    elements = {
        "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
        "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
        "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
        "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"
    }
    return elements.get(sign, "Unknown")

def get_sign_modality(sign: str) -> str:
    """Get the modality for a zodiac sign"""
    modalities = {
        "Aries": "Cardinal", "Cancer": "Cardinal", "Libra": "Cardinal", "Capricorn": "Cardinal",
        "Taurus": "Fixed", "Leo": "Fixed", "Scorpio": "Fixed", "Aquarius": "Fixed",
        "Gemini": "Mutable", "Virgo": "Mutable", "Sagittarius": "Mutable", "Pisces": "Mutable"
    }
    return modalities.get(sign, "Unknown")

def get_sign_polarity(sign: str) -> str:
    """Get the polarity (Yin/Yang) for a zodiac sign"""
    yang_signs = ["Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius"]
    return "Yang" if sign in yang_signs else "Yin"

def get_ruling_planet(sign: str) -> str:
    """Get the ruling planet for a zodiac sign"""
    rulers = {
        "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
        "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Pluto",
        "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Uranus", "Pisces": "Neptune"
    }
    return rulers.get(sign, "Unknown")

# ============== Compatibility Calculations ==============

def calculate_element_compatibility(sign1: str, sign2: str) -> dict:
    """Calculate compatibility based on elements"""
    elem1 = get_sign_element(sign1)
    elem2 = get_sign_element(sign2)
    
    # Same element = high compatibility
    if elem1 == elem2:
        return {"score": 95, "description": f"Both {elem1} signs - deep natural understanding and shared values"}
    
    # Compatible elements
    compatible_pairs = {
        ("Fire", "Air"): {"score": 85, "description": "Fire and Air fuel each other - exciting and stimulating"},
        ("Earth", "Water"): {"score": 85, "description": "Earth and Water nurture each other - stable and emotionally supportive"},
    }
    
    pair = tuple(sorted([elem1, elem2]))
    if pair in compatible_pairs:
        return compatible_pairs[pair]
    if (elem2, elem1) in compatible_pairs:
        return compatible_pairs[(elem2, elem1)]
    
    # Challenging but growth-oriented
    challenging_pairs = {
        ("Fire", "Water"): {"score": 55, "description": "Fire and Water create steam - passionate but requires balance"},
        ("Fire", "Earth"): {"score": 60, "description": "Fire and Earth - different paces, but can ground and inspire each other"},
        ("Air", "Water"): {"score": 58, "description": "Air and Water - mind vs heart, requires conscious communication"},
        ("Air", "Earth"): {"score": 62, "description": "Air and Earth - ideas vs practicality, complementary if respected"},
    }
    
    pair = tuple(sorted([elem1, elem2]))
    if pair in challenging_pairs:
        return challenging_pairs[pair]
    if (elem2, elem1) in challenging_pairs:
        return challenging_pairs[(elem2, elem1)]
    
    return {"score": 65, "description": "Neutral elemental compatibility"}

def calculate_modality_compatibility(sign1: str, sign2: str) -> dict:
    """Calculate compatibility based on modalities"""
    mod1 = get_sign_modality(sign1)
    mod2 = get_sign_modality(sign2)
    
    if mod1 == mod2:
        if mod1 == "Fixed":
            return {"score": 70, "description": "Both Fixed - loyal and stable, but may struggle with change"}
        elif mod1 == "Cardinal":
            return {"score": 72, "description": "Both Cardinal - dynamic leaders, may compete for direction"}
        else:
            return {"score": 78, "description": "Both Mutable - adaptable and flexible together"}
    
    # Mixed modalities
    if "Cardinal" in [mod1, mod2] and "Fixed" in [mod1, mod2]:
        return {"score": 75, "description": "Cardinal-Fixed: Initiative meets stability"}
    if "Cardinal" in [mod1, mod2] and "Mutable" in [mod1, mod2]:
        return {"score": 82, "description": "Cardinal-Mutable: Leadership meets adaptability"}
    if "Fixed" in [mod1, mod2] and "Mutable" in [mod1, mod2]:
        return {"score": 80, "description": "Fixed-Mutable: Stability meets flexibility"}
    
    return {"score": 75, "description": "Balanced modality interaction"}

def calculate_synastry_aspects(chart1: dict, chart2: dict) -> list:
    """Calculate synastry aspects between two charts"""
    aspects = []
    aspect_types = {
        0: {"name": "conjunction", "harmony": 0.9, "category": "intense"},
        60: {"name": "sextile", "harmony": 0.8, "category": "harmonious"},
        90: {"name": "square", "harmony": 0.4, "category": "challenging"},
        120: {"name": "trine", "harmony": 0.95, "category": "harmonious"},
        180: {"name": "opposition", "harmony": 0.5, "category": "polarizing"}
    }
    
    planets = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]
    
    for p1 in planets:
        for p2 in planets:
            if p1 in chart1.get("planets", {}) and p2 in chart2.get("planets", {}):
                deg1 = chart1["planets"][p1].get("degree", 0)
                deg2 = chart2["planets"][p2].get("degree", 0)
                
                # Calculate angular difference
                diff = abs(deg1 - deg2) % 360
                if diff > 180:
                    diff = 360 - diff
                
                # Check for aspects with orb
                for angle, aspect_info in aspect_types.items():
                    orb = abs(diff - angle)
                    if orb <= 8:  # 8 degree orb
                        strength = 1 - (orb / 8)
                        
                        # Categorize the aspect
                        category = "general"
                        if p1 in ["venus", "mars"] or p2 in ["venus", "mars"]:
                            category = "romantic"
                        elif p1 == "moon" or p2 == "moon":
                            category = "emotional"
                        elif p1 in ["mercury"] or p2 in ["mercury"]:
                            category = "communication"
                        elif p1 in ["saturn", "pluto"] or p2 in ["saturn", "pluto"]:
                            category = "karmic"
                        elif p1 == "jupiter" or p2 == "jupiter":
                            category = "growth"
                        
                        aspects.append({
                            "person1_planet": p1,
                            "person2_planet": p2,
                            "aspect_type": aspect_info["name"],
                            "orb": round(orb, 2),
                            "strength": round(strength, 2),
                            "harmony": aspect_info["harmony"],
                            "category": category
                        })
    
    return sorted(aspects, key=lambda x: x["strength"], reverse=True)[:15]

def generate_composite_chart(chart1: dict, chart2: dict) -> dict:
    """Generate a composite chart from two birth charts"""
    composite = {"planets": {}, "houses": {}}
    
    planets = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]
    
    for planet in planets:
        if planet in chart1.get("planets", {}) and planet in chart2.get("planets", {}):
            deg1 = chart1["planets"][planet].get("degree", 0)
            deg2 = chart2["planets"][planet].get("degree", 0)
            
            # Calculate midpoint
            midpoint = (deg1 + deg2) / 2
            if abs(deg1 - deg2) > 180:
                midpoint = (midpoint + 180) % 360
            
            # Determine sign from degree
            sign_index = int(midpoint / 30)
            signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
            
            composite["planets"][planet] = {
                "degree": round(midpoint % 30, 2),
                "sign": signs[sign_index % 12],
                "house": chart1["planets"][planet].get("house", 1)
            }
    
    return composite

async def generate_compatibility_analysis(user: dict, partner_data: dict, synastry: list, scores: dict) -> str:
    """Generate AI-powered compatibility analysis"""
    
    user_sun = user.get("sun_sign", "Unknown")
    partner_sun = partner_data.get("sun_sign", "Unknown")
    
    # Format synastry aspects for analysis
    aspect_summary = "\n".join([
        f"- {a['person1_planet'].title()} {a['aspect_type']} {a['person2_planet'].title()} ({a['category']})"
        for a in synastry[:8]
    ])
    
    prompt = f"""Provide a comprehensive relationship compatibility analysis:

PERSON 1: {user.get('name')} - {user_sun} Sun
PERSON 2: {partner_data.get('name')} - {partner_sun} Sun

COMPATIBILITY SCORES:
- Overall: {scores.get('overall', 0)}%
- Emotional: {scores.get('emotional', 0)}%
- Communication: {scores.get('communication', 0)}%
- Romance: {scores.get('romantic', 0)}%
- Long-term: {scores.get('stability', 0)}%

KEY SYNASTRY ASPECTS:
{aspect_summary}

Provide:
1. Overall relationship dynamic and natural chemistry
2. Key strengths of this pairing
3. Potential challenges and how to navigate them
4. Karmic or spiritual themes in this connection
5. Practical advice for building a strong relationship

Keep the analysis warm, insightful, and actionable. Focus on growth potential."""

    try:
        if not openai_client:
            raise RuntimeError("OpenAI not configured")
        completion = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are Gab44, an expert relationship astrologer. Provide insightful, compassionate compatibility analysis that helps people understand their relationship dynamics and growth opportunities."},
                {"role": "user", "content": prompt},
            ],
        )
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"Compatibility analysis error: {e}")
        return f"Based on the {user_sun}-{partner_sun} pairing, this relationship shows {scores.get('overall', 70)}% compatibility. Key themes include balancing {get_sign_element(user_sun)} and {get_sign_element(partner_sun)} energies."

# ============== AI Coach ==============

async def get_ai_coach_response(user: dict, message: str, session_id: str) -> str:
    """Generate AI coaching response"""

    # Get user's chat history
    history = await db.chat_messages.find(
        {"user_id": user["id"], "session_id": session_id},
        {"_id": 0}
    ).sort("timestamp", 1).limit(20).to_list(20)

    # Build context
    sun_sign = user.get("sun_sign", "Unknown")
    element  = get_sign_element(sun_sign)
    modality = get_sign_modality(sun_sign)

    # Fetch full natal chart (cached in DB)
    chart_doc = await db.birth_charts.find_one({"user_id": user["id"]}, {"_id": 0})

    # Build planet summary
    planet_lines = []
    if chart_doc and chart_doc.get("planets"):
        for pname, pdata in chart_doc["planets"].items():
            if pdata:
                h = f" H{pdata['house']}" if pdata.get("house") else ""
                r = " ℞" if pdata.get("retrograde") else ""
                planet_lines.append(f"  {pname.replace('_',' ').title()}: {pdata.get('sign','?')} {pdata.get('sign_degree',0):.1f}°{h}{r}")
    planets_block = "\n".join(planet_lines) if planet_lines else "  (chart not yet generated)"

    # Build numerology summary
    num_lines = []
    if chart_doc and chart_doc.get("numerology"):
        num = chart_doc["numerology"]
        for key in ("life_path", "expression", "soul_urge", "personality", "personal_year"):
            entry = num.get(key, {})
            if entry:
                num_lines.append(f"  {key.replace('_',' ').title()}: {entry['number']} ({entry.get('keyword','')})")
    numerology_block = "\n".join(num_lines) if num_lines else "  (not calculated)"

    # Top aspects
    aspect_lines = []
    if chart_doc and chart_doc.get("aspects"):
        for a in chart_doc["aspects"][:5]:
            aspect_lines.append(f"  {a['planet1'].title()} {a['aspect']} {a['planet2'].title()} (orb {a['orb']}°)")
    aspects_block = "\n".join(aspect_lines) if aspect_lines else "  (none)"

    rising = chart_doc.get("rising_sign", "Unknown") if chart_doc else "Unknown"
    moon   = chart_doc.get("moon_sign",   "Unknown") if chart_doc else "Unknown"

    system_message = f"""You are Gab44, an advanced astrology AI coach. Your mission is to help people live measurably better lives through truthful astrological guidance.

USER PROFILE:
- Name: {user.get('name', 'Seeker')}
- Sun Sign: {sun_sign} ({element}, {modality})
- Moon Sign: {moon}
- Rising Sign: {rising}
- Birth Date: {user.get('birth_date', 'Unknown')}
- Birth Place: {user.get('birth_place', 'Unknown')}

NATAL PLANETS:
{planets_block}

TOP ASPECTS:
{aspects_block}

NUMEROLOGY:
{numerology_block}

YOUR PRINCIPLES:
1. Every response must help the user make better decisions
2. Be truthful, even when uncomfortable — truth serves growth
3. Provide actionable guidance, not just information
4. Weave together astrology AND numerology when they reinforce each other
5. Connect insights to practical life outcomes
6. Ask follow-up questions to understand if guidance was helpful

RESPONSE FORMAT:
- Keep responses conversational but substantive
- Include specific action items when relevant
- Reference planets, houses, and numerology numbers when applicable
- End with a thoughtful question or call to action"""

    try:
        if not openai_client:
            raise RuntimeError("OpenAI not configured")
        messages = [{"role": "system", "content": system_message}]
        for msg in history[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})

        completion = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        return completion.choices[0].message.content

    except Exception as e:
        logging.error(f"AI Coach error: {e}")
        return f"I sense a disturbance in the cosmic connection. Let me try again... As a {sun_sign}, your {element} energy suggests taking a moment to ground yourself. What specific area of life would you like guidance on?"

# ============== Auth Routes ==============

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    # Check if user exists
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Calculate sun sign
    sun_sign = calculate_sun_sign(user_data.birth_date)

    # Generate email verification token
    email_verification_token = str(uuid.uuid4())
    
    # Create user
    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "name": user_data.name,
        "birth_date": user_data.birth_date,
        "birth_time": user_data.birth_time,
        "birth_place": user_data.birth_place,
        "birth_latitude": user_data.birth_latitude,
        "birth_longitude": user_data.birth_longitude,
        "sun_sign": sun_sign,
        "subscription_tier": "advanced",  # Default to advanced until payment is setup
        "email_verified": False,
        "email_verification_token": email_verification_token,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_doc)

    # Send verification email (non-blocking – registration succeeds even if email fails)
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    verify_url = f"{frontend_url}/verify-email?token={email_verification_token}"
    send_email(
        to_email=user_data.email,
        subject="✨ Verify your Gab44 email",
        html_content=build_verification_email(user_data.name, verify_url),
        from_email=EMAIL_VERIFY,
    )
    
    token = create_token(user_id)
    user_profile = {k: v for k, v in user_doc.items() if k != "password" and k != "_id" and k != "email_verification_token"}
    user_email = user_data.email.lower()
    user_profile["is_admin"] = user_email in ADMIN_EMAILS
    
    return TokenResponse(access_token=token, user=UserProfile(**user_profile))

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_token(user["id"])
    user_profile = {k: v for k, v in user.items() if k != "password" and k != "_id" and k != "email_verification_token"}
    user_email = user.get("email", "").lower()
    is_admin_by_role = user.get("role") == "admin"
    is_admin_by_env = user_email in ADMIN_EMAILS
    user_profile["is_admin"] = is_admin_by_role or is_admin_by_env
    
    return TokenResponse(access_token=token, user=UserProfile(**user_profile))

@api_router.get("/auth/verify-email")
async def verify_email(token: str):
    """Verify a user's email address via the token link sent at registration."""
    user = await db.users.find_one({"email_verification_token": token})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"email_verified": True}, "$unset": {"email_verification_token": ""}},
    )
    # Send a welcome email now that the address is confirmed
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    send_email(
        to_email=user["email"],
        subject="🌟 Welcome to Gab44 – you're all set!",
        html_content=build_welcome_email(user.get("name", "Seeker"), f"{frontend_url}/dashboard"),
        from_email=EMAIL_VERIFY,
    )
    return {"verified": True, "message": "Email verified successfully. You can now log in."}

@api_router.post("/auth/resend-verification")
async def resend_verification(user: dict = Depends(get_current_user)):
    """Resend the email verification link to the current user."""
    if user.get("email_verified"):
        return {"sent": False, "message": "Email is already verified"}
    token = str(uuid.uuid4())
    await db.users.update_one({"id": user["id"]}, {"$set": {"email_verification_token": token}})
    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    verify_url = f"{frontend_url}/verify-email?token={token}"
    sent = send_email(
        to_email=user["email"],
        subject="✨ Verify your Gab44 email",
        html_content=build_verification_email(user.get("name", "Seeker"), verify_url),
        from_email=EMAIL_VERIFY,
    )
    return {"sent": sent}

@api_router.post("/auth/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    """Send a password-reset link to the given email address.

    Always returns 200 to prevent user enumeration.
    """
    user = await db.users.find_one({"email": req.email})
    if user:
        reset_token = str(uuid.uuid4())
        expiry = datetime.now(timezone.utc) + timedelta(hours=PASSWORD_RESET_EXPIRY_HOURS)
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {
                "password_reset_token": reset_token,
                "password_reset_expiry": expiry.isoformat(),
            }},
        )
        frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
        reset_url = f"{frontend_url}/reset-password?token={reset_token}"
        send_email(
            to_email=user["email"],
            subject="🔑 Reset your Gab44 password",
            html_content=build_password_reset_email(user.get("name", "Seeker"), reset_url),
            from_email=EMAIL_NOREPLY,
        )
    return {"message": "If that email is registered, a reset link has been sent."}

@api_router.post("/auth/reset-password")
async def reset_password(req: ResetPasswordRequest):
    """Validate a reset token and set a new password."""
    user = await db.users.find_one({"password_reset_token": req.token})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    # Check expiry — ensure timezone-aware comparison
    expiry_str = user.get("password_reset_expiry", "")
    if expiry_str:
        expiry = datetime.fromisoformat(expiry_str)
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expiry:
            raise HTTPException(status_code=400, detail="Reset link has expired. Please request a new one.")

    await db.users.update_one(
        {"id": user["id"]},
        {
            "$set": {"password": hash_password(req.new_password)},
            "$unset": {"password_reset_token": "", "password_reset_expiry": ""},
        },
    )
    return {"message": "Password updated successfully. You can now log in."}

@api_router.get("/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    # Exclude internal token from response
    response = {k: v for k, v in user.items() if k != "email_verification_token"}
    return response

@api_router.put("/auth/me", response_model=UserProfile)
async def update_me(update_data: UserUpdate, user: dict = Depends(get_current_user)):
    """Update the current user's profile information"""
    updates = update_data.model_dump(exclude_unset=True)
    
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Recalculate sun sign if birth_date changes
    if "birth_date" in updates and updates["birth_date"]:
        updates["sun_sign"] = calculate_sun_sign(updates["birth_date"])
    
    await db.users.update_one({"id": user["id"]}, {"$set": updates})
    
    updated_user = await db.users.find_one(
        {"id": user["id"]}, {"_id": 0, "password": 0, "email_verification_token": 0}
    )
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_email = updated_user.get("email", "").lower()
    is_admin_by_role = updated_user.get("role") == "admin"
    is_admin_by_env = user_email in ADMIN_EMAILS
    updated_user["is_admin"] = is_admin_by_role or is_admin_by_env
    
    return UserProfile(**updated_user)

# ============== Chat Routes ==============

@api_router.post("/chat", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest, user: dict = Depends(get_current_user)):
    tier = user.get("subscription_tier", "seeker")
    daily_limit = CHAT_DAILY_LIMITS.get(tier, 10)

    if daily_limit > 0:
        # Count messages sent today (user messages only, UTC calendar day)
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        today_count = await db.chat_messages.count_documents({
            "user_id": user["id"],
            "role": "user",
            "timestamp": {"$gte": today_start},
        })
        if today_count >= daily_limit:
            raise HTTPException(
                status_code=429,
                detail=f"Daily message limit reached ({daily_limit} messages for {tier.title()} plan). Upgrade to continue chatting."
            )
    session_id = request.session_id or str(uuid.uuid4())
    
    # Save user message
    user_msg = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "session_id": session_id,
        "role": "user",
        "content": request.message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db.chat_messages.insert_one(user_msg)
    
    # Get AI response
    ai_response = await get_ai_coach_response(user, request.message, session_id)
    
    # Save AI response
    ai_msg = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "session_id": session_id,
        "role": "assistant",
        "content": ai_response,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    await db.chat_messages.insert_one(ai_msg)
    
    return ChatResponse(response=ai_response, session_id=session_id)

@api_router.get("/chat/history/{session_id}", response_model=List[ChatMessage])
async def get_chat_history(session_id: str, user: dict = Depends(get_current_user)):
    messages = await db.chat_messages.find(
        {"user_id": user["id"], "session_id": session_id},
        {"_id": 0, "role": 1, "content": 1, "timestamp": 1}
    ).sort("timestamp", 1).to_list(100)
    return messages

@api_router.get("/chat/sessions")
async def get_chat_sessions(user: dict = Depends(get_current_user)):
    pipeline = [
        {"$match": {"user_id": user["id"]}},
        {"$group": {
            "_id": "$session_id",
            "last_message": {"$last": "$content"},
            "timestamp": {"$last": "$timestamp"},
            "message_count": {"$sum": 1}
        }},
        {"$sort": {"timestamp": -1}},
        {"$limit": 20}
    ]
    sessions = await db.chat_messages.aggregate(pipeline).to_list(20)
    return [{"session_id": s["_id"], "preview": s["last_message"][:50], "timestamp": s["timestamp"], "count": s["message_count"]} for s in sessions]

@api_router.delete("/chat/session/{session_id}")
async def delete_chat_session(session_id: str, user: dict = Depends(get_current_user)):
    """Delete all messages in a chat session belonging to the current user."""
    result = await db.chat_messages.delete_many({"user_id": user["id"], "session_id": session_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"deleted": result.deleted_count}

# ============== Birth Chart Routes ==============

@api_router.get("/chart/me")
async def get_my_chart(user: dict = Depends(get_current_user), recalculate: bool = False):
    """Get or generate the user's birth chart using Swiss Ephemeris"""
    
    # Check for existing chart unless recalculate is requested
    if not recalculate:
        chart = await db.birth_charts.find_one({"user_id": user["id"]}, {"_id": 0})
        if chart and chart.get("calculation_method") == "Swiss Ephemeris":
            return chart
    
    # Get user's birth data
    birth_date = user.get("birth_date", "1990-01-01")
    birth_time = user.get("birth_time")
    birth_place = user.get("birth_place", "")
    
    # Get coordinates from place name or user's stored coordinates
    latitude = user.get("birth_latitude") or 0.0
    longitude = user.get("birth_longitude") or 0.0
    
    if (latitude == 0.0 and longitude == 0.0) and birth_place:
        latitude, longitude = get_coordinates(birth_place)
    
    # Calculate chart using Swiss Ephemeris
    chart_data = calculate_natal_chart(
        birth_date=birth_date,
        birth_time=birth_time,
        latitude=latitude,
        longitude=longitude
    )

    # Calculate numerology from name and birth date
    numerology_name = (user.get("birth_name") or user.get("name") or "").strip()
    numerology = calculate_numerology(numerology_name, birth_date) if numerology_name else {}

    # Build chart document
    chart_doc = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "sun_sign": chart_data["sun_sign"],
        "moon_sign": chart_data["moon_sign"],
        "rising_sign": chart_data["rising_sign"],
        "planets": chart_data["planets"],
        "houses": chart_data["houses"],
        "ascendant": chart_data.get("ascendant", {}),
        "midheaven": chart_data.get("midheaven", {}),
        "aspects": chart_data["aspects"],
        "patterns": chart_data["patterns"],
        "numerology": numerology,
        "calculation_method": "Swiss Ephemeris",
        "julian_day": chart_data.get("julian_day"),
        "birth_coordinates": {"latitude": latitude, "longitude": longitude},
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Update or insert chart
    await db.birth_charts.delete_many({"user_id": user["id"]})
    await db.birth_charts.insert_one(chart_doc)
    
    # Update user's sun sign if it changed
    if chart_data["sun_sign"] != user.get("sun_sign"):
        await db.users.update_one(
            {"id": user["id"]},
            {"$set": {"sun_sign": chart_data["sun_sign"], "moon_sign": chart_data["moon_sign"]}}
        )
    
    return {k: v for k, v in chart_doc.items() if k != "_id"}


@api_router.get("/numerology/me")
async def get_my_numerology(user: dict = Depends(get_current_user)):
    """Return Pythagorean numerology profile for the current user.

    Uses ``birth_name`` (legal name) when set, falls back to display ``name``.
    Looks up cached chart first so numerology is consistent with the chart page.
    """
    # Return cached result from stored chart when available
    chart = await db.birth_charts.find_one({"user_id": user["id"]}, {"_id": 0, "numerology": 1})
    if chart and chart.get("numerology"):
        return chart["numerology"]

    # Recalculate on-the-fly if chart hasn't been generated yet
    name = (user.get("birth_name") or user.get("name") or "").strip()
    birth_date = user.get("birth_date", "1990-01-01")
    if not name:
        return {}
    return calculate_numerology(name, birth_date)


@api_router.post("/chart/share")
async def generate_share_token(user: dict = Depends(get_current_user)):
    """Generate (or return existing) a public share token for the user's chart."""
    chart = await db.birth_charts.find_one({"user_id": user["id"]}, {"_id": 0})
    if not chart:
        raise HTTPException(status_code=404, detail="No chart found. Generate your chart first.")

    # Reuse existing token if present — avoids invalidating links already emailed
    if chart.get("share_token"):
        return {"share_token": chart["share_token"]}

    share_token = str(uuid.uuid4())
    await db.birth_charts.update_one(
        {"user_id": user["id"]},
        {"$set": {"share_token": share_token}},
    )
    return {"share_token": share_token}

@api_router.delete("/chart/share")
async def revoke_share_token(user: dict = Depends(get_current_user)):
    """Revoke the public share token (makes the chart private again)."""
    await db.birth_charts.update_one(
        {"user_id": user["id"]},
        {"$unset": {"share_token": ""}},
    )
    return {"revoked": True}

@api_router.get("/chart/public/{share_token}")
async def get_public_chart(share_token: str):
    """Public endpoint — returns a sanitized chart by share token (no auth required)."""
    chart = await db.birth_charts.find_one({"share_token": share_token}, {"_id": 0})
    if not chart:
        raise HTTPException(status_code=404, detail="Chart not found or sharing has been disabled.")
    # Strip internal fields before returning
    public_fields = {
        k: v for k, v in chart.items()
        if k not in ("user_id", "share_token")
    }
    return public_fields

# ============== Transit Routes ==============

@api_router.get("/transits/upcoming")
async def get_upcoming_transits(user: dict = Depends(get_current_user)):
    """Get upcoming transit activations for the user using Swiss Ephemeris"""
    
    # Get user's natal chart
    chart = await db.birth_charts.find_one({"user_id": user["id"]}, {"_id": 0})
    
    if not chart or "planets" not in chart:
        # Generate chart first if doesn't exist
        birth_date = user.get("birth_date", "1990-01-01")
        birth_time = user.get("birth_time")
        birth_place = user.get("birth_place", "")
        latitude, longitude = get_coordinates(birth_place) if birth_place else (0.0, 0.0)
        
        chart_data = calculate_natal_chart(birth_date, birth_time, latitude, longitude)
        natal_positions = chart_data.get("planets", {})
    else:
        natal_positions = chart.get("planets", {})
    
    # Calculate current transits to natal chart
    current_transits = calculate_current_transits(natal_positions)
    
    today = datetime.now(timezone.utc)
    transits = []
    
    # Transit interpretations
    transit_meanings = {
        ("jupiter", "sun", "trine"): {
            "interpretation": "A period of expansion, luck, and opportunity. Your confidence is boosted and doors open easily.",
            "action_items": ["Take bold action on goals", "Expand your horizons", "Share your vision with others"]
        },
        ("jupiter", "sun", "conjunction"): {
            "interpretation": "Major growth and abundance. This is your personal Jupiter return moment - dream big!",
            "action_items": ["Start new ventures", "Travel or learn something new", "Celebrate your achievements"]
        },
        ("saturn", "sun", "square"): {
            "interpretation": "A testing period requiring discipline and patience. Build solid foundations.",
            "action_items": ["Review commitments", "Set realistic goals", "Practice patience"]
        },
        ("saturn", "sun", "opposition"): {
            "interpretation": "Time to evaluate your path and responsibilities. Maturity is required.",
            "action_items": ["Assess long-term goals", "Take responsibility", "Make necessary adjustments"]
        },
        ("uranus", "sun", "conjunction"): {
            "interpretation": "Unexpected changes and breakthroughs. Embrace your authentic self.",
            "action_items": ["Welcome change", "Express individuality", "Try something new"]
        },
        ("neptune", "sun", "trine"): {
            "interpretation": "Enhanced intuition and creativity. Spiritual insights flow easily.",
            "action_items": ["Trust your intuition", "Engage in creative pursuits", "Practice meditation"]
        },
        ("pluto", "sun", "square"): {
            "interpretation": "Powerful transformation. Old patterns are breaking down for renewal.",
            "action_items": ["Release what no longer serves", "Embrace personal power", "Dig deep"]
        },
    }
    
    for transit in current_transits[:6]:  # Top 6 transits
        key = (transit["transit_planet"], transit["natal_planet"], transit["aspect"])
        meaning = transit_meanings.get(key, {
            "interpretation": f"{transit['transit_planet'].title()} {transit['aspect']} your natal {transit['natal_planet'].title()} - a significant cosmic activation.",
            "action_items": ["Pay attention to this area of life", "Journal your experiences", "Stay open to insights"]
        })
        
        # Estimate transit duration based on planet speed
        duration_days = {
            "jupiter": 14, "saturn": 21, "uranus": 30, 
            "neptune": 45, "pluto": 60
        }.get(transit["transit_planet"], 7)
        
        transits.append({
            "id": str(uuid.uuid4()),
            "transit_type": f"{transit['transit_planet'].title()} {transit['aspect']} {transit['natal_planet'].title()}",
            "planet": transit["transit_planet"].title(),
            "aspect": transit["aspect"],
            "natal_planet": transit["natal_planet"].title(),
            "transit_sign": transit["transit_sign"],
            "orb": transit["orb"],
            "start_date": (today - timedelta(days=duration_days//3)).isoformat(),
            "peak_date": today.isoformat(),
            "end_date": (today + timedelta(days=duration_days*2//3)).isoformat(),
            "strength": round(1 - (transit["orb"] / 8), 2),
            "harmony": transit["harmony"],
            "interpretation": meaning["interpretation"],
            "action_items": meaning["action_items"]
        })
    
    # If no significant transits, return some current planetary positions
    if not transits:
        transits = [{
            "id": str(uuid.uuid4()),
            "transit_type": "Current cosmic weather",
            "planet": "General",
            "aspect": "influence",
            "natal_planet": "Chart",
            "start_date": today.isoformat(),
            "peak_date": today.isoformat(),
            "end_date": (today + timedelta(days=7)).isoformat(),
            "strength": 0.5,
            "interpretation": "A relatively quiet transit period. Good time for reflection and integration.",
            "action_items": ["Review recent experiences", "Plan for upcoming opportunities", "Rest and recharge"]
        }]
    
    return transits

# ============== Daily Guidance ==============

@api_router.get("/guidance/daily", response_model=DailyGuidance)
async def get_daily_guidance(user: dict = Depends(get_current_user)):
    """Get personalized daily guidance"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sun_sign = user.get("sun_sign", "Unknown")
    
    # Check cache (24-hour window)
    cached = await db.daily_guidance.find_one(
        {"user_id": user["id"], "date": today},
        {"_id": 0}
    )
    if cached:
        return DailyGuidance(**cached)
    
    # Get current transits for personalization
    transits_summary = ""
    numerology_block = ""
    try:
        chart = await db.birth_charts.find_one({"user_id": user["id"]}, {"_id": 0})
        natal_positions = chart.get("planets", {}) if chart else {}
        if natal_positions:
            current_transits = calculate_current_transits(natal_positions)
            transits_summary = "\n".join([
                f"- {t['transit_planet'].title()} {t['aspect']} natal {t['natal_planet'].title()} (orb {t['orb']:.1f}°)"
                for t in current_transits[:5]
            ])
        # Numerology for daily tone — only include lines with real values
        if chart and chart.get("numerology"):
            num = chart["numerology"]
            lp = num.get("life_path", {})
            py = num.get("personal_year", {})
            lines = []
            if lp.get("number"):
                lines.append(f"- Life Path {lp['number']} ({lp.get('keyword', '')})")
            if py.get("number"):
                lines.append(f"- Personal Year {py['number']} ({py.get('keyword', '')}) — {py.get('theme', '')}")
            if lines:
                numerology_block = "\n".join(lines)
    except Exception as e:
        logging.warning(f"Could not fetch transits for daily guidance: {e}")

    # Sanitize user fields used in the prompt to prevent prompt injection
    safe_name = str(user.get('name', 'Seeker'))[:50].replace('\n', ' ').replace('\r', ' ')
    safe_sun_sign = str(sun_sign)[:20].replace('\n', ' ').replace('\r', ' ')
    safe_birth_date = str(user.get('birth_date', 'Unknown'))[:12].replace('\n', ' ')

    # Generate LLM-powered guidance
    prompt = f"""Generate personalized daily astrology guidance for today ({today}).

USER PROFILE:
- Name: {safe_name}
- Sun Sign: {safe_sun_sign}
- Birth Date: {safe_birth_date}

CURRENT ACTIVE TRANSITS:
{transits_summary or "No significant transits calculated"}

NUMEROLOGY:
{numerology_block or "Not available"}

Provide a JSON-structured daily guidance with:
1. overall_energy: A 1-2 sentence summary of today's cosmic energy for this person (weave in numerology if relevant)
2. focus_areas: A list of exactly 3 specific life areas to focus on today (strings)
3. action_items: A list of exactly 3 concrete, actionable tasks for today (strings)
4. transit_highlights: A list of exactly 2 objects, each with keys "transit", "influence", and "advice"

Respond ONLY with valid JSON matching this exact structure:
{{
  "overall_energy": "...",
  "focus_areas": ["...", "...", "..."],
  "action_items": ["...", "...", "..."],
  "transit_highlights": [
    {{"transit": "...", "influence": "...", "advice": "..."}},
    {{"transit": "...", "influence": "...", "advice": "..."}}
  ]
}}"""

    guidance = None
    try:
        if not openai_client:
            raise RuntimeError("OpenAI not configured")
        completion = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are Gab44, an expert astrology AI. Return only valid JSON as instructed."},
                {"role": "user", "content": prompt},
            ],
        )
        raw = completion.choices[0].message.content.strip()
        match = re.search(r"```(?:json)?\s*([\s\S]+?)```", raw)
        if match:
            raw = match.group(1).strip()
        parsed = json.loads(raw)
        guidance = {
            "date": today,
            "overall_energy": parsed["overall_energy"],
            "focus_areas": parsed["focus_areas"],
            "action_items": parsed["action_items"],
            "transit_highlights": parsed["transit_highlights"]
        }
    except Exception as e:
        logging.error(f"LLM daily guidance error: {e}")

    # Fallback to static guidance if LLM unavailable
    if guidance is None:
        guidance = {
            "date": today,
            "overall_energy": f"The cosmic energies today support {sun_sign}'s natural strengths. Focus on clarity and intentional action.",
            "focus_areas": [
                "Personal growth and self-reflection",
                "Communication with close relationships",
                "Financial planning and resource management"
            ],
            "action_items": [
                "Set one clear intention for the day",
                "Reach out to someone you've been meaning to connect with",
                "Review your weekly goals and adjust priorities"
            ],
            "transit_highlights": [
                {
                    "transit": "Moon influence",
                    "influence": "Emotional grounding and stability",
                    "advice": "Take time to appreciate simple pleasures"
                },
                {
                    "transit": "Current planetary weather",
                    "influence": "Expanded thinking and optimism",
                    "advice": "Great day for learning and big-picture planning"
                }
            ]
        }
    
    # Cache for the day
    guidance_doc = {"user_id": user["id"], **guidance}
    await db.daily_guidance.insert_one(guidance_doc)
    
    return DailyGuidance(**guidance)

# ============== Compatibility Routes ==============

@api_router.post("/compatibility/analyze")
async def analyze_compatibility(request: CompatibilityRequest, user: dict = Depends(get_current_user)):
    """Generate a comprehensive compatibility/synastry analysis using Swiss Ephemeris"""
    
    # Get or calculate user's chart
    user_chart = await db.birth_charts.find_one({"user_id": user["id"]}, {"_id": 0})
    if not user_chart or user_chart.get("calculation_method") != "Swiss Ephemeris":
        # Generate real chart using Swiss Ephemeris
        birth_date = user.get("birth_date", "1990-01-01")
        birth_time = user.get("birth_time")
        birth_place = user.get("birth_place", "")
        latitude, longitude = get_coordinates(birth_place) if birth_place else (0.0, 0.0)
        
        user_chart = calculate_natal_chart(birth_date, birth_time, latitude, longitude)
    
    # Calculate partner's chart using Swiss Ephemeris
    partner_latitude, partner_longitude = get_coordinates(request.partner_birth_place)
    partner_chart = calculate_natal_chart(
        birth_date=request.partner_birth_date,
        birth_time=request.partner_birth_time,
        latitude=partner_latitude,
        longitude=partner_longitude
    )
    
    partner_sun = partner_chart["sun_sign"]
    
    # Calculate compatibility scores
    element_compat = calculate_element_compatibility(user_chart["sun_sign"], partner_sun)
    modality_compat = calculate_modality_compatibility(user_chart["sun_sign"], partner_sun)
    
    # Calculate synastry aspects using real planetary positions
    synastry_aspects = calculate_synastry_aspects(user_chart, partner_chart)
    
    # Generate composite chart
    composite = generate_composite_chart(user_chart, partner_chart)
    
    # Calculate category scores
    romantic_aspects = [a for a in synastry_aspects if a["category"] == "romantic"]
    emotional_aspects = [a for a in synastry_aspects if a["category"] == "emotional"]
    comm_aspects = [a for a in synastry_aspects if a["category"] == "communication"]
    karmic_aspects = [a for a in synastry_aspects if a["category"] == "karmic"]
    
    category_scores = {
        "romantic": min(95, 60 + len(romantic_aspects) * 8 + sum(a["harmony"] * 10 for a in romantic_aspects)),
        "emotional": min(95, 55 + len(emotional_aspects) * 10 + sum(a["harmony"] * 12 for a in emotional_aspects)),
        "communication": min(95, 50 + len(comm_aspects) * 12 + sum(a["harmony"] * 15 for a in comm_aspects)),
        "stability": (element_compat["score"] + modality_compat["score"]) / 2,
        "karmic": min(95, 40 + len(karmic_aspects) * 15)
    }
    
    # Overall score
    overall_score = (
        element_compat["score"] * 0.25 +
        modality_compat["score"] * 0.15 +
        category_scores["romantic"] * 0.25 +
        category_scores["emotional"] * 0.20 +
        category_scores["communication"] * 0.15
    )
    
    # Generate AI analysis
    scores_for_ai = {
        "overall": round(overall_score),
        **{k: round(v) for k, v in category_scores.items()}
    }
    
    partner_data = {"name": request.partner_name, "sun_sign": partner_sun}
    ai_analysis = await generate_compatibility_analysis(user, partner_data, synastry_aspects, scores_for_ai)
    
    # Determine strengths and challenges based on aspects
    strengths = []
    challenges = []
    
    for aspect in synastry_aspects[:10]:
        if aspect["harmony"] >= 0.7:
            strengths.append(f"{aspect['person1_planet'].title()}-{aspect['person2_planet'].title()} {aspect['aspect_type']}: Natural harmony in {aspect['category']} matters")
        elif aspect["harmony"] <= 0.5:
            challenges.append(f"{aspect['person1_planet'].title()}-{aspect['person2_planet'].title()} {aspect['aspect_type']}: Growth opportunity in {aspect['category']} areas")
    
    # Build the report
    report = {
        "id": str(uuid.uuid4()),
        "user_id": user["id"],
        "partner_name": request.partner_name,
        "partner_birth_date": request.partner_birth_date,
        "partner_sun_sign": partner_sun,
        "overall_score": round(overall_score, 1),
        "category_scores": {k: round(v, 1) for k, v in category_scores.items()},
        "synastry_aspects": synastry_aspects,
        "composite_chart": composite,
        "element_compatibility": element_compat,
        "modality_compatibility": modality_compat,
        "strengths": strengths[:5],
        "challenges": challenges[:5],
        "karmic_themes": [
            f"Soul growth through {get_sign_element(user_chart['sun_sign'])}-{get_sign_element(partner_sun)} integration",
            f"Learning {modality_compat['description'].lower()}"
        ],
        "growth_opportunities": [
            "Embrace differences as complementary strengths",
            "Use challenges as catalysts for personal evolution",
            "Build on natural harmonies while working on friction points"
        ],
        "ai_analysis": ai_analysis,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Save to database
    await db.compatibility_reports.insert_one(report)
    
    # Return without _id
    return {k: v for k, v in report.items() if k != "_id"}

@api_router.get("/compatibility/reports")
async def get_compatibility_reports(user: dict = Depends(get_current_user)):
    """Get all compatibility reports for the current user"""
    reports = await db.compatibility_reports.find(
        {"user_id": user["id"]},
        {"_id": 0}
    ).sort("created_at", -1).to_list(20)
    return reports

@api_router.get("/compatibility/reports/{report_id}")
async def get_compatibility_report(report_id: str, user: dict = Depends(get_current_user)):
    """Get a specific compatibility report"""
    report = await db.compatibility_reports.find_one(
        {"id": report_id, "user_id": user["id"]},
        {"_id": 0}
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

# ============== Pricing/Subscription Info ==============

@api_router.get("/pricing")
async def get_pricing():
    """Get pricing plans"""
    return {
        "plans": [
            {
                "id": "seeker",
                "name": "Seeker",
                "tagline": "For those just starting their journey",
                "price": 0,
                "period": "month",
                "features": [
                    "Basic Chart Overview",
                    "Daily Short Guidance",
                    "1 Compatibility Reading",
                    "Educational Library"
                ],
                "cta": "Create Your Free Chart"
            },
            {
                "id": "enthusiast",
                "name": "Enthusiast",
                "tagline": "For daily guidance and deeper insights",
                "price": 19.99,
                "period": "month",
                "popular": True,
                "features": [
                    "Everything in Seeker",
                    "Daily AI Coaching",
                    "Monthly Detailed Reports",
                    "Unlimited Compatibility",
                    "30-Day Transit Forecasts"
                ],
                "cta": "Start Free Trial"
            },
            {
                "id": "advanced",
                "name": "Advanced",
                "tagline": "For serious practitioners and coaches",
                "price": 49.99,
                "period": "month",
                "features": [
                    "Everything in Enthusiast",
                    "Advanced Predictive Tools",
                    "90-Day Transit Forecasts",
                    "Chart Pattern Analysis",
                    "Export to PDF"
                ],
                "cta": "Upgrade Now"
            },
            {
                "id": "professional",
                "name": "Professional",
                "tagline": "For astrologers serving clients",
                "price": 99,
                "period": "month",
                "features": [
                    "Everything in Advanced",
                    "Client Management System",
                    "White-label Reports",
                    "API Access",
                    "Priority Support"
                ],
                "cta": "Contact Sales"
            }
        ]
    }

# ============== OneSignal Helper ==============

def send_onesignal_notification(player_ids: List[str], title: str, message: str, url: str = "/dashboard") -> bool:
    """Send a push notification via OneSignal REST API."""
    if not ONESIGNAL_APP_ID or not ONESIGNAL_API_KEY or not player_ids:
        return False
    try:
        payload = {
            "app_id": ONESIGNAL_APP_ID,
            "include_player_ids": player_ids,
            "headings": {"en": title},
            "contents": {"en": message},
            "url": url,
        }
        resp = _requests.post(
            ONESIGNAL_API_URL,
            json=payload,
            headers={
                "Authorization": f"Key {ONESIGNAL_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        resp.raise_for_status()
        return True
    except Exception as exc:
        logging.error("OneSignal notification failed: %s", exc)
        return False

# ============== Payment Routes (Stripe) ==============

@api_router.post("/payments/create-checkout-session")
async def create_checkout_session(req: CheckoutRequest, user: dict = Depends(get_current_user)):
    """Create a Stripe Checkout session for a subscription plan."""
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Payment processing not configured")

    tier = req.tier.lower()
    plan = STRIPE_PLAN_PRICES.get(tier)
    if not plan:
        raise HTTPException(status_code=400, detail=f"Unknown plan: {tier}. Choose enthusiast or advanced.")

    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")

    # Attach or retrieve Stripe customer for this user
    stripe_customer_id = user.get("stripe_customer_id")
    if not stripe_customer_id:
        customer = stripe.Customer.create(
            email=user["email"],
            name=user.get("name", ""),
            metadata={"user_id": user["id"]},
        )
        stripe_customer_id = customer.id
        await db.users.update_one({"id": user["id"]}, {"$set": {"stripe_customer_id": stripe_customer_id}})

    session = stripe.checkout.Session.create(
        customer=stripe_customer_id,
        payment_method_types=["card"],
        mode="subscription",
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": plan["name"]},
                "unit_amount": plan["amount"],
                "recurring": {"interval": "month"},
            },
            "quantity": 1,
        }],
        success_url=f"{frontend_url}/dashboard?subscription=success&tier={tier}",
        cancel_url=f"{frontend_url}/pricing",
        metadata={"user_id": user["id"], "tier": tier},
    )

    return {"checkout_url": session.url, "session_id": session.id}


@api_router.post("/payments/portal")
async def create_portal_session(user: dict = Depends(get_current_user)):
    """Create a Stripe Customer Portal session so the user can manage/cancel their subscription."""
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Payment processing not configured")

    stripe_customer_id = user.get("stripe_customer_id")
    if not stripe_customer_id:
        raise HTTPException(status_code=400, detail="No active subscription found")

    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    session = stripe.billing_portal.Session.create(
        customer=stripe_customer_id,
        return_url=f"{frontend_url}/settings",
    )
    return {"portal_url": session.url}


@api_router.post("/payments/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events."""
    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Payment processing not configured")

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        if STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        else:
            # Accept without signature verification when webhook secret not configured (dev only)
            event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        logging.error("Stripe webhook error: %s", e)
        raise HTTPException(status_code=400, detail="Invalid webhook payload")

    event_type = event["type"]
    logging.info("Stripe webhook: %s", event_type)

    if event_type == "checkout.session.completed":
        session_obj = event["data"]["object"]
        user_id = session_obj.get("metadata", {}).get("user_id")
        tier = session_obj.get("metadata", {}).get("tier")
        stripe_customer_id = session_obj.get("customer")
        stripe_subscription_id = session_obj.get("subscription")

        if user_id and tier:
            await db.users.update_one(
                {"id": user_id},
                {"$set": {
                    "subscription_tier": tier,
                    "stripe_customer_id": stripe_customer_id,
                    "stripe_subscription_id": stripe_subscription_id,
                }},
            )
            logging.info("Upgraded user %s to %s", user_id, tier)

    elif event_type in ("customer.subscription.updated", "customer.subscription.deleted"):
        sub = event["data"]["object"]
        stripe_customer_id = sub.get("customer")
        status_val = sub.get("status")

        user_doc = await db.users.find_one({"stripe_customer_id": stripe_customer_id}, {"_id": 0})
        if user_doc:
            if event_type == "customer.subscription.deleted" or status_val in ("canceled", "unpaid", "past_due"):
                await db.users.update_one(
                    {"stripe_customer_id": stripe_customer_id},
                    {"$set": {"subscription_tier": "seeker", "stripe_subscription_id": None}},
                )
                logging.info("Downgraded customer %s to seeker", stripe_customer_id)

    return {"received": True}


# ============== Notification Routes (OneSignal) ==============

@api_router.post("/notifications/register-device")
async def register_device(reg: DeviceRegistration, user: dict = Depends(get_current_user)):
    """Store a OneSignal player_id for push notification delivery."""
    player_id = reg.player_id.strip()
    if not player_id:
        raise HTTPException(status_code=400, detail="player_id is required")

    await db.users.update_one(
        {"id": user["id"]},
        {"$addToSet": {"onesignal_player_ids": player_id}},
    )
    return {"registered": True}


@api_router.post("/notifications/send-daily")
async def send_daily_notifications(admin: dict = Depends(require_admin)):
    """Admin endpoint: send daily guidance push to all users with push enabled."""
    users_with_push = await db.users.find(
        {"onesignal_player_ids": {"$exists": True, "$ne": []}},
        {"_id": 0, "onesignal_player_ids": 1},
    ).to_list(1000)

    all_player_ids = []
    for u in users_with_push:
        all_player_ids.extend(u.get("onesignal_player_ids", []))

    if not all_player_ids:
        return {"sent": False, "reason": "No registered devices"}

    today = datetime.now(timezone.utc).strftime("%B %d")
    sent = send_onesignal_notification(
        player_ids=all_player_ids,
        title="✨ Your Daily Cosmic Guidance",
        message=f"Your personalized astrological guidance for {today} is ready.",
        url="/dashboard",
    )
    return {"sent": sent, "devices": len(all_player_ids)}

# ============== Newsletter / Contact Routes (Public) ==============

@api_router.post("/subscribe")
async def subscribe_newsletter(sub: NewsletterSubscription):
    """Capture email for newsletter / marketing list."""
    existing = await db.newsletter_subscribers.find_one({"email": sub.email})
    if existing:
        return {"subscribed": True, "already_subscribed": True}

    await db.newsletter_subscribers.insert_one({
        "id": str(uuid.uuid4()),
        "email": sub.email,
        "name": sub.name,
        "subscribed_at": datetime.now(timezone.utc).isoformat(),
        "active": True,
    })

    # Send confirmation email (non-blocking fire-and-forget)
    greeting = f"Hi {sub.name}!" if sub.name else "Hi there!"
    confirm_html = build_promotional_email(
        name=sub.name or "Seeker",
        headline="You're In! 🌟",
        body_html=f"""
          <p>{greeting} Thanks for subscribing to Gab44 Cosmic Updates.</p>
          <p>You'll receive weekly astrological guidance, feature announcements, and exclusive offers directly in your inbox.</p>
          <p>In the meantime, why not discover your full cosmic blueprint?</p>
        """,
        cta_text="Create My Free Chart",
        cta_url=f"{os.environ.get('FRONTEND_URL','https://gab44.com')}/auth?mode=register",
    )
    send_email(
        to_email=sub.email,
        subject="Welcome to Gab44 Cosmic Updates ✨",
        html_content=confirm_html,
        from_email=EMAIL_MARKETING,
    )
    return {"subscribed": True, "already_subscribed": False}

@api_router.post("/contact")
async def submit_contact_form(msg: ContactMessage):
    """Store a contact/support ticket and forward to support email."""
    ticket_id = str(uuid.uuid4())
    await db.contact_messages.insert_one({
        "id": ticket_id,
        "name": msg.name,
        "email": msg.email,
        "subject": msg.subject,
        "message": msg.message,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "open",
    })

    # Forward to support inbox
    support_html = f"""
    <div style="font-family:sans-serif;font-size:14px;color:#333;">
      <h2 style="color:#c9a84c;">New Support Ticket #{ticket_id[:8]}</h2>
      <p><strong>From:</strong> {msg.name} &lt;{msg.email}&gt;</p>
      <p><strong>Subject:</strong> {msg.subject}</p>
      <hr style="border:1px solid #eee;margin:16px 0;"/>
      <p style="white-space:pre-wrap;">{msg.message}</p>
    </div>
    """
    send_email(
        to_email=EMAIL_SUPPORT,
        subject=f"[Gab44 Support] {msg.subject}",
        html_content=support_html,
        from_email=EMAIL_NOREPLY,
    )

    # Auto-reply to sender
    auto_reply = build_support_reply_email(
        name=msg.name,
        ticket_subject=msg.subject,
        reply_body=f"""
          <p>Thanks for reaching out. We've received your message and will get back to you
          within 1–2 business days.</p>
          <p><strong>Your ticket ID:</strong> <code>#{ticket_id[:8]}</code></p>
        """,
    )
    send_email(
        to_email=msg.email,
        subject=f"Re: {msg.subject} [Ticket #{ticket_id[:8]}]",
        html_content=auto_reply,
        from_email=EMAIL_SUPPORT,
    )
    return {"submitted": True, "ticket_id": ticket_id[:8]}

# ============== Health Check ==============

@api_router.get("/")
async def root():
    return {"message": "Gab44 API - Astrology AI Coaching Platform", "version": "2.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# ============== Admin Routes (Protected) ==============

@api_router.post("/admin/upgrade-all-users")
async def upgrade_all_users_to_advanced(admin: dict = Depends(require_admin)):
    """Upgrade all existing users to advanced tier (temporary until payment setup)"""
    result = await db.users.update_many(
        {"subscription_tier": {"$ne": "advanced"}},
        {"$set": {"subscription_tier": "advanced"}}
    )
    return {
        "message": "All users upgraded to advanced tier",
        "modified_count": result.modified_count
    }

@api_router.get("/admin/stats")
async def get_admin_stats(admin: dict = Depends(require_admin)):
    """Get platform statistics for admin dashboard"""
    total_users = await db.users.count_documents({})
    
    # Subscription breakdown
    subscription_stats = await db.users.aggregate([
        {"$group": {"_id": "$subscription_tier", "count": {"$sum": 1}}}
    ]).to_list(10)
    
    # Sun sign distribution
    sign_stats = await db.users.aggregate([
        {"$group": {"_id": "$sun_sign", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]).to_list(12)
    
    # Total chats
    total_chats = await db.chat_messages.count_documents({})
    total_sessions = len(await db.chat_messages.distinct("session_id"))
    
    # Total compatibility reports
    total_compatibility = await db.compatibility_reports.count_documents({})
    
    # Recent signups (last 7 days)
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    recent_signups = await db.users.count_documents({"created_at": {"$gte": week_ago}})
    
    return {
        "total_users": total_users,
        "recent_signups": recent_signups,
        "subscription_breakdown": {s["_id"]: s["count"] for s in subscription_stats},
        "sun_sign_distribution": {s["_id"]: s["count"] for s in sign_stats if s["_id"]},
        "total_chat_messages": total_chats,
        "total_chat_sessions": total_sessions,
        "total_compatibility_reports": total_compatibility
    }

@api_router.get("/admin/users")
async def get_all_users(skip: int = 0, limit: int = 50, admin: dict = Depends(require_admin)):
    """Get all users for admin dashboard"""
    users = await db.users.find(
        {},
        {"_id": 0, "password": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    # Add is_admin flag to each user
    for user in users:
        user_email = user.get("email", "").lower()
        is_admin_by_role = user.get("role") == "admin"
        is_admin_by_env = user_email in ADMIN_EMAILS
        user["is_admin"] = is_admin_by_role or is_admin_by_env
    
    total = await db.users.count_documents({})
    
    return {
        "users": users,
        "total": total,
        "skip": skip,
        "limit": limit
    }

@api_router.put("/admin/users/{user_id}/tier")
async def update_user_tier(user_id: str, tier: str, admin: dict = Depends(require_admin)):
    """Update a user's subscription tier"""
    valid_tiers = ["seeker", "enthusiast", "advanced", "professional"]
    if tier not in valid_tiers:
        raise HTTPException(status_code=400, detail=f"Invalid tier. Must be one of: {valid_tiers}")
    
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"subscription_tier": tier}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": f"User {user_id} updated to {tier} tier"}

@api_router.put("/admin/users/{user_id}/role")
async def update_user_role(user_id: str, role: str, admin: dict = Depends(require_admin)):
    """Grant or revoke admin role for a user"""
    valid_roles = ["user", "admin"]
    if role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {valid_roles}")
    
    # Prevent self-demotion
    if user_id == admin["id"] and role != "admin":
        raise HTTPException(status_code=400, detail="Cannot remove your own admin role")
    
    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"role": role}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    action = "granted" if role == "admin" else "revoked"
    return {"message": f"Admin role {action} for user {user_id}"}

@api_router.get("/admin/admins")
async def get_admin_users(admin: dict = Depends(require_admin)):
    """Get list of all admin users"""
    # Users with admin role in DB
    db_admins = await db.users.find(
        {"role": "admin"},
        {"_id": 0, "password": 0}
    ).to_list(100)
    
    # Users in ADMIN_EMAILS env var (bootstrap admins)
    env_admins = await db.users.find(
        {"email": {"$in": ADMIN_EMAILS}},
        {"_id": 0, "password": 0}
    ).to_list(100)
    
    # Merge and dedupe
    all_admins = {u["id"]: u for u in db_admins + env_admins}
    return list(all_admins.values())

def _do_email_blast(subject: str, body_html: str, recipients: list) -> None:
    """Background worker: sends marketing emails to a list of recipients."""
    frontend_url = os.environ.get("FRONTEND_URL", "https://gab44.com")
    for recipient in recipients:
        html = build_promotional_email(
            name=recipient.get("name", "Seeker"),
            headline=subject,
            body_html=body_html,
            cta_text="Open Gab44",
            cta_url=frontend_url,
        )
        send_email(
            to_email=recipient["email"],
            subject=subject,
            html_content=html,
            from_email=EMAIL_MARKETING,
        )

@api_router.post("/admin/send-email-blast")
async def send_email_blast(
    req: EmailBlastRequest,
    background_tasks: BackgroundTasks,
    admin: dict = Depends(require_admin),
):
    """Send a marketing email blast to a filtered subset of verified users (runs in background)."""
    query: dict = {"email_verified": True}
    if req.tier_filter != "all":
        query["subscription_tier"] = req.tier_filter

    # Fetch up to 10 000 recipients in batches using cursor
    recipients = await db.users.find(query, {"_id": 0, "email": 1, "name": 1}).to_list(10_000)
    if not recipients:
        return {"queued": 0, "message": "No matching recipients"}

    # Schedule the actual sends as a background task so the HTTP response is immediate
    background_tasks.add_task(_do_email_blast, req.subject, req.body_html, recipients)
    return {"queued": len(recipients), "message": f"Email blast queued for {len(recipients)} recipients"}

@api_router.get("/admin/newsletter-subscribers")
async def get_newsletter_subscribers(admin: dict = Depends(require_admin)):
    """Return all newsletter subscribers."""
    subs = await db.newsletter_subscribers.find(
        {"active": True}, {"_id": 0, "id": 1, "email": 1, "name": 1, "subscribed_at": 1}
    ).sort("subscribed_at", -1).to_list(5000)
    return {"count": len(subs), "subscribers": subs}

@api_router.get("/admin/contact-messages")
async def get_contact_messages(admin: dict = Depends(require_admin)):
    """Return all contact / support tickets."""
    tickets = await db.contact_messages.find(
        {}, {"_id": 0}
    ).sort("created_at", -1).to_list(500)
    return {"count": len(tickets), "tickets": tickets}

# Include router and setup middleware
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def create_indexes():
    """Create MongoDB indexes for performance"""
    # Users collection
    await db.users.create_index("email", unique=True)
    await db.users.create_index("id", unique=True)
    await db.users.create_index("stripe_customer_id", sparse=True)
    # Chat messages
    await db.chat_messages.create_index("user_id")
    await db.chat_messages.create_index("session_id")
    await db.chat_messages.create_index([("user_id", 1), ("session_id", 1)])
    # Chat message daily limit helper index
    await db.chat_messages.create_index([("user_id", 1), ("role", 1), ("timestamp", 1)])
    # Birth charts
    await db.birth_charts.create_index("user_id", unique=True)
    await db.birth_charts.create_index("share_token", sparse=True)
    # Compatibility reports
    await db.compatibility_reports.create_index("user_id")
    await db.compatibility_reports.create_index("id", unique=True)
    # Daily guidance cache
    await db.daily_guidance.create_index([("user_id", 1), ("date", 1)], unique=True)
    # Newsletter subscribers
    await db.newsletter_subscribers.create_index("email", unique=True)
    # Contact messages
    await db.contact_messages.create_index("created_at")
    logger.info("MongoDB indexes created")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
