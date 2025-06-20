from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import httpx
import uuid
import os
import subprocess

VOICEVOX_URL = "http://voicevox:50021"
STATIC_DIR = "static"
os.makedirs(STATIC_DIR, exist_ok=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class SpeakRequest(BaseModel):
    text: str
    speaker: int = 14
    speed: float = 1.0
    pitch: float = 1.0

@app.post("/speak")
async def speak(request: Request, req: SpeakRequest):
    text = req.text[:200]

    async with httpx.AsyncClient() as client:
        # Step 1: audio_query
        query_resp = await client.post(
            f"{VOICEVOX_URL}/audio_query",
            params={"text": text, "speaker": req.speaker},
            headers={"accept": "application/json"}
        )
        query_resp.raise_for_status()
        query_data = query_resp.json()
        query_data["speedScale"] = req.speed
        query_data["pitchScale"] = req.pitch

        # Step 2: synthesis
        synth_resp = await client.post(
            f"{VOICEVOX_URL}/synthesis",
            params={"speaker": req.speaker},
            headers={"accept": "audio/wav", "Content-Type": "application/json"},
            json=query_data
        )
        synth_resp.raise_for_status()

        # Save WAV & Convert
        uid = uuid.uuid4().hex
        wav_path = os.path.join(STATIC_DIR, f"{uid}.wav")
        mp4_path = os.path.join(STATIC_DIR, f"{uid}.mp4")
        with open(wav_path, "wb") as f:
            f.write(synth_resp.content)

        subprocess.run([
            "ffmpeg",
            "-y",
            "-i", wav_path,
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            mp4_path
        ], check=True)

        os.remove(wav_path)

        # Get full URL
        host = request.headers.get("host")
        scheme = request.url.scheme
        full_url = f"{scheme}://{host}/static/{uid}.mp4"

        return PlainTextResponse(content=full_url)
