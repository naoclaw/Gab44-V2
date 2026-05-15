from fastapi import APIRouter, Depends, Request
from datetime import datetime
import time
import os
from dotenv import load_dotenv

load_dotenv('/root/secrets/all-keys.env')

router = APIRouter(prefix='/performance', tags=['Optimization'])

# In-memory response time tracking (bypasses MongoDB)
RESPONSE_TIMES = []

@router.middleware('http')
async def track_response_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    response_time = time.time() - start_time
    RESPONSE_TIMES.append({
        'path': request.url.path,
        'method': request.method,
        'response_time_ms': round(response_time * 1000),
        'timestamp': datetime.utcnow().isoformat()
    })
    # Keep only last 1000 entries to prevent memory bloat
    if len(RESPONSE_TIMES) > 1000:
        RESPONSE_TIMES.pop(0)
    return response

@router.get('/response-time-stats')
def get_response_time_stats(path: str | None = None):
    filtered_times = RESPONSE_TIMES
    if path:
        filtered_times = [t for t in RESPONSE_TIMES if t['path'] == path]
    if not filtered_times:
        return {'error': 'No response time data available'}
    return {
        'total_requests': len(filtered_times),
        'average_response_time_ms': round(sum(t['response_time_ms'] for t in filtered_times) / len(filtered_times)),
        'min_response_time_ms': min(t['response_time_ms'] for t in filtered_times),
        'max_response_time_ms': max(t['response_time_ms'] for t in filtered_times),
        'recent_requests': filtered_times[-10:]
    }
