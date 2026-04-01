from flask import Flask, request, jsonify
from flask_cors import CORS
import json, os, urllib.request, urllib.error

app = Flask(__name__)
CORS(app)

KEY = os.environ.get("OPENROUTER_API_KEY", "")

CLASSES = {
    "5th": "Basic arithmetic, fractions",
    "6th": "Ratios, percentages, basic algebra",
    "7th": "Linear equations, integers",
    "8th": "Linear equations, Pythagoras",
    "9th": "Quadratics, coordinate geometry",
    "10th": "Trigonometry, statistics",
    "11th": "Limits, derivatives",
    "12th": "Integration, vectors",
    "Uni": "Calculus, linear algebra",
    "Adv": "Advanced math",
}

MODELS = [
    "google/gemma-3-27b-it:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-3-12b-it:free",
    "qwen/qwen3-next-80b-a3b-instruct:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "google/gemma-3-4b-it:free",
    "meta-llama/llama-3.2-3b-instruct:free",
]

def ask(content):
    if isinstance(content, str):
        messages = [{"role": "user", "content": content}]
    else:
        messages = [{"role": "user", "content": content}]

    for model in MODELS:
        try:
            payload = json.dumps({
                "model": model,
                "messages": messages
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://openrouter.ai/api/v1/chat/completions",
                data=payload,
                headers={
                    "Authorization": "Bearer " + KEY,
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://mathmind.app",
                    "X-Title": "MathMind"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                result = json.loads(r.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            if e.code in [429, 503, 502]:
                continue
            raise e
        except Exception as e:
            continue

    return "All models are busy. Please try again in a moment."

@app.route("/")
def home():
    return jsonify({"status": "MathMind API is running"})

@app.route("/solve", methods=["POST"])
def solve():
    try:
        body = request.get_json()
        problem = body.get("problem", "").strip()
        grade = body.get("grade", "")
        if not problem:
            return jsonify({"error": "No problem"}), 400
        level
