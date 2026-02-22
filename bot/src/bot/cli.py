from __future__ import annotations

import argparse

from .client import BotRunnerClient


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Minimal bot-to-runner client")
    parser.add_argument("--runner", default="http://127.0.0.1:8000")

    # Legacy (main branch style): no subcommand, direct chat args.
    parser.add_argument("--thread-id")
    parser.add_argument("--user-id")
    parser.add_argument("--text")
    parser.add_argument("--model", default="gemini-flash")

    sub = parser.add_subparsers(dest="command")

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
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    client = BotRunnerClient(args.runner)

    if args.command == "permissions":
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
        return

    # chat subcommand or legacy mode.
    if not args.thread_id or not args.user_id or not args.text:
        parser.error("chat requires --thread-id, --user-id, and --text")
    result = client.chat(args.thread_id, args.user_id, args.text, model=args.model)
    print(result)


if __name__ == "__main__":
    main()
