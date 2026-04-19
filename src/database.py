import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", "/data/podcast.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                youtube_url TEXT NOT NULL,
                video_id TEXT NOT NULL UNIQUE,
                title TEXT,
                filename TEXT,
                duration INTEGER,
                filesize INTEGER,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                converted_at TEXT
            )
        """)
        conn.commit()
