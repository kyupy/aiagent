from __future__ import annotations

import json
from dataclasses import dataclass
from urllib import request


@dataclass
class BotRunnerClient:
    runner_base_url: str

    def _post_json(self, path: str, payload: dict) -> dict:
        req = request.Request(
            f"{self.runner_base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=10) as res:
            return json.loads(res.read().decode("utf-8"))

    def chat(self, thread_id: str, user_id: str, text: str, model: str = "gemini-flash") -> dict:
        return self._post_json(
            "/chat",
            {"thread_id": thread_id, "user_id": user_id, "text": text, "model": model},
        )

    def set_permissions(
        self,
        thread_id: str,
        user_id: str,
        read_ok: bool | None = None,
        write_ok: bool | None = None,
        model: str = "gemini-flash",
    ) -> dict:
        payload: dict = {"thread_id": thread_id, "user_id": user_id, "model": model}
        if read_ok is not None:
            payload["read_ok"] = read_ok
        if write_ok is not None:
            payload["write_ok"] = write_ok
        return self._post_json("/permissions", payload)
