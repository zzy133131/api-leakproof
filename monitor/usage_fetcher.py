"""Fetches official usage data from API providers."""
import requests
from datetime import datetime
from typing import Optional

from shared.types import MonitoredKey, UsageSnapshot, Platform


class UsageFetcher:
    """Pulls usage stats from each platform's API."""

    def fetch(self, key: MonitoredKey, api_key: str, since: datetime) -> Optional[UsageSnapshot]:
        """Fetch usage for a single key since a given time."""
        if key.platform == Platform.OPENAI:
            return self._fetch_openai(key, api_key, since)
        return None

    def _fetch_openai(self, key: MonitoredKey, api_key: str, since: datetime) -> Optional[UsageSnapshot]:
        """Fetch OpenAI usage via /v1/usage endpoint (if available)."""
        try:
            url = "https://api.openai.com/v1/usage"
            params = {"date": since.strftime("%Y-%m-%d")}
            headers = {"Authorization": f"Bearer {api_key}"}
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            if resp.status_code != 200:
                return None
            data = resp.json()
            total_tokens = data.get("total_usage", 0) if isinstance(data, dict) else 0
            return UsageSnapshot(
                platform=key.platform,
                key_id=key.id or 0,
                timestamp=datetime.now(),
                total_calls=0,
                total_tokens=total_tokens,
                total_cost=0.0,
                caller_ips=[],
            )
        except Exception:
            return None

    def fetch_usage_count(self, key: MonitoredKey, api_key: str, since: datetime) -> int:
        """Get a simple count of calls since a given time."""
        snapshot = self.fetch(key, api_key, since)
        if snapshot:
            return snapshot.total_calls
        return 0
