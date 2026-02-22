from __future__ import annotations

import json
from dataclasses import dataclass
from urllib import request


@dataclass
class BotRunnerClient:
    runner_base_url: str

    def chat(self, thread_id: str, user_id: str, text: str, model: str = "gemini-flash") -> dict:
        payload = json.dumps(
            {"thread_id": thread_id, "user_id": user_id, "text": text, "model": model}
        ).encode("utf-8")
        req = request.Request(
            f"{self.runner_base_url}/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=10) as res:
            return json.loads(res.read().decode("utf-8"))
