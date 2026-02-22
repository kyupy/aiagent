from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .service import ChatRequest, RunnerService


class RunnerHandler(BaseHTTPRequestHandler):
    service = RunnerService()

    def _json_response(self, status_code: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._json_response(200, {"status": "ok"})
            return
        self._json_response(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/chat":
            content_length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_length)
            try:
                payload = json.loads(raw.decode("utf-8"))
                req = ChatRequest(
                    thread_id=payload["thread_id"],
                    user_id=payload["user_id"],
                    text=payload["text"],
                    model=payload.get("model", "gemini-flash"),
                )
            except Exception:
                self._json_response(400, {"error": "invalid request"})
                return

            res = self.service.handle_chat(req)
            self._json_response(
                200,
                {"kind": res.kind, "message": res.message, "thread_id": res.thread_id},
            )
            return

        if self.path == "/permissions/write":
            content_length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_length)
            try:
                payload = json.loads(raw.decode("utf-8"))
                thread_id = payload["thread_id"]
                self.service.grant_write_permission(thread_id)
            except Exception:
                self._json_response(400, {"error": "invalid request"})
                return
            self._json_response(200, {"status": "ok"})
            return

        self._json_response(404, {"error": "not found"})


def run(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), RunnerHandler)
    print(f"runner listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
