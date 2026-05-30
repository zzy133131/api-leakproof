"""Database operations for monitored keys, proxy logs, and anomaly events."""
import sqlite3
from datetime import datetime
from typing import Optional

from db.models import get_connection
from shared.types import (
    MonitoredKey, ProxyLogEntry, AnomalyEvent,
    Platform, Severity, AnomalyType,
)


# ── Monitored Keys ─────────────────────────────────────────────

def insert_key(key: MonitoredKey) -> int:
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO monitored_key (key_prefix, key_encrypted, platform, custom_base_url, alert_enabled)
           VALUES (?, ?, ?, ?, ?)""",
        (key.key_prefix, key.key_encrypted, key.platform.value,
         key.custom_base_url, int(key.alert_enabled))
    )
    conn.commit()
    key_id = cursor.lastrowid
    conn.close()
    return key_id


def get_all_keys() -> list[MonitoredKey]:
    conn = get_connection()
    rows = conn.execute("SELECT * FROM monitored_key ORDER BY created_at DESC").fetchall()
    conn.close()
    return [_row_to_key(r) for r in rows]


def get_key_by_id(key_id: int) -> Optional[MonitoredKey]:
    conn = get_connection()
    row = conn.execute("SELECT * FROM monitored_key WHERE id = ?", (key_id,)).fetchone()
    conn.close()
    return _row_to_key(row) if row else None


def delete_key(key_id: int) -> None:
    conn = get_connection()
    conn.execute("DELETE FROM monitored_key WHERE id = ?", (key_id,))
    conn.commit()
    conn.close()


def update_key_alert(key_id: int, enabled: bool) -> None:
    conn = get_connection()
    conn.execute("UPDATE monitored_key SET alert_enabled = ? WHERE id = ?",
                 (int(enabled), key_id))
    conn.commit()
    conn.close()


def _row_to_key(row: sqlite3.Row) -> MonitoredKey:
    return MonitoredKey(
        id=row["id"],
        key_prefix=row["key_prefix"],
        key_encrypted=row["key_encrypted"],
        platform=Platform(row["platform"]),
        custom_base_url=row["custom_base_url"],
        alert_enabled=bool(row["alert_enabled"]),
        created_at=datetime.fromisoformat(row["created_at"]),
    )


# ── Proxy Logs ─────────────────────────────────────────────────

def insert_proxy_log(entry: ProxyLogEntry) -> int:
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO proxy_log (key_id, timestamp, method, endpoint,
           request_body_size, response_status, token_count, source_ip, cost_estimate)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (entry.key_id, entry.timestamp.isoformat(), entry.method, entry.endpoint,
         entry.request_body_size, entry.response_status, entry.token_count,
         entry.source_ip, entry.cost_estimate)
    )
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    return log_id


def count_proxy_logs_since(key_id: int, since: datetime) -> int:
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM proxy_log WHERE key_id = ? AND timestamp >= ?",
        (key_id, since.isoformat())
    ).fetchone()
    conn.close()
    return row["cnt"]


def get_proxy_logs_since(key_id: int, since: datetime) -> list[ProxyLogEntry]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM proxy_log WHERE key_id = ? AND timestamp >= ? ORDER BY timestamp DESC",
        (key_id, since.isoformat())
    ).fetchall()
    conn.close()
    return [_row_to_log(r) for r in rows]


def _row_to_log(row: sqlite3.Row) -> ProxyLogEntry:
    return ProxyLogEntry(
        id=row["id"],
        key_id=row["key_id"],
        timestamp=datetime.fromisoformat(row["timestamp"]),
        method=row["method"],
        endpoint=row["endpoint"],
        request_body_size=row["request_body_size"],
        response_status=row["response_status"],
        token_count=row["token_count"],
        source_ip=row["source_ip"],
        cost_estimate=row["cost_estimate"],
    )


# ── Anomaly Events ─────────────────────────────────────────────

def insert_anomaly(event: AnomalyEvent) -> int:
    conn = get_connection()
    cursor = conn.execute(
        """INSERT INTO anomaly_event (key_id, detected_at, severity, anomaly_type, detail_json, acknowledged)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (event.key_id, event.detected_at.isoformat(), event.severity.value,
         event.anomaly_type.value, event.detail_json, int(event.acknowledged))
    )
    conn.commit()
    ev_id = cursor.lastrowid
    conn.close()
    return ev_id


def get_recent_anomalies(limit: int = 50) -> list[AnomalyEvent]:
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM anomaly_event ORDER BY detected_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [_row_to_anomaly(r) for r in rows]


def count_recent_anomalies_for_key(key_id: int, since: datetime) -> int:
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) as cnt FROM anomaly_event WHERE key_id = ? AND detected_at >= ?",
        (key_id, since.isoformat())
    ).fetchone()
    conn.close()
    return row["cnt"]


def get_consecutive_gap_count(key_id: int) -> int:
    """Count consecutive checks with volume gaps for a key."""
    conn = get_connection()
    rows = conn.execute(
        """SELECT anomaly_type FROM anomaly_event
           WHERE key_id = ? AND anomaly_type = 'volume_gap'
           ORDER BY detected_at DESC LIMIT ?""",
        (key_id, 10)
    ).fetchall()
    conn.close()
    count = 0
    for row in rows:
        if row["anomaly_type"] == "volume_gap":
            count += 1
        else:
            break
    return count


def acknowledge_anomaly(event_id: int) -> None:
    conn = get_connection()
    conn.execute("UPDATE anomaly_event SET acknowledged = 1 WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()


def _row_to_anomaly(row: sqlite3.Row) -> AnomalyEvent:
    return AnomalyEvent(
        id=row["id"],
        key_id=row["key_id"],
        detected_at=datetime.fromisoformat(row["detected_at"]),
        severity=Severity(row["severity"]),
        anomaly_type=AnomalyType(row["anomaly_type"]),
        detail_json=row["detail_json"],
        acknowledged=bool(row["acknowledged"]),
    )
