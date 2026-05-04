from __future__ import annotations

from pathlib import Path

from groq import AsyncGroq, Groq

from CLI_convo.config import api_key

CHAT_MODEL = "llama-3.3-70b-versatile"
WHISPER_MODEL = "whisper-large-v3-turbo"


def _require_api_key() -> str:
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set.")
    return api_key


def complete(system: str, user: str) -> str:
    client = Groq(api_key=_require_api_key())
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return response.choices[0].message.content or ""


async def transcribe(path: str) -> str:
    client = AsyncGroq(api_key=_require_api_key())
    audio_path = Path(path)
    with audio_path.open("rb") as audio_file:
        transcription = await client.audio.transcriptions.create(
            file=(str(audio_path), audio_file.read()),
            model=WHISPER_MODEL,
        )
    return transcription.text
