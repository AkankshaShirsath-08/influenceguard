import uuid
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

MODEL_DIR = Path(__file__).resolve().parents[1] / "ml" / "saved_models"
bot_model = joblib.load(MODEL_DIR / "bot_model.pkl")
spam_model = joblib.load(MODEL_DIR / "spam_model.pkl")

ACCOUNT_FEATURES = ["followers", "following", "posts", "has_pic", "bio_len",
                    "username_digits", "account_age_days"]
GENERIC = {"nice pic", "nice", "great post", "wow", "awesome", "cool", "amazing"}


def check_columns(df, needed, label):
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise ValueError(f"{label}: ye columns missing hain: {', '.join(missing)}")


def fake_followers(accounts):
    check_columns(accounts, ACCOUNT_FEATURES, "accounts.csv")
    x = accounts[ACCOUNT_FEATURES].copy()
    x["follow_ratio"] = accounts["followers"] / (accounts["following"] + 1)
    pred = bot_model.predict(x)
    return float(pred.mean() * 100), pred


def comment_reason(text, dup):
    t = text.lower().strip()
    if "http" in t or "www." in t or ".com" in t:
        return "link/promo"
    if not any(ch.isalnum() for ch in t):
        return "emoji-only"
    if t in GENERIC:
        return "generic"
    if dup:
        return "duplicate"
    return "spam pattern"


def spam_comments(comments):
    check_columns(comments, ["user", "text", "timestamp", "post_id"], "comments.csv")
    c = comments.copy()
    c["text"] = c["text"].fillna("").astype(str)
    model_pred = spam_model.predict(c["text"].tolist())
    dup = c.duplicated(subset=["user", "text"], keep=False).tolist()
    rows = []
    for (_, r), m, d in zip(c.iterrows(), model_pred, dup):
        reason = comment_reason(r["text"], d)
        rule_hit = reason in ("link/promo", "emoji-only")
        is_spam = bool(m) or rule_hit
        rows.append({"user": str(r["user"]), "text": r["text"], "is_spam": is_spam,
                     "reason": reason if is_spam else None})
    spam_pct = float(np.mean([r["is_spam"] for r in rows]) * 100) if rows else 0.0
    return spam_pct, rows


def growth_spikes(growth):
    check_columns(growth, ["date", "followers"], "growth.csv")
    g = growth.sort_values("date").reset_index(drop=True)
    diff = g["followers"].diff().fillna(0)
    med = diff.median()
    mad = max((diff - med).abs().median() * 1.4826, 1.0)
    robust_z = (diff - med) / mad
    is_spike = (robust_z > 5) & (diff > 0)
    out = [{"date": str(d), "followers": int(f), "is_spike": bool(s)}
           for d, f, s in zip(g["date"], g["followers"], is_spike)]
    return out, [str(d) for d in g.loc[is_spike, "date"]]


def find_pods(comments, window=60, min_users=15):
    c = comments.copy()
    c["ts"] = pd.to_datetime(c["timestamp"], errors="coerce")
    c = c.dropna(subset=["ts"])
    posts = c["post_id"].nunique()
    pod_posts, windows = 0, []
    for _, grp in c.groupby("post_id"):
        grp = grp.sort_values("ts")
        t = (grp["ts"] - grp["ts"].min()).dt.total_seconds().to_numpy()
        users = grp["user"].astype(str).to_numpy()
        best_n, best_i, j = 0, 0, 0
        for i in range(len(t)):
            while j < len(t) and t[j] - t[i] <= window:
                j += 1
            if j - i > best_n:
                best_n, best_i = j - i, i
        members = sorted(set(users[best_i:best_i + best_n]))
        if len(members) >= min_users:
            pod_posts += 1
            windows.append(members)
    counts = Counter(u for w in windows for u in w)
    need = min(2, len(windows))
    members = sorted(u for u, n in counts.items() if n >= need) if windows else []
    pct = pod_posts / posts * 100 if posts else 0.0
    return pct, pod_posts, members


def build_graph(members, comments, bot_users):
    nodes = [{"id": u, "is_bot": True} for u in members]
    edges = []
    n = len(members)
    for i in range(n):
        for step in (1, 3):
            if n > step:
                edges.append({"source": members[i], "target": members[(i + step) % n]})
    seen = set(members)
    genuine = [u for u in comments["user"].astype(str).unique() if u not in seen and u not in bot_users]
    for u in genuine[:15]:
        nodes.append({"id": u, "is_bot": False})
    return {"nodes": nodes, "edges": edges}


def analyze(accounts, comments, growth, name="uploaded_influencer"):
    fake_pct, pred = fake_followers(accounts)
    bot_users = set(accounts.loc[pred == 1, "username"].astype(str)) if "username" in accounts else set()
    spam_pct, comment_rows = spam_comments(comments)
    growth_rows, spike_dates = growth_spikes(growth)
    pod_pct, pod_posts, pod_members = find_pods(comments)

    # DYNAMIC NUMBERS CALCULATION
    total_followers = int(len(accounts)) 
    fake_follower_count = int((fake_pct / 100) * total_followers)

    spike_pen = min(100.0, len(spike_dates) * 50.0)
    parts = {
        "fake": 0.4 * fake_pct,
        "spam": 0.3 * spam_pct,
        "spike": 0.2 * spike_pen,
        "pod": 0.1 * pod_pct,
    }
    penalty = sum(parts.values())
    score = round(max(0.0, min(100.0, 100 - penalty)))
    risk = "Low" if score >= 70 else "Medium" if score >= 40 else "High"

    labels = {
        "fake": f"Fake follower accounts ({fake_pct:.0f}%)",
        "spam": f"Spam comments ({spam_pct:.0f}%)",
        "spike": "Sudden follower spike on " + ", ".join(spike_dates[:3]) if spike_dates else "",
        "pod": f"Bot pod commenting within seconds ({pod_posts} posts)",
    }
    reasons = [{"feature": labels[k], "impact": round(v / penalty, 2)}
               for k, v in sorted(parts.items(), key=lambda kv: -kv[1]) if v > 0 and penalty > 0][:4]

    spam_rows = [r for r in comment_rows if r["is_spam"]][:100]
    ok_rows = [r for r in comment_rows if not r["is_spam"]][:50]

    return {
        "id": uuid.uuid4().hex[:8],
        "influencer_name": name,
        "authenticity_score": int(score),
        "risk_level": risk,
        "fake_follower_pct": round(fake_pct, 1),
        "spam_comment_pct": round(spam_pct, 1),
        "engagement_anomaly_pct": round(pod_pct, 1),
        "total_followers": total_followers,          # Added
        "fake_follower_count": fake_follower_count,  # Added
        "reasons": reasons,
        "growth": growth_rows,
        "comments": spam_rows + ok_rows,
        "graph": build_graph(pod_members, comments, bot_users),
    }