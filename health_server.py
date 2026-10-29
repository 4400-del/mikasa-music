"""Minimal Render health server that never exposes the repository filesystem."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os


class HealthHandler(BaseHTTPRequestHandler):
    def _send_health(self, include_body=True):
        if self.path not in ("/", "/health", "/healthz"):
            self.send_error(404, "Not found")
            return
        body = json.dumps({"status": "ok", "service": "mikasa-music"}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if include_body:
            self.wfile.write(body)

    def do_GET(self):
        self._send_health(include_body=True)

    def do_HEAD(self):
        self._send_health(include_body=False)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    ThreadingHTTPServer(("0.0.0.0", port), HealthHandler).serve_forever()
