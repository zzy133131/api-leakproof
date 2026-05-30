"""HTTP proxy server that intercepts API calls."""
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from config.settings import PROXY_HOST, PROXY_PORT
from proxy.recorder import ProxyRecorder
from shared.types import ProxyStatus


class ProxyRequestHandler(BaseHTTPRequestHandler):
    recorder: ProxyRecorder = None  # set by server

    def do_POST(self):
        self._handle_request("POST")

    def do_GET(self):
        self._handle_request("GET")

    def do_PUT(self):
        self._handle_request("PUT")

    def do_DELETE(self):
        self._handle_request("DELETE")

    def _handle_request(self, method: str):
        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8", errors="ignore") if content_length else ""

        # Determine the target URL
        target_url = self.headers.get("X-Target-URL", "")
        if not target_url:
            # Fallback: reconstruct from path + Host header
            host = self.headers.get("Host", "")
            target_url = f"https://{host}{self.path}"

        # Match key
        auth = self.headers.get("Authorization", "")
        key_id = self.recorder.find_key_id(auth)

        # Forward the request
        try:
            req = Request(target_url, data=body.encode() if body else None, method=method)
            # Copy relevant headers
            for hdr in ["Content-Type", "Authorization", "x-api-key", "api-key"]:
                val = self.headers.get(hdr)
                if val:
                    req.add_header(hdr, val)

            with urlopen(req, timeout=60) as resp:
                resp_body = resp.read().decode("utf-8", errors="ignore")
                self.send_response(resp.status)
                for h, v in resp.getheaders():
                    if h.lower() not in ("transfer-encoding", "content-encoding"):
                        self.send_header(h, v)
                self.end_headers()
                self.wfile.write(resp_body.encode())

                # Record if key matched
                if key_id is not None:
                    self.recorder.record(key_id, method, target_url, body, resp.status, resp_body)

        except HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except URLError as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Proxy error: {e.reason}"}).encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def log_message(self, format, *args):
        pass  # Suppress default logging to stderr


class ProxyServer:
    """Manages the lifecycle of the local proxy server."""

    def __init__(self):
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._status = ProxyStatus.STOPPED
        self.recorder = ProxyRecorder()

    @property
    def status(self) -> ProxyStatus:
        return self._status

    @property
    def address(self) -> str:
        return f"{PROXY_HOST}:{PROXY_PORT}"

    def start(self) -> bool:
        if self._status == ProxyStatus.RUNNING:
            return True
        try:
            ProxyRequestHandler.recorder = self.recorder
            self._server = HTTPServer((PROXY_HOST, PROXY_PORT), ProxyRequestHandler)
            self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
            self._thread.start()
            self._status = ProxyStatus.RUNNING
            return True
        except OSError as e:
            self._status = ProxyStatus.ERROR
            print(f"Failed to start proxy: {e}")
            return False

    def stop(self) -> None:
        if self._server:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
            self._thread = None
        self._status = ProxyStatus.STOPPED

    def refresh_keys(self) -> None:
        """Reload key cache after user adds/removes keys."""
        self.recorder._refresh_key_cache()
