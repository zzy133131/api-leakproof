"""Key management table panel."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QPushButton, QMessageBox,
    QAbstractItemView,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.styles import Colors
from app.add_key_dialog import AddKeyDialog
from db.database import get_all_keys, delete_key, update_key_alert, get_recent_anomalies
from shared.types import Severity


class KeyManagerPanel(QWidget):
    """Table showing all monitored keys and their status."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        header = QLabel("监控列表")
        header.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; font-weight: 600; text-transform: uppercase;")
        layout.addWidget(header)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Key", "平台", "状态", "差异", "费用", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 140)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def refresh(self):
        keys = get_all_keys()
        anomalies = get_recent_anomalies(50)

        # Build anomaly map
        anomaly_map: dict[int, list] = {}
        for ev in anomalies:
            anomaly_map.setdefault(ev.key_id, []).append(ev)

        self.table.setRowCount(len(keys))
        for i, key in enumerate(keys):
            evs = anomaly_map.get(key.id, [])
            severity = Severity.NORMAL
            gap = len(evs)
            cost = 0.0

            for ev in evs:
                if ev.severity == Severity.CRITICAL:
                    severity = Severity.CRITICAL
                elif ev.severity == Severity.WARNING and severity != Severity.CRITICAL:
                    severity = Severity.WARNING

            # Key prefix (masked)
            self.table.setItem(i, 0, QTableWidgetItem(f"{key.key_prefix}***"))

            # Platform
            self.table.setItem(i, 1, QTableWidgetItem(key.platform.value.upper()))

            # Status
            text = "🟢 正常"
            if severity == Severity.CRITICAL:
                text = "🔴 异常"
            elif severity == Severity.WARNING:
                text = "🟡 注意"
            self.table.setItem(i, 2, QTableWidgetItem(text))

            # Gap
            self.table.setItem(i, 3, QTableWidgetItem(f"+{gap}" if gap > 0 else "0"))

            # Cost
            self.table.setItem(i, 4, QTableWidgetItem(f"${cost:.2f}"))

            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 2, 4, 2)
            action_layout.setSpacing(6)

            detail_btn = QPushButton("详情")
            detail_btn.setObjectName("secondaryBtn")
            detail_btn.setFixedSize(50, 26)
            detail_btn.setStyleSheet("font-size: 11px; padding: 2px 6px;")
            detail_btn.clicked.connect(lambda checked, kid=key.id: self._show_detail(kid))
            action_layout.addWidget(detail_btn)

            toggle_btn = QPushButton("暂停" if key.alert_enabled else "恢复")
            toggle_btn.setObjectName("secondaryBtn")
            toggle_btn.setFixedSize(50, 26)
            toggle_btn.setStyleSheet("font-size: 11px; padding: 2px 6px;")
            toggle_btn.clicked.connect(lambda checked, k=key: self._toggle_key(k.id, not k.alert_enabled))
            action_layout.addWidget(toggle_btn)

            self.table.setCellWidget(i, 5, action_widget)

    def show_add_dialog(self):
        dlg = AddKeyDialog(self)
        if dlg.exec():
            self.refresh()
            # Notify proxy to refresh key cache
            w = self.window()
            if hasattr(w, 'proxy'):
                w.proxy.refresh_keys()

    def _show_detail(self, key_id: int):
        from db.database import get_key_by_id
        key = get_key_by_id(key_id)
        evs = get_recent_anomalies(50)
        key_evs = [e for e in evs if e.key_id == key_id]
        info = f"Key: {key.key_prefix}***\n平台: {key.platform.value.upper()}\n"
        if key_evs:
            import json
            latest = key_evs[0]
            detail = json.loads(latest.detail_json)
            info += f"最近告警: {detail.get('message', 'N/A')}"
        else:
            info += "无告警记录"
        QMessageBox.information(self, "Key 详情", info)

    def _toggle_key(self, key_id: int, enabled: bool):
        update_key_alert(key_id, enabled)
        self.refresh()
