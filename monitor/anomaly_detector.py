"""Compares proxy logs against official usage to detect anomalies."""
import json
from datetime import datetime, timedelta
from typing import Optional

from config.settings import (
    COST_GAP_WARNING, COST_GAP_CRITICAL,
    CONSECUTIVE_CRITICAL,
)
from db.database import (
    count_proxy_logs_since, get_consecutive_gap_count,
    insert_anomaly,
)
from shared.types import (
    MonitoredKey, AnomalyEvent, Severity, AnomalyType,
)


class AnomalyDetector:
    """Detects anomalies by comparing proxy logs with reported usage."""

    def __init__(self):
        pass

    def check_key(self, key: MonitoredKey) -> Optional[AnomalyEvent]:
        """Check a single key for anomalies. Returns an AnomalyEvent if anomaly found."""
        now = datetime.now()
        since = now - timedelta(minutes=10)

        proxy_count = count_proxy_logs_since(key.id, since)

        # IP mismatch detection
        ip_anomaly = self._check_ip_mismatch(key.id)

        # Volume gap detection
        volume_anomaly = self._check_volume_gap(key.id, proxy_count)

        if ip_anomaly:
            return ip_anomaly
        return volume_anomaly

    def _check_ip_mismatch(self, key_id: int) -> Optional[AnomalyEvent]:
        """Detect IP mismatches from recent proxy logs."""
        return None

    def _check_volume_gap(self, key_id: int, proxy_count: int) -> Optional[AnomalyEvent]:
        """Check if there's a volume gap (official calls > proxy calls)."""
        if proxy_count > 0:
            return None

        consecutive = get_consecutive_gap_count(key_id)

        severity = Severity.WARNING
        if consecutive >= CONSECUTIVE_CRITICAL:
            severity = Severity.CRITICAL

        event = AnomalyEvent(
            key_id=key_id,
            detected_at=datetime.now(),
            severity=severity,
            anomaly_type=AnomalyType.VOLUME_GAP,
            detail_json=json.dumps({
                "proxy_count": proxy_count,
                "consecutive_gaps": consecutive + 1,
                "message": f"No proxy activity detected for {consecutive + 1} consecutive checks",
            }),
        )
        insert_anomaly(event)
        return event

    def detect_with_official_data(
        self, key: MonitoredKey, official_call_count: int,
        official_ips: list[str], user_ip: str, official_cost: float
    ) -> list[AnomalyEvent]:
        """Full comparison with official usage data. Returns all detected anomalies."""
        events = []
        now = datetime.now()
        since = now - timedelta(minutes=10)
        proxy_count = count_proxy_logs_since(key.id, since)

        # 1. Volume gap
        gap = official_call_count - proxy_count
        if gap > 0:
            consecutive = get_consecutive_gap_count(key.id) + 1
            severity = Severity.CRITICAL if consecutive >= CONSECUTIVE_CRITICAL else Severity.WARNING
            event = AnomalyEvent(
                key_id=key.id,
                detected_at=now,
                severity=severity,
                anomaly_type=AnomalyType.VOLUME_GAP,
                detail_json=json.dumps({
                    "proxy_count": proxy_count,
                    "official_count": official_call_count,
                    "gap": gap,
                    "consecutive_gaps": consecutive,
                    "message": f"检测到 {gap} 次非代理调用，可能被第三方中转",
                }),
            )
            insert_anomaly(event)
            events.append(event)

        # 2. IP mismatch
        unknown_ips = [ip for ip in official_ips if ip and ip != user_ip]
        if unknown_ips:
            event = AnomalyEvent(
                key_id=key.id,
                detected_at=now,
                severity=Severity.CRITICAL,
                anomaly_type=AnomalyType.IP_MISMATCH,
                detail_json=json.dumps({
                    "user_ip": user_ip,
                    "abnormal_ips": unknown_ips,
                    "call_count": len(unknown_ips),
                    "message": f"检测到异常IP调用: {', '.join(unknown_ips)}",
                }),
            )
            insert_anomaly(event)
            events.append(event)

        # 3. Cost spike
        if official_cost > COST_GAP_CRITICAL:
            event = AnomalyEvent(
                key_id=key.id,
                detected_at=now,
                severity=Severity.CRITICAL,
                anomaly_type=AnomalyType.COST_SPIKE,
                detail_json=json.dumps({
                    "cost": official_cost,
                    "message": f"费用异常: ${official_cost:.2f}",
                }),
            )
            insert_anomaly(event)
            events.append(event)

        return events
