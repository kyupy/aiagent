from __future__ import annotations

import argparse

from .client import BotRunnerClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal bot-to-runner chat client")
    parser.add_argument("--runner", default="http://127.0.0.1:8000")
    parser.add_argument("--thread-id", required=True)
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--text", required=True)
    args = parser.parse_args()

    client = BotRunnerClient(args.runner)
    result = client.chat(args.thread_id, args.user_id, args.text)
    print(result)


if __name__ == "__main__":
    main()
