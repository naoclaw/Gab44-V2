from fastapi import APIRouter, Depends
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv('/root/secrets/all-keys.env')

router = APIRouter(prefix='/mobile', tags=['Responsiveness'])

class MobileContentRequest(BaseModel):
    device_type: str
    content_id: str
    user_id: str | None = None

# In-memory mobile-optimized content (bypasses MongoDB)
MOBILE_CONTENT = {
    'horoscope-today': {
        'desktop': 'Detailed daily horoscope with charts',
        'mobile': 'Condensed daily horoscope with quick takeaways'
    }
}

@router.post('/get-optimized-content')
def get_mobile_optimized_content(request: MobileContentRequest):
    if request.content_id not in MOBILE_CONTENT:
        return {'error': 'Content not found', 'available_content': list(MOBILE_CONTENT.keys())}
    content = MOBILE_CONTENT[request.content_id].get(request.device_type, MOBILE_CONTENT[request.content_id]['desktop'])
    return {
        'content_id': request.content_id,
        'device_type': request.device_type,
        'optimized_content': content,
        'is_mobile_optimized': request.device_type == 'mobile'
    }
