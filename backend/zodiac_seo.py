from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from performance_optimization import track_endpoint_performance

load_dotenv('/root/secrets/all-keys.env')

router = APIRouter(prefix='/zodiac', tags=['SEO'])

class ZodiacLandingPage(BaseModel):
    sign: str
    daily_content: str
    meta_title: str
    meta_description: str
    seo_keywords: list[str]

# In-memory storage (bypasses MongoDB for initial implementation)
ZODIAC_CONTENT = {
    'aries': {'meta_title': 'Aries Daily Horoscope | Gab44 Astrology Coaching', 'meta_description': 'Get your personalized Aries daily horoscope and astrology coaching from Gab44.'}
}

@router.get('/{sign}/landing-page')
@track_endpoint_performance
async def get_zodiac_landing_page(sign: str, request: Request):
    if sign not in ZODIAC_CONTENT:
        return {'error': 'Zodiac sign not found', 'suggested_signs': list(ZODIAC_CONTENT.keys())}
    return ZODIAC_CONTENT[sign]

@router.post('/{sign}/update-content')
def update_zodiac_landing_page(sign: str, page_data: ZodiacLandingPage):
    ZODIAC_CONTENT[sign] = page_data.dict()
    return {'success': True, 'updated_sign': sign}
