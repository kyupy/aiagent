from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def init_db(db_path: Path, schema_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    schema = schema_path.read_text(encoding="utf-8")
    with sqlite3.connect(db_path) as conn:
        conn.executescript(schema)
        conn.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize SQLite schema")
    parser.add_argument("--db", default="data/db.sqlite3")
    parser.add_argument("--schema", default="db/schema.sql")
    args = parser.parse_args()
    init_db(Path(args.db), Path(args.schema))
    print(f"initialized {args.db}")


if __name__ == "__main__":
    main()
