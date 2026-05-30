"""Alert log panel showing recent anomaly events."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame,
)
from PySide6.QtCore import Qt

from app.styles import Colors
from db.database import get_recent_anomalies, get_key_by_id
from shared.types import Severity
import json


class AlertItem(QFrame):
    """A single alert entry in the log."""

    def __init__(self, event, key_prefix: str, platform: str):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border-bottom: 1px solid {Colors.BORDER};
                padding: 6px 0px;
            }}
        """)
        self.setFixedHeight(36)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        # Time
        time_str = event.detected_at.strftime("%H:%M")
        time_label = QLabel(time_str)
        time_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; font-family: 'SF Mono', monospace;")
        time_label.setFixedWidth(40)
        layout.addWidget(time_label)

        # Icon
        icon = "🔴" if event.severity == Severity.CRITICAL else "🟡"
        icon_label = QLabel(icon)
        icon_label.setFixedWidth(24)
        layout.addWidget(icon_label)

        # Detail
        detail = json.loads(event.detail_json)
        msg = detail.get("message", "异常调用检测")
        text = f"[{platform}] {key_prefix}*** {msg}"
        text_label = QLabel(text)
        text_label.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 12px;")
        layout.addWidget(text_label, 1)


class AlertPanel(QWidget):
    """Scrollable alert log panel."""

    def __init__(self):
        super().__init__()
        self.setFixedHeight(160)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        header = QLabel("告警日志")
        header.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; font-weight: 600; text-transform: uppercase;")
        layout.addWidget(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"QScrollArea {{ border: 1px solid {Colors.BORDER}; border-radius: 8px; background-color: {Colors.BG_SECONDARY}; }}")

        self._container = QWidget()
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setContentsMargins(0, 0, 0, 0)
        self._container_layout.setSpacing(0)
        self._container_layout.addStretch()
        self.scroll.setWidget(self._container)

        layout.addWidget(self.scroll)

    def refresh(self):
        # Clear existing items
        while self._container_layout.count() > 1:
            item = self._container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        events = get_recent_anomalies(30)
        for ev in events:
            key = get_key_by_id(ev.key_id)
            prefix = key.key_prefix if key else "???"
            platform = key.platform.value.upper() if key else "???"
            item = AlertItem(ev, prefix, platform)
            self._container_layout.insertWidget(self._container_layout.count() - 1, item)
