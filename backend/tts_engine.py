import os
import base64
from io import BytesIO
from typing import Optional

def tts_available() -> bool:
    if os.getenv("ENABLE_TTS", "1") == "0":
        return False
    try:
        import gtts  # noqa: F401
        return True
    except Exception:
        return False

def _synthesize_mp3_bytes(text: str) -> bytes:
    """Use gTTS to synthesize speech to bytes (MP3)."""
    from gtts import gTTS
    buf = BytesIO()
    gTTS(text=text, lang="en").write_to_fp(buf)
    return buf.getvalue()

def synthesize_to_data_url(text: str, voice: Optional[str] = None) -> Optional[str]:
    """
    Return a data URL (data:audio/mpeg;base64,...) for the synthesized audio.
    Serverless-safe: no filesystem writes, works on Vercel.
    """
    if os.getenv("ENABLE_TTS", "1") == "0":
        return None
    if not tts_available():
        return None
    audio_bytes = _synthesize_mp3_bytes(text)
    b64 = base64.b64encode(audio_bytes).decode("ascii")
    return f"data:audio/mpeg;base64,{b64}"
