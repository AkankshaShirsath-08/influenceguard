import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "influenceguard.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            influencer_name TEXT,
            score INTEGER,
            risk_level TEXT,
            fake_follower_pct REAL,
            spam_comment_pct REAL,
            total_followers INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_analysis(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO analysis_history 
        (influencer_name, score, risk_level, fake_follower_pct, spam_comment_pct, total_followers)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data.get("influencer_name", "unknown"),
        data["authenticity_score"],
        data["risk_level"],
        data["fake_follower_pct"],
        data["spam_comment_pct"],
        data.get("total_followers", 0)
    ))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM analysis_history ORDER BY created_at DESC LIMIT 20')
    rows = cursor.fetchall()
    conn.close()
    return rows

init_db()