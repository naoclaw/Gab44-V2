from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
from emergentintegrations.llm.chat import LlmChat, UserMessage

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

# LLM Configuration
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

# Admin emails (set via environment variable)
ADMIN_EMAILS = [e.strip().lower() for e in os.environ.get('ADMIN_EMAILS', '').split(',') if e.strip()]

app = FastAPI(title="Gab44 - Astrology AI Coaching Platform")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# ============== Models ==============

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    birth_date: str  # YYYY-MM-DD
    birth_time: Optional[str] = None  # HH:MM
    birth_place: str
    birth_latitude: Optional[float] = None
    birth_longitude: Optional[float] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    email: str
    name: str
    birth_date: str
    birth_time: Optional[str] = None
    birth_place: str
    birth_latitude: Optional[float] = None
    birth_longitude: Optional[float] = None
    sun_sign: Optional[str] = None
    subscription_tier: str = "seeker"
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

# ============== Astrology Helpers ==============

def calculate_sun_sign(birth_date: str) -> str:
    """Calculate sun sign from birth date"""
    date = datetime.strptime(birth_date, "%Y-%m-%d")
    month, day = date.month, date.day
    
    signs = [
        ((3, 21), (4, 19), "Aries"),
        ((4, 20), (5, 20), "Taurus"),
        ((5, 21), (6, 20), "Gemini"),
        ((6, 21), (7, 22), "Cancer"),
        ((7, 23), (8, 22), "Leo"),
        ((8, 23), (9, 22), "Virgo"),
        ((9, 23), (10, 22), "Libra"),
        ((10, 23), (11, 21), "Scorpio"),
        ((11, 22), (12, 21), "Sagittarius"),
        ((12, 22), (1, 19), "Capricorn"),
        ((1, 20), (2, 18), "Aquarius"),
        ((2, 19), (3, 20), "Pisces"),
    ]
    
    for start, end, sign in signs:
        if start[0] == 12 and month == 12 and day >= start[1]:
            return sign
        if start[0] == 12 and month == 1 and day <= end[1]:
            return sign
        if start[0] <= month <= end[0]:
            if month == start[0] and day >= start[1]:
                return sign
            if month == end[0] and day <= end[1]:
                return sign
            if start[0] < month < end[0]:
                return sign
    
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
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"compatibility-{user['id']}-{uuid.uuid4()}",
            system_message="You are Gab44, an expert relationship astrologer. Provide insightful, compassionate compatibility analysis that helps people understand their relationship dynamics and growth opportunities."
        ).with_model("openai", "gpt-4o")
        
        response = await chat.send_message(UserMessage(text=prompt))
        return response
    except Exception as e:
        logging.error(f"Compatibility analysis error: {e}")
        return f"Based on the {user_sun}-{partner_sun} pairing, this relationship shows {scores.get('overall', 70)}% compatibility. Key themes include balancing {get_sign_element(user_sun)} and {get_sign_element(partner_sun)} energies."

# ============== AI Coach ==============

async def get_ai_coach_response(user: dict, message: str, session_id: str) -> str:
    """Generate AI coaching response using emergentintegrations"""
    
    # Get user's chat history
    history = await db.chat_messages.find(
        {"user_id": user["id"], "session_id": session_id},
        {"_id": 0}
    ).sort("timestamp", 1).limit(20).to_list(20)
    
    # Build context
    sun_sign = user.get("sun_sign", "Unknown")
    element = get_sign_element(sun_sign)
    modality = get_sign_modality(sun_sign)
    
    system_message = f"""You are Gab44, an advanced astrology AI coach. Your mission is to help people live measurably better lives through truthful astrological guidance.

USER PROFILE:
- Name: {user.get('name', 'Seeker')}
- Sun Sign: {sun_sign} ({element}, {modality})
- Birth Date: {user.get('birth_date', 'Unknown')}
- Birth Place: {user.get('birth_place', 'Unknown')}

YOUR PRINCIPLES:
1. Every response must help the user make better decisions
2. Be truthful, even when uncomfortable - truth serves growth
3. Provide actionable guidance, not just information
4. Adapt your tone to be warm but wise
5. Connect astrological insights to practical life outcomes
6. Ask follow-up questions to understand if guidance was helpful

RESPONSE FORMAT:
- Keep responses conversational but substantive
- Include specific action items when relevant
- Reference the user's chart when applicable
- End with a thoughtful question or call to action"""

    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"gab44-{user['id']}-{session_id}",
            system_message=system_message
        ).with_model("openai", "gpt-4o")
        
        # Build conversation history context
        history_text = ""
        for msg in history[-10:]:  # Last 10 messages for context
            role = "User" if msg["role"] == "user" else "Gab44"
            history_text += f"\n{role}: {msg['content']}"
        
        full_message = message
        if history_text:
            full_message = f"Previous conversation:{history_text}\n\nUser's new message: {message}"
        
        user_message = UserMessage(text=full_message)
        response = await chat.send_message(user_message)
        return response
        
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
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.users.insert_one(user_doc)
    
    token = create_token(user_id)
    user_profile = {k: v for k, v in user_doc.items() if k != "password" and k != "_id"}
    
    return TokenResponse(access_token=token, user=UserProfile(**user_profile))

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_token(user["id"])
    user_profile = {k: v for k, v in user.items() if k != "password" and k != "_id"}
    
    return TokenResponse(access_token=token, user=UserProfile(**user_profile))

