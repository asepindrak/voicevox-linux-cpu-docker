from fastapi import FastAPI, Query, Response
import httpx

app = FastAPI()

VOICEVOX_URL = "http://voicevox:50021"

@app.get("/speak")
async def speak(text: str = Query(...), speaker: int = Query(1)):
    async with httpx.AsyncClient() as client:
        # Step 1: audio_query
        query_resp = await client.post(
            f"{VOICEVOX_URL}/audio_query",
            params={"text": text, "speaker": speaker},
            headers={"accept": "application/json"}
        )
        query_resp.raise_for_status()
        query_data = query_resp.json()

        # Step 2: synthesis
        synth_resp = await client.post(
            f"{VOICEVOX_URL}/synthesis",
            params={"speaker": speaker},
            headers={"accept": "audio/wav", "Content-Type": "application/json"},
            json=query_data
        )
        synth_resp.raise_for_status()

        return Response(content=synth_resp.content, media_type="audio/wav")
