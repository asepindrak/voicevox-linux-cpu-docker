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
    speaker: int = 1
    speed: float = 1.0
    pitch: float = 1.0

@app.post("/speak")
async def speak(request: Request, req: SpeakRequest):
    text = req.text[:200]  # batasi panjang maksimal

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

        # Save WAV
        uid = uuid.uuid4().hex
        wav_path = os.path.join(STATIC_DIR, f"{uid}.wav")
        mp3_path = os.path.join(STATIC_DIR, f"{uid}.mp3")

        with open(wav_path, "wb") as f:
            f.write(synth_resp.content)

        # Convert to MP3
        subprocess.run([
            "ffmpeg",
            "-y",
            "-i", wav_path,
            "-codec:a", "libmp3lame",
            "-qscale:a", "2"
        , mp3_path], check=True)

        # Hapus WAV setelah konversi
        os.remove(wav_path)

        # Buat URL
        host = request.headers.get("host")
        scheme = request.url.scheme
        url = f"{scheme}://{host}/static/{uid}.mp3"

        return PlainTextResponse(content=url)
