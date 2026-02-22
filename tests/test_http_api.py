import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

from runner.http_api import build_handler
from runner.service import RunnerService
from runner.session import SessionStore


def test_permissions_endpoint_bootstraps_thread(tmp_path: Path) -> None:
    service = RunnerService(SessionStore(db_path=str(tmp_path / "db.sqlite3")))
    server = ThreadingHTTPServer(("127.0.0.1", 0), build_handler(service))
    port = server.server_address[1]
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    try:
        payload = json.dumps({"thread_id": "t1", "user_id": "u1", "write_ok": True}).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/permissions",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as res:
            body = json.loads(res.read().decode("utf-8"))
        assert body["status"] == "ok"

        state = service.session_store.get_or_create("t1", "u1")
        assert state.write_ok is True
    finally:
        server.shutdown()
        server.server_close()