@api_router.get("/auth/me")
async def get_me(user: dict = Depends(get_current_user)):
    # Include is_admin in response
    response = {**user}
    return response

# ============== Chat Routes ==============

@api_router.post("/chat", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest, user: dict = Depends(get_current_user)):
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

# ============== Birth Chart Routes ==============

@api_router.get("/chart/me")
async def get_my_chart(user: dict = Depends(get_current_user)):
    """Get or generate the user's birth chart"""
    chart = await db.birth_charts.find_one({"user_id": user["id"]}, {"_id": 0})
    
    if not chart:
        # Generate a basic chart (in production, use Swiss Ephemeris)
        sun_sign = user.get("sun_sign", calculate_sun_sign(user.get("birth_date", "1990-01-01")))
        
        # Simulated chart data - in production, calculate with Swiss Ephemeris
        chart_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user["id"],
            "sun_sign": sun_sign,
            "moon_sign": "Scorpio",  # Would be calculated
            "rising_sign": "Leo",     # Would be calculated
            "planets": {
                "sun": {"sign": sun_sign, "degree": 15.5, "house": 10},
                "moon": {"sign": "Scorpio", "degree": 22.3, "house": 4},
                "mercury": {"sign": "Taurus", "degree": 8.7, "house": 10},
                "venus": {"sign": "Gemini", "degree": 3.2, "house": 11},
                "mars": {"sign": "Aries", "degree": 28.9, "house": 9},
                "jupiter": {"sign": "Scorpio", "degree": 5.1, "house": 4},
                "saturn": {"sign": "Pisces", "degree": 12.8, "house": 8},
                "uranus": {"sign": "Capricorn", "degree": 25.4, "house": 6},
                "neptune": {"sign": "Capricorn", "degree": 22.1, "house": 6},
                "pluto": {"sign": "Scorpio", "degree": 27.6, "house": 4}
            },
            "houses": {
                "1": "Leo", "2": "Virgo", "3": "Libra", "4": "Scorpio",
                "5": "Sagittarius", "6": "Capricorn", "7": "Aquarius", "8": "Pisces",
                "9": "Aries", "10": "Taurus", "11": "Gemini", "12": "Cancer"
            },
            "aspects": [
                {"planet1": "sun", "planet2": "moon", "aspect": "opposition", "orb": 2.3},
                {"planet1": "venus", "planet2": "mars", "aspect": "sextile", "orb": 1.5},
                {"planet1": "jupiter", "planet2": "pluto", "aspect": "conjunction", "orb": 0.5}
            ],
            "patterns": ["T-Square", "Grand Trine (Water)"],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.birth_charts.insert_one(chart_doc)
        # Return the chart without _id (which MongoDB adds during insert)
        chart = {k: v for k, v in chart_doc.items() if k != "_id"}
    
    return chart

# ============== Transit Routes ==============

