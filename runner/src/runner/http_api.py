from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from .service import ChatRequest, RunnerService
from .session import SessionStore


def build_handler(service: RunnerService) -> type[BaseHTTPRequestHandler]:
    class RunnerHandler(BaseHTTPRequestHandler):
        _service = service

        def _json_response(self, status_code: int, payload: dict) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _read_json(self) -> dict:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0:
                raise ValueError("empty body")
            return json.loads(self.rfile.read(content_length).decode("utf-8"))

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path == "/health":
                self._json_response(200, {"status": "ok"})
                return
            self._json_response(404, {"error": "not found"})

        def do_POST(self) -> None:  # noqa: N802
            path = urlparse(self.path).path

            if path == "/chat":
                try:
                    payload = self._read_json()
                    req = ChatRequest(
                        thread_id=payload["thread_id"],
                        user_id=payload["user_id"],
                        text=payload["text"],
                        model=payload.get("model", "gemini-flash"),
                    )
                except (ValueError, KeyError, json.JSONDecodeError):
                    self._json_response(400, {"error": "invalid request"})
                    return

                res = self._service.handle_chat(req)
                self._json_response(200, {"kind": res.kind, "message": res.message, "thread_id": res.thread_id})
                return

            if path == "/permissions":
                try:
                    payload = self._read_json()
                    self._service.update_permissions(
                        thread_id=payload["thread_id"],
                        user_id=payload["user_id"],
                        model=payload.get("model", "gemini-flash"),
                        read_ok=payload.get("read_ok"),
                        write_ok=payload.get("write_ok"),
                    )
                except (ValueError, KeyError, json.JSONDecodeError):
                    self._json_response(400, {"error": "invalid request"})
                    return
                self._json_response(200, {"status": "ok"})
                return

            self._json_response(404, {"error": "not found"})

    return RunnerHandler


def run(host: str = "0.0.0.0", port: int = 8000) -> None:
    db_path = os.getenv("RUNNER_DB_PATH", "data/db.sqlite3")
    service = RunnerService(SessionStore(db_path=db_path))
    server = ThreadingHTTPServer((host, port), build_handler(service))
    print(f"runner listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
