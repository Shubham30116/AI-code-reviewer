import sqlite3
import json
from datetime import datetime

DB_PATH = "review_history.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT,
            language TEXT,
            code_snippet TEXT,
            overall_score INTEGER,
            summary TEXT,
            review_json TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_review(language: str, code: str, review: dict):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO reviews (created_at, language, code_snippet, overall_score, summary, review_json) VALUES (?,?,?,?,?,?)",
        (
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            language,
            code[:300],
            review.get("overall_score", 0),
            review.get("summary", ""),
            json.dumps(review)
        )
    )
    conn.commit()
    conn.close()

def load_history(limit: int = 20) -> list:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, created_at, language, code_snippet, overall_score, summary FROM reviews ORDER BY id DESC LIMIT ?",
        (limit,)
    ).fetchall()
    conn.close()
    return [{"id": r[0], "created_at": r[1], "language": r[2],
             "code_snippet": r[3], "overall_score": r[4], "summary": r[5]} for r in rows]

def load_review_by_id(review_id: int) -> dict:
    init_db()
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT review_json FROM reviews WHERE id=?", (review_id,)).fetchone()
    conn.close()
    return json.loads(row[0]) if row else {}

def delete_review(review_id: int):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM reviews WHERE id=?", (review_id,))
    conn.commit()
    conn.close()
