"""Flask web UI + JSON API for Prompt Shield AI.   Run: python app.py  ->  http://127.0.0.1:5000"""
from flask import Flask, jsonify, request, send_from_directory
from prompt_shield import PromptShield
from prompt_shield.config import T1, T2

app = Flask(__name__, static_folder="static")
shield = PromptShield()


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.post("/api/analyze")
def analyze():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "Please provide a prompt."}), 400
    if len(prompt) > 5000:
        return jsonify({"error": "Prompt too long (max 5000 characters)."}), 400
    return jsonify(shield.analyze(prompt, user_id=data.get("user_id", "web")))


@app.get("/api/logs")
def logs():
    return jsonify(shield.db.recent(15))


@app.get("/api/stats")
def stats():
    return jsonify(shield.db.stats())


@app.get("/api/config")
def config():
    return jsonify({"t1": T1, "t2": T2})


if __name__ == "__main__":
    app.run(debug=False)
