import sqlite3
import hashlib
from datetime import datetime
from typing import Optional, List, Dict, Any
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Topics Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS topics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_hash TEXT UNIQUE,
        title TEXT NOT NULL,
        source TEXT NOT NULL,
        raw_content TEXT,
        status TEXT DEFAULT 'pending', -- pending, approved, scripted, rejected
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 2. Scripts & Fact-Checking Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scripts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic_id INTEGER,
        title TEXT NOT NULL,
        hook TEXT NOT NULL,
        body TEXT NOT NULL,
        outro TEXT NOT NULL,
        full_narration TEXT NOT NULL,
        fact_check_verdict TEXT, -- VERIFIED, ADJUSTED, REJECTED
        citations TEXT,
        status TEXT DEFAULT 'ready', -- ready, recorded, failed
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (topic_id) REFERENCES topics (id)
    )
    ''')

    # 3. Videos & Upload Status Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        script_id INTEGER,
        video_path TEXT,
        audio_path TEXT,
        duration REAL,
        youtube_id TEXT,
        scheduled_time TIMESTAMP,
        status TEXT DEFAULT 'rendered', -- rendered, uploaded, failed
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (script_id) REFERENCES scripts (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def compute_hash(text: str) -> str:
    cleaned = "".join(text.lower().split())
    return hashlib.sha256(cleaned.encode("utf-8")).hexdigest()

def is_topic_duplicate(title: str) -> bool:
    topic_hash = compute_hash(title)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM topics WHERE topic_hash = ?", (topic_hash,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def save_topic(title: str, source: str, raw_content: str) -> Optional[int]:
    if is_topic_duplicate(title):
        return None
    
    topic_hash = compute_hash(title)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO topics (topic_hash, title, source, raw_content) VALUES (?, ?, ?, ?)",
            (topic_hash, title, source, raw_content)
        )
        conn.commit()
        topic_id = cursor.lastrowid
        return topic_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_next_pending_topic() -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM topics WHERE status = 'pending' ORDER BY id ASC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def mark_topic_status(topic_id: int, status: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE topics SET status = ? WHERE id = ?", (status, topic_id))
    conn.commit()
    conn.close()

def save_script(topic_id: int, title: str, hook: str, body: str, outro: str, full_narration: str, verdict: str, citations: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO scripts (topic_id, title, hook, body, outro, full_narration, fact_check_verdict, citations)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (topic_id, title, hook, body, outro, full_narration, verdict, citations))
    conn.commit()
    script_id = cursor.lastrowid
    conn.close()
    return script_id

def save_video_record(script_id: int, video_path: str, audio_path: str, duration: float) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO videos (script_id, video_path, audio_path, duration)
    VALUES (?, ?, ?, ?)
    ''', (script_id, video_path, audio_path, duration))
    conn.commit()
    video_id = cursor.lastrowid
    conn.close()
    return video_id

if __name__ == "__main__":
    init_db()
    print("History Vault Database Initialized successfully at:", DB_PATH)
