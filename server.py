from flask import Flask, request, jsonify
from flask_cors import CORS
import urllib.request
import urllib.error
import json
import os

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

def ask(messages, model="nvidia/nemotron-super-49b-v1:free"):
    payload = json.dumps({"model": model, "messages": messages}).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=payload,
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        result = json.loads(r.read().decode())
    return result["choices"][0]["message"]["content"]

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
        level = "Grade " + grade + ": " + CLASSES.get(grade, "") if grade else "High school"
        prompt = "You are MathMind, a math tutor. " + level + "\nSolve step by step, label each step, highlight FINAL ANSWER.\n\nProblem: " + problem
        answer = ask([{"role": "user", "content": prompt}])
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/solve-image", methods=["POST"])
def solve_image():
    try:
        body = request.get_json()
        image_b64 = body.get("image_b64", "")
        mime_type = body.get("mime_type", "image/jpeg")
        note = body.get("note", "")
        grade = body.get("grade", "")
        if not image_b64:
            return jsonify({"error": "No image"}), 400
        level = "Grade " + grade + ": " + CLASSES.get(grade, "") if grade else "High school"
        prompt = "You are MathMind. " + level + "\nSolve the math in this image step by step. Highlight FINAL ANSWER."
        if note:
            prompt = prompt + "\nNote: " + note
        messages = [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": "data:" + mime_type + ";base64," + image_b64}},
            {"type": "text", "text": prompt}
        ]}]
        answer = ask(messages, model="meta-llama/llama-3.2-11b-vision-instruct:free")
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
