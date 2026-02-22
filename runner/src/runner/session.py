from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from typing import Dict, List


@dataclass
class SessionState:
    """In-memory chat session keyed by Discord thread_id."""

    thread_id: str
    user_id: str
    model: str = "gemini-flash"
    read_ok: bool = True
    write_ok: bool = False
    history: List[str] = field(default_factory=list)


class SessionStore:
    """Thread-safe in-memory session store for runner process."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._sessions: Dict[str, SessionState] = {}

    def get_or_create(self, thread_id: str, user_id: str, model: str = "gemini-flash") -> SessionState:
        with self._lock:
            state = self._sessions.get(thread_id)
            if state is None:
                state = SessionState(thread_id=thread_id, user_id=user_id, model=model)
                self._sessions[thread_id] = state
            return state

    def set_permissions(self, thread_id: str, read_ok: bool | None = None, write_ok: bool | None = None) -> SessionState:
        with self._lock:
            state = self._sessions[thread_id]
            if read_ok is not None:
                state.read_ok = read_ok
            if write_ok is not None:
                state.write_ok = write_ok
            return state
