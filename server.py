from flask import Flask, request, jsonify
from flask_cors import CORS
import urllib.request
import urllib.parse
import json
import os

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

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

def call_openrouter(messages, model="deepseek/deepseek-r1:free"):
    data = json.dumps({
        "model": model,
        "messages": messages
    }).encode("utf-8")
    r = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=data,
        headers={
            "Authorization": "Bearer " + API_KEY,
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(r, timeout=60) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result["choices"][0]["message"]["content"]

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "MathMind API is running"})

@app.route("/solve", methods=["POST"])
def solve():
    try:
        data = request.get_json()
        problem = data.get("problem", "").strip()
        grade = data.get("grade", "")
        if not problem:
            return jsonify({"error": "No problem provided"}), 400
        level = "Grade " + grade + ": " + CLASSES.get(grade, "") if grade else "High school"
        prompt = "You are MathMind, a math tutor. " + level + "\nSolve step by step, label each step, highlight FINAL ANSWER.\n\nProblem: " + problem
        answer = call_openrouter([{"role": "user", "content": prompt}])
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/solve-image", methods=["POST"])
def solve_image():
    try:
        data = request.get_json()
        image_b64 = data.get("image_b64", "")
        mime_type = data.get("mime_type", "image/jpeg")
        note = data.get("note", "")
        grade = data.get("grade", "")
        if not image_b64:
            return jsonify({"error": "No image provided"}), 400
        level = "Grade " + grade + ": " + CLASSES.get(grade, "") if grade else "High school"
        prompt = "You are MathMind. " + level + "\nSolve the math problem in this image step by step. Highlight FINAL ANSWER."
        if note:
            prompt = prompt + "\nNote: " + note
        messages = [{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": "data:" + mime_type + ";base64," + image_b64}},
            {"type": "text", "text": prompt}
        ]}]
        answer = call_openrouter(messages, model="meta-llama/llama-3.2-11b-vision-instruct:free")
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
```

Aur `requirements.txt` yeh karo:
```
flask==3.0.3
flask-cors==4.0.1
gunicorn==22.0.0
