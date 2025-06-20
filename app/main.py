from fastapi import FastAPI, Response
from pydantic import BaseModel
import httpx

app = FastAPI()

VOICEVOX_URL = "http://voicevox:50021"

class SpeakRequest(BaseModel):
    text: str
    speaker: int = 1  # default speaker

@app.post("/speak")
async def speak(request: SpeakRequest):
    async with httpx.AsyncClient() as client:
        # Step 1: audio_query
        query_resp = await client.post(
            f"{VOICEVOX_URL}/audio_query",
            params={"text": request.text, "speaker": request.speaker},
            headers={"accept": "application/json"}
        )
        query_resp.raise_for_status()
        query_data = query_resp.json()

        # Step 2: synthesis
        synth_resp = await client.post(
            f"{VOICEVOX_URL}/synthesis",
            params={"speaker": request.speaker},
            headers={"accept": "audio/wav", "Content-Type": "application/json"},
            json=query_data
        )
        synth_resp.raise_for_status()

        return Response(content=synth_resp.content, media_type="audio/wav")