@api_router.get("/transits/upcoming")
async def get_upcoming_transits(user: dict = Depends(get_current_user)):
    """Get upcoming transit activations for the user"""
    # In production, these would be calculated based on current planetary positions
    today = datetime.now(timezone.utc)
    
    transits = [
        {
            "id": str(uuid.uuid4()),
            "transit_type": "Jupiter trine Sun",
            "planet": "Jupiter",
            "aspect": "trine",
            "natal_planet": "Sun",
            "start_date": today.isoformat(),
            "peak_date": (today + timedelta(days=3)).isoformat(),
            "end_date": (today + timedelta(days=7)).isoformat(),
            "strength": 0.85,
            "interpretation": "A period of expansion and opportunity. Your natural talents are highlighted and recognition may come your way.",
            "action_items": [
                "Take initiative on projects you've been postponing",
                "Network and make new professional connections",
                "Set intentions for long-term growth"
            ]
        },
        {
            "id": str(uuid.uuid4()),
            "transit_type": "Mercury conjunct Venus",
            "planet": "Mercury",
            "aspect": "conjunction",
            "natal_planet": "Venus",
            "start_date": (today + timedelta(days=5)).isoformat(),
            "peak_date": (today + timedelta(days=7)).isoformat(),
            "end_date": (today + timedelta(days=10)).isoformat(),
            "strength": 0.72,
            "interpretation": "Excellent for communication in relationships. Express your feelings and have meaningful conversations.",
            "action_items": [
                "Have important conversations with loved ones",
                "Write heartfelt messages or letters",
                "Negotiate or discuss financial matters"
            ]
        },
        {
            "id": str(uuid.uuid4()),
            "transit_type": "Saturn square Mars",
            "planet": "Saturn",
            "aspect": "square",
            "natal_planet": "Mars",
            "start_date": (today + timedelta(days=14)).isoformat(),
            "peak_date": (today + timedelta(days=21)).isoformat(),
            "end_date": (today + timedelta(days=28)).isoformat(),
            "strength": 0.65,
            "interpretation": "A testing period for your ambitions. Patience and strategic planning are key. Avoid forcing outcomes.",
            "action_items": [
                "Review and refine your action plans",
                "Practice patience with delays",
                "Focus on sustainable progress over quick wins"
            ]
        }
    ]
    
    return transits

# ============== Daily Guidance ==============

@api_router.get("/guidance/daily", response_model=DailyGuidance)
async def get_daily_guidance(user: dict = Depends(get_current_user)):
    """Get personalized daily guidance"""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    sun_sign = user.get("sun_sign", "Unknown")
    
    # Check cache
    cached = await db.daily_guidance.find_one(
        {"user_id": user["id"], "date": today},
        {"_id": 0}
    )
    if cached:
        return DailyGuidance(**cached)
    
    # Generate new guidance (in production, use AI with current transits)
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
                "transit": "Moon in Taurus",
                "influence": "Emotional stability and grounding",
                "advice": "Take time to appreciate simple pleasures"
            },
            {
                "transit": "Mercury trine Jupiter",
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
    """Generate a comprehensive compatibility/synastry analysis"""
    
    # Get user's chart
    user_chart = await db.birth_charts.find_one({"user_id": user["id"]}, {"_id": 0})
    if not user_chart:
        # Generate basic chart if not exists
        user_chart = {
            "sun_sign": user.get("sun_sign", calculate_sun_sign(user.get("birth_date", "1990-01-01"))),
            "moon_sign": "Scorpio",
            "rising_sign": "Leo",
            "planets": {
                "sun": {"sign": user.get("sun_sign", "Aries"), "degree": 15.5, "house": 10},
                "moon": {"sign": "Scorpio", "degree": 22.3, "house": 4},
                "mercury": {"sign": "Taurus", "degree": 8.7, "house": 10},
                "venus": {"sign": "Gemini", "degree": 3.2, "house": 11},
                "mars": {"sign": "Aries", "degree": 28.9, "house": 9},
                "jupiter": {"sign": "Scorpio", "degree": 5.1, "house": 4},
                "saturn": {"sign": "Pisces", "degree": 12.8, "house": 8}
            }
        }
    
    # Calculate partner's sun sign
    partner_sun = calculate_sun_sign(request.partner_birth_date)
    
    # Generate partner chart (simulated - in production use Swiss Ephemeris)
    partner_chart = {
        "sun_sign": partner_sun,
        "moon_sign": "Taurus",
        "rising_sign": "Virgo",
        "planets": {
            "sun": {"sign": partner_sun, "degree": 12.3, "house": 7},
            "moon": {"sign": "Taurus", "degree": 18.5, "house": 2},
            "mercury": {"sign": partner_sun, "degree": 20.1, "house": 7},
            "venus": {"sign": "Libra", "degree": 5.8, "house": 6},
            "mars": {"sign": "Cancer", "degree": 15.2, "house": 4},
            "jupiter": {"sign": "Gemini", "degree": 22.7, "house": 3},
            "saturn": {"sign": "Aquarius", "degree": 8.4, "house": 11}
        }
    }
    
    # Calculate compatibility scores
    element_compat = calculate_element_compatibility(user_chart["sun_sign"], partner_sun)
    modality_compat = calculate_modality_compatibility(user_chart["sun_sign"], partner_sun)
    
    # Calculate synastry aspects
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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
