"""Scheduler for periodic monitoring checks."""
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from config.settings import CHECK_INTERVAL_MINUTES
from db.database import get_all_keys
from monitor.anomaly_detector import AnomalyDetector
from monitor.alerter import Alerter


class MonitorScheduler:
    """Runs periodic anomaly checks for all monitored keys."""

    def __init__(self, detector: AnomalyDetector, alerter: Alerter):
        self._scheduler = BackgroundScheduler()
        self._detector = detector
        self._alerter = alerter
        self._last_check: datetime | None = None

    @property
    def last_check(self) -> datetime | None:
        return self._last_check

    def start(self) -> None:
        self._scheduler.add_job(
            self._run_check,
            "interval",
            minutes=CHECK_INTERVAL_MINUTES,
            id="monitor_check",
            next_run_time=datetime.now() + timedelta(seconds=5),
        )
        self._scheduler.start()

    def stop(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)

    def run_check_now(self) -> list:
        """Run a check immediately (for manual refresh)."""
        return self._run_check()

    def _run_check(self) -> list:
        self._last_check = datetime.now()
        keys = get_all_keys()
        events = []
        for key in keys:
            if key.alert_enabled:
                ev = self._detector.check_key(key)
                if ev:
                    events.append(ev)
                    self._alerter.alert(ev, key)
        return events
