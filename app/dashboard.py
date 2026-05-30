"""Dashboard with per-key status cards."""
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QScrollArea,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from app.styles import Colors
from db.database import get_all_keys, get_recent_anomalies
from shared.types import Severity


class StatusCard(QFrame):
    """A single key's status card."""

    def __init__(self, key_data: dict):
        super().__init__()
        self.setFixedSize(200, 120)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        platform = key_data.get("platform", "unknown").upper()
        severity = key_data.get("severity", Severity.NORMAL)
        gap = key_data.get("gap", 0)

        # Platform name
        name = QLabel(platform)
        name.setFont(QFont("-apple-system", 11, QFont.Bold))
        layout.addWidget(name)

        # Status indicator
        color = self._severity_color(severity)
        status_text = self._severity_text(severity)
        status = QLabel(f"{color} {status_text}")
        status.setStyleSheet(f"color: {self._severity_hex(severity)}; font-size: 13px;")
        layout.addWidget(status)

        # Gap info
        info = QLabel(f"{gap} 次差异" if gap > 0 else "无异常")
        info.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        layout.addWidget(info)

        layout.addStretch()

    def _severity_color(self, s: Severity) -> str:
        if s == Severity.CRITICAL:
            return "🔴"
        elif s == Severity.WARNING:
            return "🟡"
        return "🟢"

    def _severity_text(self, s: Severity) -> str:
        if s == Severity.CRITICAL:
            return "异常"
        elif s == Severity.WARNING:
            return "注意"
        return "正常"

    def _severity_hex(self, s: Severity) -> str:
        if s == Severity.CRITICAL:
            return Colors.RED
        elif s == Severity.WARNING:
            return Colors.YELLOW
        return Colors.GREEN


class DashboardPanel(QScrollArea):
    """Horizontal scrollable row of status cards."""

    def __init__(self):
        super().__init__()
        self.setFixedHeight(150)
        self.setWidgetResizable(True)
        self.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self._container = QWidget()
        self._layout = QHBoxLayout(self._container)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(12)
        self._layout.addStretch()
        self.setWidget(self._container)

    def refresh(self):
        # Clear existing cards
        while self._layout.count() > 1:
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        keys = get_all_keys()
        anomalies = get_recent_anomalies(50)

        # Compute per-key severity
        key_status: dict[int, dict] = {}
        for k in keys:
            key_status[k.id] = {
                "platform": k.platform.value,
                "severity": Severity.NORMAL,
                "gap": 0,
            }

        for ev in anomalies:
            if ev.key_id in key_status:
                if ev.severity == Severity.CRITICAL:
                    key_status[ev.key_id]["severity"] = Severity.CRITICAL
                elif ev.severity == Severity.WARNING and key_status[ev.key_id]["severity"] != Severity.CRITICAL:
                    key_status[ev.key_id]["severity"] = Severity.WARNING
                key_status[ev.key_id]["gap"] += 1

        for k in keys:
            card = StatusCard(key_status[k.id])
            self._layout.insertWidget(self._layout.count() - 1, card)
