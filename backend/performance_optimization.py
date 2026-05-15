from fastapi import APIRouter, Depends, Request
from datetime import datetime
import time
import os
from dotenv import load_dotenv

load_dotenv('/root/secrets/all-keys.env')

router = APIRouter(prefix='/performance', tags=['Optimization'])

# In-memory response time tracking (bypasses MongoDB)
RESPONSE_TIMES = []

def track_endpoint_performance(func):
    async def wrapper(*args, **kwargs):
        from fastapi import Request
        import time
        from datetime import datetime
        request = kwargs.get('request')
        if request:
            start_time = time.time()
            response = await func(*args, **kwargs)
            response_time = time.time() - start_time
            RESPONSE_TIMES.append({
                'path': request.url.path,
                'method': request.method,
                'response_time_ms': round(response_time * 1000),
                'timestamp': datetime.utcnow().isoformat()
            })
            if len(RESPONSE_TIMES) > 1000:
                RESPONSE_TIMES.pop(0)
            return response
        return await func(*args, **kwargs)

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
