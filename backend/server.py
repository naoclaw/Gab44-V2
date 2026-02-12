from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
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
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

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

@api_router.get("/auth/me", response_model=UserProfile)
async def get_me(user: dict = Depends(get_current_user)):
    return UserProfile(**user)

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
