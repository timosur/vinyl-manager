import base64
from fastapi import HTTPException
import requests
import os

def analyze_track_audio(audio_base64):
    # Decode base64 string to bytes
    audio_bytes = base64.b64decode(audio_base64.split(',')[1])
    
    response = requests.post(
        f'{os.environ.get("AUDIO_ANALYZER_URL")}/analyze_audio',
        files={'file': ('audio.webm', audio_bytes, 'audio/webm')}
    )
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error analyzing track audio")
    return response.json()