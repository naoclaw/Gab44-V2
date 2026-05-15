from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
import elevenlabs
from dotenv import load_dotenv
import os
from performance_optimization import track_endpoint_performance

load_dotenv('/root/secrets/all-keys.env')

router = APIRouter(prefix='/premium/voice-horoscope', tags=['Premium'])

class VoiceHoroscopeRequest(BaseModel):
    horoscope_text: str
    voice_id: str = '21m00Tcm4TlvDq8ikWAM'

def get_elevenlabs_client():
    return elevenlabs.ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))

@router.post('/generate')
@track_endpoint_performance
async def generate_voice_horoscope(request_body: VoiceHoroscopeRequest, client: elevenlabs.ElevenLabs = Depends(get_elevenlabs_client), request: Request = None):
    audio = client.generate(
        text=request_body.horoscope_text,
        voice=request_body.voice_id,
        model='eleven_multilingual_v2'
    )
    return {'audio_base64': elevenlabs.to_base64(audio)}