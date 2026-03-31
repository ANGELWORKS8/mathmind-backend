"""
MathMind Backend — Flask API Server (Gemini)
Free API — no credits needed!
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import base64
import os

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get("GEMINI_API_KEY", "")

CLASSES = {
    "5th":  "Basic arithmetic, fractions, decimals, simple geometry",
    "6th":  "Ratios, percentages, basic algebra, area & perimeter",
    "7th":  "Linear equations, integers, ratio & proportion",
    "8th":  "Linear equations, systems, Pythagoras, factoring",
    "9th":  "Quadratics, coordinate geometry, trig basics",
    "10th": "Quadratics, trigonometry, circles, statistics",
    "11th": "Functions, limits, derivatives, probability",
    "12th": "Integration, differential equations, vectors",
    "Uni":  "Calculus, linear algebra, differential equations",
    "Adv":  "Advanced — full rigor, no simplification",
}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "MathMind API is running ✓"})

@app.route("/solve", methods=["POST"])
def solve():
    try:
        data = request.get_json()
        problem = data.get("problem", "").strip()
        grade   = data.get("grade", "")

        if not problem:
            return jsonify({"error": "No problem provided"}), 400

        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")

        level_str = f"The student is in Grade {grade}. Topics: {CLASSES.get(grade, '')}." if grade else "General high school level."

        prompt = f"""You are MathMind, a world-class math tutor.
{level_str}

Solve the following problem with complete step-by-step working:
- Start by identifying the problem type
- Label each step clearly (Step 1, Step 2 ...)
- Explain briefly WHY each step is done
- Use proper notation: ^ for powers, sqrt() for roots
- Clearly highlight the FINAL ANSWER at the end
- Keep language clear for Grade {grade} level

Problem: {problem}"""

        response = model.generate_content(prompt)
        return jsonify({"answer": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/solve-image", methods=["POST"])
def solve_image():
    try:
        data      = request.get_json()
        image_b64 = data.get("image_b64", "")
        mime_type = data.get("mime_type", "image/jpeg")
        note      = data.get("note", "")
        grade     = data.get("grade", "")

        if not image_b64:
            return jsonify({"error": "No image provided"}), 400

        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        level_str = f"Student is in Grade {grade}. Topics: {CLASSES.get(grade, '')}." if grade else "General high school level."

        prompt = f"""You are MathMind, an expert math tutor.
{level_str}

Examine this image carefully. Extract the complete math problem, then solve it step-by-step with clearly labeled steps. Identify the problem type first. Highlight the FINAL ANSWER clearly.
{f'Student note: {note}' if note else ''}"""

        image_data = base64.b64decode(image_b64)
        image_part = {"mime_type": mime_type, "data": image_data}

        response = model.generate_content([prompt, image_part])
        return jsonify({"answer": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
