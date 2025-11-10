from flask import Flask, request, jsonify
from flask_cors import CORS
from story_engine import (
    CATEGORIES_PUBLIC,
    generate_story_api,
    revise_story_api,
)

app = Flask(__name__)
CORS(app)  # enable CORS for all routes (safe for dev)


@app.get("/api/categories")
def list_categories():
    return jsonify({
        "categories": CATEGORIES_PUBLIC
    })


@app.post("/api/generate")
def api_generate():
    data = request.get_json(force=True) or {}
    age_bracket = (data.get("ageBracket") or "middle").strip().lower()  # 'young'|'middle'|'older'
    prompt = (data.get("prompt") or "").strip()
    category = (data.get("category") or None)

    try:
        story, chosen_category = generate_story_api(
            user_request=prompt if prompt else "Tell me a fun and imaginative story for a child.",
            age_bracket=age_bracket,
            category=category,
        )
        return jsonify({"story": story, "category": chosen_category})
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
        return jsonify({"story": revised})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)