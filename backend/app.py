import os
from urllib.parse import urljoin
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from story_engine import (
    CATEGORIES_PUBLIC,
    generate_story_api,
    revise_story_api,
)
from tts_engine import synthesize_to_wav, AUDIO_DIR, tts_available

load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="/static")
# Enable CORS for both /api and /static so audio can be fetched cross-origin in prod if needed
CORS(app, resources={
    r"/api/*": {"origins": os.getenv("FRONTEND_ORIGIN", "*")},
    r"/static/*": {"origins": os.getenv("FRONTEND_ORIGIN", "*")},
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

    try:
        story, chosen_category = generate_story_api(
            user_request=prompt if prompt else "Tell me a fun and imaginative story for a child.",
            age_bracket=age_bracket,
            category=category,
        )
        rel_audio_url = synthesize_to_wav(story)  # e.g. "/static/audio/xyz.mp3" or None
        abs_audio_url = urljoin(request.host_url, rel_audio_url.lstrip('/')) if rel_audio_url else None
        return jsonify({"story": story, "category": chosen_category, "audioUrl": abs_audio_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post("/api/revise")
def api_revise():
    data = request.get_json(force=True) or {}
    story = data.get("story")
    feedback = (data.get("feedback") or "").strip()

    if not story:
        return jsonify({"error": "Missing 'story' in request."}), 400
    try:
        revised = revise_story_api(story, user_feedback=feedback)
        rel_audio_url = synthesize_to_wav(revised)
        abs_audio_url = urljoin(request.host_url, rel_audio_url.lstrip('/')) if rel_audio_url else None
        return jsonify({"story": revised, "audioUrl": abs_audio_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serve generated audio files
@app.get("/static/audio/<path:filename>")
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
