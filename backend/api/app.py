import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Clean, package-based imports (no sys.path hacks)
from backend.story_engine import (
    CATEGORIES_PUBLIC,
    generate_story_api,
    revise_story_api,
)
from backend.tts_engine import (
    tts_available,
    synthesize_to_data_url,  # returns data:audio/mpeg;base64,...
)

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": os.getenv("FRONTEND_ORIGIN", "*")}})

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("api")
if not os.getenv("OPENAI_API_KEY"):
    log.warning("OPENAI_API_KEY is not set; calls to OpenAI will fail.")

@app.get("/api/health")
def health():
    return jsonify({
        "ok": True,
        "tts": tts_available(),
        "python": os.getenv("PYTHON_VERSION", "3.x"),
    })

@app.get("/api/categories")
def list_categories():
    return jsonify({"categories": CATEGORIES_PUBLIC})

@app.post("/api/generate")
def api_generate():
    try:
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
    except Exception as e:
        log.exception("Error in /api/generate")
        return jsonify({"error": str(e)}), 500

@app.post("/api/revise")
def api_revise():
    try:
        data = request.get_json(force=True) or {}
        story = data.get("story")
        feedback = (data.get("feedback") or "").strip()
        if not story:
            return jsonify({"error": "Missing 'story' in request."}), 400

        revised = revise_story_api(story, user_feedback=feedback)
        audio_data_url = synthesize_to_data_url(revised)
        return jsonify({"story": revised, "audioUrl": audio_data_url})
    except Exception as e:
        log.exception("Error in /api/revise")
        return jsonify({"error": str(e)}), 500

# No app.run() — Vercel detects `app` automatically (Flask on Vercel).
