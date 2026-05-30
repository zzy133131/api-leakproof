"""Database models and table creation."""
import sqlite3
from config.settings import DB_PATH


CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS monitored_key (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_prefix TEXT NOT NULL,
    key_encrypted TEXT NOT NULL,
    platform TEXT NOT NULL DEFAULT 'openai',
    custom_base_url TEXT,
    alert_enabled INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS proxy_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_id INTEGER NOT NULL,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    method TEXT NOT NULL DEFAULT 'POST',
    endpoint TEXT NOT NULL DEFAULT '',
    request_body_size INTEGER NOT NULL DEFAULT 0,
    response_status INTEGER NOT NULL DEFAULT 200,
    token_count INTEGER,
    source_ip TEXT NOT NULL DEFAULT '',
    cost_estimate REAL NOT NULL DEFAULT 0.0,
    FOREIGN KEY (key_id) REFERENCES monitored_key(id)
);

CREATE TABLE IF NOT EXISTS anomaly_event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_id INTEGER NOT NULL,
    detected_at TEXT NOT NULL DEFAULT (datetime('now')),
    severity TEXT NOT NULL DEFAULT 'normal',
    anomaly_type TEXT NOT NULL DEFAULT 'volume_gap',
    detail_json TEXT NOT NULL DEFAULT '{}',
    acknowledged INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (key_id) REFERENCES monitored_key(id)
);

CREATE INDEX IF NOT EXISTS idx_proxy_log_key_id ON proxy_log(key_id);
CREATE INDEX IF NOT EXISTS idx_proxy_log_timestamp ON proxy_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_anomaly_event_key_id ON anomaly_event(key_id);
CREATE INDEX IF NOT EXISTS idx_anomaly_event_detected_at ON anomaly_event(detected_at);
"""


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory enabled."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db() -> None:
    """Create all tables if they don't exist."""
    conn = get_connection()
    conn.executescript(CREATE_TABLES_SQL)
    conn.commit()
    conn.close()
