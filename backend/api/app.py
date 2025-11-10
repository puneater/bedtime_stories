import os
import sys
import pathlib
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Make /backend importable after moving this file under /api
ROOT = pathlib.Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
sys.path.append(str(ROOT))
sys.path.append(str(BACKEND_DIR))

from story_engine import (  # noqa: E402
    CATEGORIES_PUBLIC,
    generate_story_api,
    revise_story_api,
)
from tts_engine import (    # noqa: E402
    tts_available,
    synthesize_to_data_url,  # returns data:audio/mpeg;base64,...
)

load_dotenv()

app = Flask(__name__)
# If frontend runs on a different origin in dev, keep CORS open or pin FRONTEND_ORIGIN
CORS(app, resources={
    r"/api/*": {"origins": os.getenv("FRONTEND_ORIGIN", "*")}
})

@app.get("/api/health")
def health():
    return jsonify({"ok": True, "tts": tts_available()})

@app.get("/api/categories")
def list_categories():
    return jsonify({"categories": CATEGORIES_PUBLIC})

@app.post("/api/generate")
def api_generate():
    data = request.get_json(force=True) or {}
    age_bracket = (data.get("ageBracket") or "middle").strip().lower()
    prompt = (data.get("prompt") or "").strip()
    category = (data.get("category") or None)

    story, chosen_category = generate_story_api(
        user_request=prompt if prompt else "Tell me a fun and imaginative story for a child.",
        age_bracket=age_bracket,
        category=category,
    )
    audio_data_url = synthesize_to_data_url(story)  # data:audio/mpeg;base64,...
    return jsonify({"story": story, "category": chosen_category, "audioUrl": audio_data_url})

@app.post("/api/revise")
def api_revise():
    data = request.get_json(force=True) or {}
    story = data.get("story")
    feedback = (data.get("feedback") or "").strip()
    if not story:
        return jsonify({"error": "Missing 'story' in request."}), 400

    revised = revise_story_api(story, user_feedback=feedback)
    audio_data_url = synthesize_to_data_url(revised)
    return jsonify({"story": revised, "audioUrl": audio_data_url})

# --- Vercel handler (serverless entrypoint) ---
# pip install vercel-python-wsgi
import vercel_wsgi  # noqa: E402

def handler(event, context):
    """Vercel Serverless Function entrypoint."""
    return vercel_wsgi.handle(app, event, context)

# Do NOT call app.run() on Vercel
