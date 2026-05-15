from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv('/root/secrets/all-keys.env')

router = APIRouter(prefix='/conversion', tags=['Optimization'])

class CtaClick(BaseModel):
    cta_id: str
    page_url: str
    user_id: str | None = None
    device_type: str | None = None

# In-memory storage for CTA click data (bypasses MongoDB)
CTA_CLICK_DATA = []

@router.post('/track-cta-click')
def track_cta_click(click_data: CtaClick):
    tracked_click = {**click_data.dict(), 'timestamp': datetime.utcnow().isoformat()}
    CTA_CLICK_DATA.append(tracked_click)
    return {'success': True, 'tracked_click_id': len(CTA_CLICK_DATA) - 1}

@router.get('/cta-click-stats')
def get_cta_click_stats(cta_id: str | None = None):
    filtered_clicks = CTA_CLICK_DATA
    if cta_id:
        filtered_clicks = [c for c in CTA_CLICK_DATA if c['cta_id'] == cta_id]
    return {
        'total_clicks': len(filtered_clicks),
        'unique_pages': len(set(c['page_url'] for c in filtered_clicks)),
        'recent_clicks': filtered_clicks[-5:] if filtered_clicks else []
    }
