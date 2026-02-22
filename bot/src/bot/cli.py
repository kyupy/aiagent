from __future__ import annotations

import argparse

from .client import BotRunnerClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal bot-to-runner client")
    parser.add_argument("--runner", default="http://127.0.0.1:8000")

    sub = parser.add_subparsers(dest="command", required=True)

    chat = sub.add_parser("chat")
    chat.add_argument("--thread-id", required=True)
    chat.add_argument("--user-id", required=True)
    chat.add_argument("--text", required=True)
    chat.add_argument("--model", default="gemini-flash")

    perms = sub.add_parser("permissions")
    perms.add_argument("--thread-id", required=True)
    perms.add_argument("--user-id", required=True)
    perms.add_argument("--model", default="gemini-flash")
    perms.add_argument("--read-ok", choices=["true", "false"])
    perms.add_argument("--write-ok", choices=["true", "false"])

    args = parser.parse_args()
    client = BotRunnerClient(args.runner)

    if args.command == "chat":
        result = client.chat(args.thread_id, args.user_id, args.text, model=args.model)
    else:
        read_ok = None if args.read_ok is None else args.read_ok == "true"
        write_ok = None if args.write_ok is None else args.write_ok == "true"
        result = client.set_permissions(
            thread_id=args.thread_id,
            user_id=args.user_id,
            read_ok=read_ok,
            write_ok=write_ok,
            model=args.model,
        )
    print(result)


if __name__ == "__main__":
    main()
