"""Alert notifications via macOS Notification Center and in-app logging."""
import json
import subprocess
from datetime import datetime

from shared.types import AnomalyEvent, MonitoredKey, Severity


class Alerter:
    """Sends alerts to macOS Notification Center and tracks alert state."""

    def __init__(self):
        self._last_alert_time: dict[int, datetime] = {}
        self.alert_callbacks: list[callable] = []

    def alert(self, event: AnomalyEvent, key: MonitoredKey) -> None:
        """Send an alert for an anomaly event."""
        detail = json.loads(event.detail_json)
        title = self._format_title(event, key)
        body = detail.get("message", "检测到API异常调用")

        # macOS notification
        self._send_macos_notification(title, body)

        # Notify GUI callbacks
        for cb in self.alert_callbacks:
            try:
                cb(event, key)
            except Exception:
                pass

        self._last_alert_time[key.id] = datetime.now()

    def _format_title(self, event: AnomalyEvent, key: MonitoredKey) -> str:
        platform_name = key.platform.value.upper()
        prefix = key.key_prefix[:8]
        if event.severity == Severity.CRITICAL:
            return f"🔴 [{platform_name}] API异常告警 — {prefix}***"
        return f"🟡 [{platform_name}] API注意 — {prefix}***"

    def _send_macos_notification(self, title: str, body: str) -> None:
        """Send a native macOS notification via osascript."""
        try:
            script = f'''
            display notification "{body}" with title "{title}" sound name "default"
            '''
            subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, timeout=5
            )
        except Exception:
            print(f"[ALERT] {title}: {body}")

    def register_callback(self, callback) -> None:
        """Register a callback for GUI updates on alerts."""
        self.alert_callbacks.append(callback)
