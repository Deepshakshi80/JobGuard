# JobGuard — Fake Job Posting Detector

> Detect fraudulent job postings using Machine Learning and NLP.

---

## Overview

JobGuard is a full-stack web application that analyses job descriptions and predicts whether they are **real or fake** using a trained Machine Learning model. It is built with Python (Flask) on the backend and vanilla HTML/CSS/JavaScript on the frontend.

The model was trained on the **EMSI Fake Job Postings** dataset containing 17,880 job postings (866 fake, 17,014 real).

---

## Live Demo

> Deploy on Render and paste your URL here:
> **https://jobguard.onrender.com**

## GitHub Repository

🔗 **https://github.com/Deepshakshi80/JobGuard**

---

## Features

- Paste any job description and get an instant Real / Fake prediction
- Probability bars showing confidence (Real % vs Fake %)
- Risk level indicator: Very Low / Low / Moderate / High Risk
- Suspicious keyword detection (e.g. "work from home", "no experience", "WhatsApp")
- Try Example buttons for both a real and a fake posting
- Model performance stats (Accuracy, ROC-AUC, dataset size)
- Fully responsive UI matching a professional design

---

## Model Performance

| Metric | Score |
|--------|-------|
| Accuracy | **98.27%** |
| ROC-AUC | **98.83%** |
| Fake Recall | **91%** |
| Algorithm | Logistic Regression + TF-IDF (1+2-grams) |
| Training samples | 17,880 job postings |
| Fake samples | 866 |
| Real samples | 17,014 |

---

## Project Structure

```
jobguard/
├── app.py                  # Flask backend — API routes + model inference
├── Procfile                # Gunicorn start command for Render/Heroku
├── render.yaml             # Render deployment config
├── requirements.txt        # Python dependencies
├── run.bat                 # One-click local startup (Windows)
├── model/
│   ├── train_model.py      # ML training script (run once)
│   └── model.pkl           # Trained pipeline (TF-IDF + Logistic Regression)
├── static/
│   ├── style.css           # All UI styles
│   └── app.js              # Frontend logic, API calls, result rendering
└── templates/
    └── index.html          # Main HTML page
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, Flask 3, Flask-CORS |
| ML | scikit-learn (Logistic Regression, TF-IDF) |
| NLP | NLTK (stopwords, lemmatization) |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Server | Gunicorn (production), Flask dev server (local) |
| Dataset | EMSI Fake Job Postings (`fake_job_postings.csv`) |

---

## Getting Started (Local)

### Prerequisites

- Python 3.10 or higher
- pip

### 1. Clone the repository

```bash
git clone https://github.com/Deepshakshi80/JobGuard.git
cd JobGuard
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Train the model (first time only)

> Skip this step if `model/model.pkl` already exists.

Place `fake_job_postings.csv` in the root of `job_detect/` (one level above `jobguard/`), then run:

```bash
python model/train_model.py
```

This generates `model/model.pkl`.

### 4. Start the server

**Windows (double-click or run in terminal):**
```bat
.\run.bat
```

**Or directly:**
```bash
python app.py
```

### 5. Open in browser

```
http://127.0.0.1:5000
```

---

## API Endpoints

### `POST /api/predict`

Analyse a job description text.

**Request body:**
```json
{
  "text": "We are hiring a Python developer with 2+ years of experience..."
}
```

**Response:**
```json
{
  "label": "REAL",
  "real_prob": 86.1,
  "fake_prob": 13.9,
  "risk_level": "Very Low Risk",
  "flags": []
}
```

---

### `GET /api/stats`

Returns model training statistics.

**Response:**
```json
{
  "accuracy": 98.27,
  "roc_auc": 98.83,
  "total_jobs": 17880,
  "fake_jobs": 866,
  "real_jobs": 17014,
  "model": "Logistic Regression + TF-IDF"
}
```

---

## Deployment (Render — Free)

1. Push this repository to GitHub
2. Go to [render.com](https://render.com) → **New → Web Service**
3. Connect your GitHub repo
4. Use these settings:

| Field | Value |
|-------|-------|
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt && python -c "import nltk; nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt')"` |
| Start Command | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
| Plan | Free |

5. Click **Create Web Service** — your app will be live in ~5 minutes.

---

## Dataset

- **Name:** EMSI Fake Job Postings
- **Source:** [Kaggle — Real or Fake Job Postings](https://www.kaggle.com/datasets/shivamb/real-or-fake-fake-jobposting-prediction)
- **Size:** 17,880 rows × 18 columns
- **Target column:** `fraudulent` (0 = Real, 1 = Fake)

---

## How It Works

1. The text input (title + company profile + description + requirements + benefits) is combined into one string
2. It is cleaned: lowercased, HTML/URLs stripped, non-alpha removed, stop words removed, lemmatized
3. The cleaned text is passed through a trained **TF-IDF vectorizer** (30,000 features, 1+2-grams)
4. A **Logistic Regression** classifier (class_weight=balanced) outputs a probability
5. If fake probability ≥ 50%, the posting is flagged as **FAKE**
6. Known suspicious keywords are also scanned and highlighted

---

## License

MIT License — free to use, modify, and distribute.
