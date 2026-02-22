import sqlite3
from pathlib import Path

from db.init_db import init_db


def test_init_db_creates_tables(tmp_path: Path) -> None:
    db_file = tmp_path / "db.sqlite3"
    schema = Path("db/schema.sql")

    init_db(db_file, schema)

    with sqlite3.connect(db_file) as conn:
        names = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}

    assert {"users", "channels", "threads", "session_events"}.issubset(names)
