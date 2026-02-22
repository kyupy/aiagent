from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from threading import RLock
from typing import Dict, List


@dataclass
class SessionState:
    """Chat session keyed by Discord thread_id."""

    thread_id: str
    user_id: str
    model: str = "gemini-flash"
    read_ok: bool = True
    write_ok: bool = False
    history: List[str] = field(default_factory=list)


class SessionStore:
    """Thread-safe session store with SQLite snapshot persistence."""

    def __init__(self, db_path: str = "data/db.sqlite3") -> None:
        self._lock = RLock()
        self._sessions: Dict[str, SessionState] = {}
        self._db_path = Path(db_path)
        self._ensure_db()

    def _ensure_db(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS threads (
                  thread_id TEXT PRIMARY KEY,
                  user_id TEXT NOT NULL,
                  model TEXT DEFAULT 'gemini-flash',
                  read_ok INTEGER DEFAULT 1,
                  write_ok INTEGER DEFAULT 0
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS session_events (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  thread_id TEXT NOT NULL,
                  role TEXT NOT NULL,
                  content TEXT NOT NULL,
                  created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def _load_from_db(self, thread_id: str) -> SessionState | None:
        with sqlite3.connect(self._db_path) as conn:
            row = conn.execute(
                "SELECT thread_id, user_id, model, read_ok, write_ok FROM threads WHERE thread_id = ?",
                (thread_id,),
            ).fetchone()
            if row is None:
                return None

            events = conn.execute(
                "SELECT role, content FROM session_events WHERE thread_id = ? ORDER BY id",
                (thread_id,),
            ).fetchall()

        history = [f"{role}:{content}" for role, content in events]
        return SessionState(
            thread_id=row[0],
            user_id=row[1],
            model=row[2],
            read_ok=bool(row[3]),
            write_ok=bool(row[4]),
            history=history,
        )

    def _upsert_thread(self, state: SessionState) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                INSERT INTO threads(thread_id, user_id, model, read_ok, write_ok)
                VALUES(?, ?, ?, ?, ?)
                ON CONFLICT(thread_id) DO UPDATE SET
                  user_id = excluded.user_id,
                  model = excluded.model,
                  read_ok = excluded.read_ok,
                  write_ok = excluded.write_ok
                """,
                (state.thread_id, state.user_id, state.model, int(state.read_ok), int(state.write_ok)),
            )
            conn.commit()

    def append_event(self, thread_id: str, role: str, content: str) -> None:
        with self._lock:
            state = self._sessions[thread_id]
            state.history.append(f"{role}:{content}")
            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    "INSERT INTO session_events(thread_id, role, content) VALUES(?, ?, ?)",
                    (thread_id, role, content),
                )
                conn.commit()

    def get_or_create(self, thread_id: str, user_id: str, model: str = "gemini-flash") -> SessionState:
        with self._lock:
            state = self._sessions.get(thread_id)
            if state is None:
                state = self._load_from_db(thread_id)
                if state is None:
                    state = SessionState(thread_id=thread_id, user_id=user_id, model=model)
                    self._upsert_thread(state)
                self._sessions[thread_id] = state
            return state

    def set_permissions(
        self,
        thread_id: str,
        user_id: str,
        model: str = "gemini-flash",
        read_ok: bool | None = None,
        write_ok: bool | None = None,
    ) -> SessionState:
        with self._lock:
            state = self.get_or_create(thread_id=thread_id, user_id=user_id, model=model)
            if read_ok is not None:
                state.read_ok = read_ok
            if write_ok is not None:
                state.write_ok = write_ok
            self._upsert_thread(state)
            return state
