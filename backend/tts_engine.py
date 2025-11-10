import os
import time
from pathlib import Path
from typing import Optional

AUDIO_DIR = Path(__file__).resolve().parent / "static" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

def _gtts_available() -> bool:
    if os.getenv("ENABLE_TTS", "1") == "0":
        return False
    try:
        import gtts  # noqa: F401
        return True
    except Exception:
        return False

def tts_available() -> bool:
    """Return True iff TTS can run (gTTS present and enabled)."""
    return _gtts_available()

def synthesize_to_wav(text: str, voice: Optional[str] = None) -> Optional[str]:
    """
    Generate TTS with gTTS and return a relative URL to the audio file.

    Note: returns an MP3 file (kept function name for API compatibility).
    Example: "/static/audio/story_1712345678901.mp3"
    """
    if os.getenv("ENABLE_TTS", "1") == "0":
        return None
    if not _gtts_available():
        return None

    from gtts import gTTS

    ts = int(time.time() * 1000)
    fname = f"story_{ts}.mp3"
    out_path = AUDIO_DIR / fname

    # gTTS is online; default language English
    gTTS(text=text, lang="en").save(str(out_path))
    return f"/static/audio/{fname}"
