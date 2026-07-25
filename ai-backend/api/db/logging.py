"""
Step 11: basic logging of flagged messages for demo purposes. SQLite is
enough — no production database needed.

Wired into both analyze_message.py and analyze_call.py -- every
classification gets a row here, regardless of category (including
not_scam, so you can see the full traffic picture, not just flagged scams).
init_db() runs once at app startup (api/main.py).
"""

import os
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DB_PATH", "api/db/suraksha.db")


def init_db(db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS flagged_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT,
            category TEXT,
            risk_percent INTEGER,
            language TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def log_flagged_message(text: str, category: str, risk_percent: int, language: str, db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO flagged_messages (text, category, risk_percent, language, created_at) VALUES (?, ?, ?, ?, ?)",
        (text, category, risk_percent, language, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()