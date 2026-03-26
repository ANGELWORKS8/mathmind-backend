"""
╔══════════════════════════════════════════════════════╗
║         MathMind Backend — Flask API Server          ║
║  Deploy on Railway.app (free)                        ║
╚══════════════════════════════════════════════════════╝

Install: pip install flask flask-cors anthropic
Run locally: python server.py
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic
import base64
import os

app = Flask(__name__)
CORS(app)  # Allow requests from Flutter app

# ── API Key (set in Railway environment variables — NEVER hardcode!) ────────
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ── Class info ──────────────────────────────────────────────────────────────
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

# ── Health check ────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "MathMind API is running ✓"})

# ── Solve text equation ─────────────────────────────────────────────────────
@app.route("/solve", methods=["POST"])
def solve():
    try:
        data = request.get_json()
        problem  = data.get("problem", "").strip()
        grade    = data.get("grade", "")

        if not problem:
            return jsonify({"error": "No problem provided"}), 400

        if not API_KEY:
            return jsonify({"error": "API key not configured on server"}), 500

        # Build prompt
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

        client = anthropic.Anthropic(api_key=API_KEY)
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        answer = response.content[0].text
        return jsonify({"answer": answer})

    except anthropic.AuthenticationError:
        return jsonify({"error": "Invalid API key on server"}), 401
    except anthropic.RateLimitError:
        return jsonify({"error": "Rate limit reached. Try again shortly."}), 429
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Solve image equation ────────────────────────────────────────────────────
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

        if not API_KEY:
            return jsonify({"error": "API key not configured on server"}), 500

        level_str = f"Student is in Grade {grade}. Topics: {CLASSES.get(grade, '')}." if grade else "General high school level."

        prompt_text = (
            f"You are MathMind, an expert math tutor.\n{level_str}\n\n"
            "Examine this image carefully. Extract the complete math problem, "
            "then solve it step-by-step with clearly labeled steps. "
            "Identify the problem type first. Highlight the FINAL ANSWER clearly.\n"
            + (f"Student note: {note}" if note else "")
        )

        client = anthropic.Anthropic(api_key=API_KEY)
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": image_b64,
                        }
                    },
                    {"type": "text", "text": prompt_text}
                ]
            }]
        )

        answer = response.content[0].text
        return jsonify({"answer": answer})

    except anthropic.AuthenticationError:
        return jsonify({"error": "Invalid API key on server"}), 401
    except anthropic.RateLimitError:
        return jsonify({"error": "Rate limit reached. Try again shortly."}), 429
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Run ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
