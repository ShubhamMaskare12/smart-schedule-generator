"""
StudyPilot — Database Layer
SQLite + lightweight ORM via raw SQL (no heavy deps)
"""

import sqlite3
import hashlib
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(__file__), "studypilot.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create all tables if they don't exist."""
    conn = get_conn()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT UNIQUE NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            created_at  TEXT DEFAULT (datetime('now')),
            last_login  TEXT
        );

        CREATE TABLE IF NOT EXISTS timetables (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            name        TEXT NOT NULL,
            config_json TEXT NOT NULL,
            grid_json   TEXT,
            weeks       INTEGER DEFAULT 1,
            created_at  TEXT DEFAULT (datetime('now')),
            updated_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS sessions (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL REFERENCES users(id),
            timetable_id  INTEGER REFERENCES timetables(id),
            date          TEXT NOT NULL,
            subject       TEXT NOT NULL,
            duration_min  INTEGER DEFAULT 60,
            completed     INTEGER DEFAULT 0,
            notes         TEXT,
            created_at    TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS streaks (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL REFERENCES users(id) UNIQUE,
            current    INTEGER DEFAULT 0,
            best       INTEGER DEFAULT 0,
            last_date  TEXT
        );

        CREATE TABLE IF NOT EXISTS preferences (
            user_id     INTEGER PRIMARY KEY REFERENCES users(id),
            theme       TEXT DEFAULT 'dark',
            color_accent TEXT DEFAULT '#6C63FF',
            time_format TEXT DEFAULT '24h',
            pref_json   TEXT DEFAULT '{}'
        );
    """)
    conn.commit()
    conn.close()


# ---------- Auth ----------

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def create_user(username: str, email: str, password: str) -> Optional[int]:
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username.strip(), email.strip().lower(), _hash(password))
        )
        conn.commit()
        uid = cur.lastrowid
        # init streak + prefs
        cur.execute("INSERT INTO streaks (user_id) VALUES (?)", (uid,))
        cur.execute("INSERT INTO preferences (user_id) VALUES (?)", (uid,))
        conn.commit()
        conn.close()
        return uid
    except sqlite3.IntegrityError:
        return None


def verify_user(email: str, password: str) -> Optional[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email.strip().lower(), _hash(password))
    )
    row = cur.fetchone()
    if row:
        cur.execute(
            "UPDATE users SET last_login=? WHERE id=?",
            (datetime.now().isoformat(), row["id"])
        )
        conn.commit()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(uid: int) -> Optional[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id=?", (uid,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


# ---------- Timetables ----------

def save_timetable(user_id: int, name: str, config: Dict, grid: Dict, weeks: int = 1) -> int:
    import json
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO timetables (user_id, name, config_json, grid_json, weeks)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, name, json.dumps(config), json.dumps(grid), weeks)
    )
    conn.commit()
    tid = cur.lastrowid
    conn.close()
    return tid


def get_timetables(user_id: int) -> List[Dict]:
    import json
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM timetables WHERE user_id=? ORDER BY created_at DESC",
        (user_id,)
    )
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["config"] = json.loads(d["config_json"])
            d["grid"]   = json.loads(d["grid_json"] or "{}")
        except Exception:
            d["config"] = {}
            d["grid"]   = {}
        result.append(d)
    return result


def get_timetable(tid: int) -> Optional[Dict]:
    import json
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM timetables WHERE id=?", (tid,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    try:
        d["config"] = json.loads(d["config_json"])
        d["grid"]   = json.loads(d["grid_json"] or "{}")
    except Exception:
        d["config"] = {}
        d["grid"]   = {}
    return d


# ---------- Sessions ----------

def log_session(user_id: int, subject: str, duration_min: int,
                timetable_id: Optional[int] = None, notes: str = "") -> None:
    conn = get_conn()
    cur = conn.cursor()
    today = datetime.now().date().isoformat()
    cur.execute(
        """INSERT INTO sessions (user_id, timetable_id, date, subject, duration_min, completed, notes)
           VALUES (?, ?, ?, ?, ?, 1, ?)""",
        (user_id, timetable_id, today, subject, duration_min, notes)
    )
    conn.commit()

    # Update streak
    cur.execute("SELECT * FROM streaks WHERE user_id=?", (user_id,))
    st = cur.fetchone()
    if st:
        last = st["last_date"]
        from datetime import date, timedelta
        today_d = date.today()
        if last == (today_d - timedelta(days=1)).isoformat():
            new_curr = st["current"] + 1
        elif last == today_d.isoformat():
            new_curr = st["current"]
        else:
            new_curr = 1
        new_best = max(new_curr, st["best"])
        cur.execute(
            "UPDATE streaks SET current=?, best=?, last_date=? WHERE user_id=?",
            (new_curr, new_best, today_d.isoformat(), user_id)
        )
    conn.commit()
    conn.close()


def get_sessions(user_id: int, limit: int = 100) -> List[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM sessions WHERE user_id=? ORDER BY date DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_streak(user_id: int) -> Dict:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM streaks WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else {"current": 0, "best": 0}


# ---------- Preferences ----------

def get_prefs(user_id: int) -> Dict:
    import json
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM preferences WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {}
    d = dict(row)
    try:
        d["extra"] = json.loads(d["pref_json"])
    except Exception:
        d["extra"] = {}
    return d


def save_prefs(user_id: int, theme: str, color_accent: str, time_format: str) -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO preferences (user_id, theme, color_accent, time_format)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(user_id) DO UPDATE SET
               theme=excluded.theme,
               color_accent=excluded.color_accent,
               time_format=excluded.time_format""",
        (user_id, theme, color_accent, time_format)
    )
    conn.commit()
    conn.close()
