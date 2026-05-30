"""Records proxy requests to the database."""
from db.database import insert_proxy_log, get_all_keys
from shared.types import ProxyLogEntry, Platform
from proxy.platform_rules import detect_platform, extract_token_count, estimate_cost
import json
import socket
from datetime import datetime


class ProxyRecorder:
    """Handles request logging and key matching."""

    def __init__(self):
        self._local_ip = self._get_local_ip()
        self._key_cache: dict[str, int] = {}
        self._refresh_key_cache()

    def _get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def _refresh_key_cache(self) -> None:
        """Reload key cache from DB."""
        keys = get_all_keys()
        self._key_cache: dict[str, int] = {}
        for k in keys:
            self._key_cache[k.key_prefix] = k.id

    def find_key_id(self, auth_header: str) -> int | None:
        """Match an Authorization header to a monitored key."""
        if not auth_header:
            return None
        token = auth_header.removeprefix("Bearer ").removeprefix("bearer ")
        self._refresh_key_cache()
        for prefix, key_id in self._key_cache.items():
            if token.startswith(prefix):
                return key_id
        return None

    def record(self, key_id: int, method: str, url: str,
               request_body: str, response_status: int,
               response_body: str) -> None:
        """Record a proxied request."""
        platform = detect_platform(url)
        resp_json = {}
        token_count = None
        try:
            resp_json = json.loads(response_body) if response_body else {}
            token_count = extract_token_count(resp_json, platform)
        except json.JSONDecodeError:
            pass

        cost = estimate_cost(platform, token_count)

        entry = ProxyLogEntry(
            key_id=key_id,
            timestamp=datetime.now(),
            method=method,
            endpoint=url,
            request_body_size=len(request_body.encode()) if request_body else 0,
            response_status=response_status,
            token_count=token_count,
            source_ip=self._local_ip,
            cost_estimate=cost,
        )
        insert_proxy_log(entry)

    def get_local_ip(self) -> str:
        return self._local_ip
