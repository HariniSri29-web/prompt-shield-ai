"""Step 9 - Logging & database (SQLite)."""
import json
import sqlite3
from datetime import datetime, timezone
from .config import DB_PATH

_SCHEMA = """
CREATE TABLE IF NOT EXISTS prompt_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    user_id TEXT,
    original_prompt TEXT NOT NULL,
    normalized_prompt TEXT,
    ml_score REAL, rule_score REAL, risk_score REAL,
    risk_level TEXT, action TEXT,
    matched_rules TEXT,
    safe_prompt TEXT
);
"""


class LogDB:
    def __init__(self, path=DB_PATH):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = str(path)
        with self._conn() as c:
            c.executescript(_SCHEMA)

    def _conn(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def log(self, r: dict) -> int:
        with self._conn() as c:
            cur = c.execute(
                """INSERT INTO prompt_logs (timestamp,user_id,original_prompt,normalized_prompt,ml_score,rule_score,
                   risk_score,risk_level,action,matched_rules,safe_prompt) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (datetime.now(timezone.utc).isoformat(timespec="seconds"), r.get("user_id"), r["original_prompt"],
                 r["normalized_prompt"], r["ml_score"], r["rule_score"], r["risk_score"], r["risk_level"], r["action"],
                 json.dumps([m["rule"] for m in r["matched_rules"]]), r.get("safe_prompt")))
            return cur.lastrowid

    def recent(self, limit: int = 50):
        with self._conn() as c:
            return [dict(x) for x in c.execute("SELECT * FROM prompt_logs ORDER BY id DESC LIMIT ?", (limit,))]

    def stats(self):
        with self._conn() as c:
            return {row["action"]: row["n"] for row in c.execute("SELECT action, COUNT(*) n FROM prompt_logs GROUP BY action")}
