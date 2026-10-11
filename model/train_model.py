"""
JobGuard - ML Training Script
Trains a Random Forest + TF-IDF pipeline on the fake_job_postings dataset.
Run once to generate model/model.pkl before starting the Flask server.
"""

import os
import re
import warnings
import pandas as pd
import numpy as np
import joblib
import nltk

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, accuracy_score
)
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings("ignore")

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


# ── Text cleaning ─────────────────────────────────────────────────────────────
def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", " ", text)           # URLs
    text = re.sub(r"<[^>]+>", " ", text)                   # HTML tags
    text = re.sub(r"[^a-z\s]", " ", text)                  # non-alpha
    text = re.sub(r"\s+", " ", text).strip()
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in STOP_WORDS and len(t) > 2]
    return " ".join(tokens)


# ── Feature engineering ───────────────────────────────────────────────────────
def build_features(df: pd.DataFrame) -> pd.Series:
    """Combine text columns into a single string for TF-IDF."""
    text_cols = ["title", "company_profile", "description", "requirements", "benefits"]
    combined = df[text_cols].fillna("").apply(
        lambda row: " ".join(row.values.astype(str)), axis=1
    )
    return combined.apply(clean_text)


# ── Load data ─────────────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "fake_job_postings.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

print("Loading dataset …")
df = pd.read_csv(DATA_PATH)
print(f"  Shape : {df.shape}")
print(f"  Fraudulent distribution:\n{df['fraudulent'].value_counts()}\n")

X_text = build_features(df)
y = df["fraudulent"].astype(int)

# ── Train / test split ────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X_text, y, test_size=0.20, random_state=42, stratify=y
)

print(f"Train size: {len(X_train)}  |  Test size: {len(X_test)}\n")

# ── Build pipeline ────────────────────────────────────────────────────────────
pipeline = Pipeline([
    ("tfidf", TfidfVectorizer(
        max_features=30_000,
        ngram_range=(1, 2),
        sublinear_tf=True,
        min_df=2,
    )),
    ("clf", LogisticRegression(
        C=1.0,
        class_weight="balanced",
        max_iter=1000,
        solver="lbfgs",
        random_state=42,
    )),
])

print("Training Logistic Regression pipeline …")
pipeline.fit(X_train, y_train)

# ── Evaluation ────────────────────────────────────────────────────────────────
y_pred = pipeline.predict(X_test)
y_prob = pipeline.predict_proba(X_test)[:, 1]

acc   = accuracy_score(y_test, y_pred)
auc   = roc_auc_score(y_test, y_prob)

print("=" * 52)
print(f"  Accuracy : {acc:.4f}")
print(f"  ROC-AUC  : {auc:.4f}")
print("=" * 52)
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Real", "Fake"]))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# ── Save ──────────────────────────────────────────────────────────────────────
print(f"\nSaving model -> {MODEL_PATH}")
joblib.dump(pipeline, MODEL_PATH)
print("Done. Model saved successfully.")
