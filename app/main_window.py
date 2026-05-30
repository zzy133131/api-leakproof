"""Main application window."""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from app.styles import Colors, STYLESHEET
from app.dashboard import DashboardPanel
from app.key_manager import KeyManagerPanel
from app.alert_panel import AlertPanel
from proxy.server import ProxyServer
from monitor.anomaly_detector import AnomalyDetector
from monitor.alerter import Alerter
from monitor.scheduler import MonitorScheduler
from shared.types import ProxyStatus


class MainWindow(QMainWindow):
    """API LeakProof main window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("API LeakProof")
        self.setMinimumSize(960, 680)
        self.resize(1024, 720)

        # Core components
        self.proxy = ProxyServer()
        self.alerter = Alerter()
        self.detector = AnomalyDetector()
        self.scheduler = MonitorScheduler(self.detector, self.alerter)

        # Setup UI
        self.setStyleSheet(STYLESHEET)
        self._setup_ui()

        # Auto-start proxy
        self._start_proxy()

        # Start monitoring
        self.scheduler.start()

        # Periodic UI refresh
        self._refresh_timer = QTimer()
        self._refresh_timer.timeout.connect(self._refresh_status)
        self._refresh_timer.start(5000)

        # Alert callbacks
        self.alerter.register_callback(self._on_alert)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 12, 20, 16)
        root.setSpacing(12)

        # ── Header ──────────────────────────────────────────
        header = QHBoxLayout()
        title = QLabel("🔑 API LeakProof")
        title.setFont(QFont("-apple-system", 18, QFont.Bold))
        header.addWidget(title)
        header.addStretch()

        self._status_label = QLabel("● 代理未启动")
        self._status_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        header.addWidget(self._status_label)

        root.addLayout(header)

        # ── Status bar line ─────────────────────────────────
        status_line = QHBoxLayout()
        self._proxy_addr_label = QLabel("localhost:8080")
        self._proxy_addr_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        status_line.addWidget(self._proxy_addr_label)
        status_line.addStretch()
        self._last_check_label = QLabel("上次检查: --")
        self._last_check_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        status_line.addWidget(self._last_check_label)
        root.addLayout(status_line)

        # ── Dashboard cards ─────────────────────────────────
        self.dashboard = DashboardPanel()
        root.addWidget(self.dashboard)

        # ── Monitor table ───────────────────────────────────
        self.key_manager = KeyManagerPanel()
        root.addWidget(self.key_manager, 1)

        # ── Alert log ───────────────────────────────────────
        self.alert_panel = AlertPanel()
        root.addWidget(self.alert_panel)

        # ── Bottom action bar ───────────────────────────────
        actions = QHBoxLayout()
        add_btn = QPushButton("+ 添加 Key")
        add_btn.clicked.connect(self.key_manager.show_add_dialog)
        actions.addWidget(add_btn)

        self._proxy_btn = QPushButton("⏹ 停止代理")
        self._proxy_btn.setObjectName("secondaryBtn")
        self._proxy_btn.clicked.connect(self._toggle_proxy)
        actions.addWidget(self._proxy_btn)

        pause_btn = QPushButton("⏸ 暂停全部")
        pause_btn.setObjectName("secondaryBtn")
        pause_btn.clicked.connect(self._toggle_all_pause)
        actions.addWidget(pause_btn)

        actions.addStretch()
        root.addLayout(actions)

    def _start_proxy(self):
        if self.proxy.start():
            self._status_label.setText("● 代理运行中")
            self._status_label.setStyleSheet(f"color: {Colors.GREEN}; font-size: 12px;")
            self._proxy_addr_label.setText(self.proxy.address)
            self._proxy_btn.setText("⏹ 停止代理")
        else:
            self._status_label.setText("● 代理启动失败")
            self._status_label.setStyleSheet(f"color: {Colors.RED}; font-size: 12px;")

    def _toggle_proxy(self):
        if self.proxy.status == ProxyStatus.RUNNING:
            self.proxy.stop()
            self._status_label.setText("● 代理已停止")
            self._status_label.setStyleSheet(f"color: {Colors.YELLOW}; font-size: 12px;")
            self._proxy_btn.setText("▶ 启动代理")
        else:
            self._start_proxy()

    def _toggle_all_pause(self):
        from db.database import get_all_keys, update_key_alert
        keys = get_all_keys()
        all_enabled = all(k.alert_enabled for k in keys)
        for k in keys:
            update_key_alert(k.id, not all_enabled)
        self.key_manager.refresh()
        btn = self.sender()
        if btn:
            btn.setText("▶ 恢复全部" if all_enabled else "⏸ 暂停全部")

    def _refresh_status(self):
        status = self.proxy.status
        if status == ProxyStatus.RUNNING:
            self._status_label.setText("● 代理运行中")
            self._status_label.setStyleSheet(f"color: {Colors.GREEN}; font-size: 12px;")
        else:
            self._status_label.setText("● 代理已停止")
            self._status_label.setStyleSheet(f"color: {Colors.YELLOW}; font-size: 12px;")

        if self.scheduler.last_check:
            self._last_check_label.setText(
                f"上次检查: {self.scheduler.last_check.strftime('%H:%M:%S')}"
            )
        self.dashboard.refresh()
        self.key_manager.refresh()
        self.alert_panel.refresh()

    def _on_alert(self, event, key):
        """Called when alerter fires an alert."""
        self.alert_panel.refresh()
        self.dashboard.refresh()
        self.key_manager.refresh()

    def closeEvent(self, event):
        self.proxy.stop()
        self.scheduler.stop()
        event.accept()
