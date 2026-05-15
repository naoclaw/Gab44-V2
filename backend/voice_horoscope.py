from fastapi import APIRouter, Depends
import elevenlabs
from dotenv import load_dotenv
import os

load_dotenv('/root/secrets/all-keys.env')

router = APIRouter(prefix='/premium/voice-horoscope', tags=['Premium'])

def get_elevenlabs_client():
    return elevenlabs.ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))

@router.post('/generate')
def generate_voice_horoscope(horoscope_text: str, voice_id: str = '21m00Tcm4TlvDq8ikWAM', client: elevenlabs.ElevenLabs = Depends(get_elevenlabs_client)):
    audio = client.generate(
        text=horoscope_text,
        voice=voice_id,
        model='eleven_multilingual_v2'
    )
    return {'audio_base64': elevenlabs.to_base64(audio)}