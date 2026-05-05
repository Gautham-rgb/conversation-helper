from __future__ import annotations
from pathlib import Path
from groq import AsyncGroq, Groq
from CLI_convo.config import api_key

CHAT_MODEL    = "llama-3.3-70b-versatile"
WHISPER_MODEL = "whisper-large-v3-turbo"

def _require_api_key() -> str:
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set.")
    return api_key

# Module-level singletons — created once, reused every call
_sync_client:  Groq      | None = None
_async_client: AsyncGroq | None = None

def _get_sync() -> Groq:
    global _sync_client
    if _sync_client is None:
        _sync_client = Groq(api_key=_require_api_key())
    return _sync_client

def _get_async() -> AsyncGroq:
    global _async_client
    if _async_client is None:
        _async_client = AsyncGroq(api_key=_require_api_key())
    return _async_client


def complete(system: str, user: str) -> str:
    response = _get_sync().chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    )
    return response.choices[0].message.content or ""


async def transcribe(path: str) -> str:
    audio_path = Path(path)
    with audio_path.open("rb") as audio_file:
        transcription = await _get_async().audio.transcriptions.create(
            file=(str(audio_path), audio_file.read()),
            model=WHISPER_MODEL,
        )
    return transcription.text