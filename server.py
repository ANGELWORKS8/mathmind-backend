from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64
import os

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL   = "meta-llama/llama-3.3-8b-instruct:free"

CLASSES = {
    "5th":  "Basic arithmetic, fractions, decimals",
    "6th":  "Ratios, percentages, basic algebra",
    "7th":  "Linear equations, integers",
    "8th":  "Linear equations, Pythagoras",
    "9th":  "Quadratics, coordinate geometry",
    "10th": "Trigonometry, circles, statistics",
    "11th": "Limits, derivatives, probability",
    "12th": "Integration, vectors",
    "Uni":  "Calculus, linear algebra",
    "Adv":  "Advanced — full rigor",
}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "MathMind API is running ✓"})

@app.route("/solve", methods=["POST"])
def solve():
    try:
        data    = request.get_json()
        problem = data.get("problem", "").strip()
        grade   = data.get("grade", "")
        if not problem:
            return jsonify({"error": "No problem provided"}), 400
        level = f"Grade {grade}: {CLASSES.get(grade,'')}" if grade else "High school level"
        prompt = f"""You are MathMind, a math tutor. {level}
Solve step by step:
- Label steps clearly
- Show working
- Highlight FINAL ANSWER

Problem: {problem}"""
        res = requests.post(API_URL, headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }, json={"model": MODEL, "messages": [{"role":"user","content":prompt}]})
        data = res.json()
        answer = data["choices"][0]["message"]["content"]
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/solve-image", methods=["POST"])
def solve_image():
    try:
        data      = request.get_json()
        image_b64 = data.get("image_b64","")
        mime_type = data.get("mime_type","image/jpeg")
        note      = data.get("note","")
        grade     = data.get("grade","")
        if not image_b64:
            return jsonify({"error": "No image provided"}), 400
        level = f"Grade {grade}: {CLASSES.get(grade,'')}" if grade else "High school level"
        prompt = f"You are MathMind. {level}\nSolve the math problem in this image step by step. Highlight FINAL ANSWER.\n{f'Note: {note}' if note else ''}"
        res = requests.post(API_URL, headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }, json={"model": "meta-llama/llama-3.2-11b-vision-instruct:free",
                 "messages": [{"role":"user","content":[
                     {"type":"image_url","image_url":{"url":f"data:{mime_type};base64,{image_b64}"}},
                     {"type":"text","text":prompt}
                 ]}]})
        data = res.json()
        answer = data["choices"][0]["message"]["content"]
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
```

