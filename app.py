"""
JobGuard - Flask Backend
Run: python app.py
"""

import os
import re
import joblib
import nltk
import numpy as np
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

# ── NLTK resources ────────────────────────────────────────────────────────────
for resource in ["punkt", "stopwords", "wordnet"]:
    try:
        nltk.data.find(f"tokenizers/{resource}")
    except LookupError:
        nltk.download(resource, quiet=True)

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

STOP_WORDS = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

# ── Load model ────────────────────────────────────────────────────────────────
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "model.pkl")
pipeline = joblib.load(MODEL_PATH)


def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in STOP_WORDS and len(t) > 2]
    return " ".join(tokens)


# ── Flask app ─────────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)
    job_text = data.get("text", "").strip()

    if not job_text:
        return jsonify({"error": "No text provided"}), 400

    cleaned = clean_text(job_text)
    if not cleaned:
        return jsonify({"error": "Text too short or invalid"}), 400

    prob      = pipeline.predict_proba([cleaned])[0]
    fake_prob = float(prob[1])
    real_prob = float(prob[0])
    label     = "FAKE" if fake_prob >= 0.5 else "REAL"

    # risk level
    if fake_prob >= 0.75:
        risk = "High Risk"
    elif fake_prob >= 0.50:
        risk = "Moderate Risk"
    elif fake_prob >= 0.25:
        risk = "Low Risk"
    else:
        risk = "Very Low Risk"

    # red-flag keywords
    FRAUD_KEYWORDS = [
        "work from home", "no experience", "immediate joining", "whatsapp",
        "earn money fast", "high salary", "part time", "wire transfer",
        "send money", "guaranteed income", "no interview", "direct hire",
        "instant approval", "limited seats", "apply now", "earn daily",
    ]
    text_lower = job_text.lower()
    flags      = [kw for kw in FRAUD_KEYWORDS if kw in text_lower]

    return jsonify({
        "label":      label,
        "fake_prob":  round(fake_prob * 100, 1),
        "real_prob":  round(real_prob * 100, 1),
        "risk_level": risk,
        "flags":      flags,
    })


@app.route("/api/stats", methods=["GET"])
def stats():
    """Return static training stats to display on UI."""
    return jsonify({
        "accuracy":    98.27,
        "roc_auc":     98.83,
        "total_jobs":  17880,
        "fake_jobs":   866,
        "real_jobs":   17014,
        "model":       "Logistic Regression + TF-IDF",
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"JobGuard server starting on http://0.0.0.0:{port}")
    app.run(debug=False, host="0.0.0.0", port=port, use_reloader=False)
