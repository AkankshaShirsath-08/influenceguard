import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "train"
OUT = Path(__file__).resolve().parent / "saved_models"
OUT.mkdir(exist_ok=True)

FEATURES = ["followers", "following", "posts", "has_pic", "bio_len",
            "username_digits", "account_age_days"]


def add_ratio(df):
    x = df[FEATURES].copy()
    x["follow_ratio"] = df["followers"] / (df["following"] + 1)
    return x


def scores(y_true, y_pred):
    return {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred), 4),
        "recall": round(recall_score(y_true, y_pred), 4),
        "f1": round(f1_score(y_true, y_pred), 4),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }


# ---------- Model 1: Fake account detector ----------
acc = pd.read_csv(DATA / "accounts_train.csv")
X = add_ratio(acc)
y = acc["is_bot"]
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

bot_model = RandomForestClassifier(n_estimators=200, random_state=42)
bot_model.fit(X_tr, y_tr)
bot_metrics = scores(y_te, bot_model.predict(X_te))
joblib.dump(bot_model, OUT / "bot_model.pkl")
print("Fake account model:", bot_metrics)

# ---------- Model 2: Comment spam detector ----------
com = pd.read_csv(DATA / "comments_train.csv")
Xc_tr, Xc_te, yc_tr, yc_te = train_test_split(
    com["text"], com["is_spam"], test_size=0.2, random_state=42, stratify=com["is_spam"])

spam_model = make_pipeline(
    TfidfVectorizer(ngram_range=(1, 2), lowercase=True),
    LogisticRegression(max_iter=500),
)
spam_model.fit(Xc_tr, yc_tr)
spam_metrics = scores(yc_te, spam_model.predict(Xc_te))
joblib.dump(spam_model, OUT / "spam_model.pkl")
print("Spam model:", spam_metrics)

# ---------- Metrics file (for /api/metrics) ----------
importance = dict(zip(X.columns, [round(float(v), 4) for v in bot_model.feature_importances_]))
with open(OUT / "metrics.json", "w", encoding="utf-8") as f:
    json.dump({"bot_model": bot_metrics, "spam_model": spam_metrics,
               "bot_feature_importance": importance}, f, indent=2)
print("Feature importance:", importance)
print("Saved models + metrics.json in", OUT)