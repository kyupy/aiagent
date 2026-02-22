from __future__ import annotations

from dataclasses import dataclass

from .session import SessionStore


@dataclass
class ChatRequest:
    thread_id: str
    user_id: str
    text: str
    model: str = "gemini-flash"


@dataclass
class ChatResponse:
    kind: str
    message: str
    thread_id: str


class RunnerService:
    """Minimal runner logic with resumable in-memory session state."""

    def __init__(self, session_store: SessionStore | None = None) -> None:
        self.session_store = session_store or SessionStore()

    def handle_chat(self, req: ChatRequest) -> ChatResponse:
        state = self.session_store.get_or_create(req.thread_id, req.user_id, req.model)

        if not state.read_ok:
            return ChatResponse(
                kind="need_permission",
                message="read permission is required for this thread",
                thread_id=state.thread_id,
            )

        state.history.append(f"user:{req.text}")

        # Minimal permission contract for writes.
        if "[WRITE]" in req.text and not state.write_ok:
            return ChatResponse(
                kind="need_permission",
                message="write permission is required for this operation",
                thread_id=state.thread_id,
            )

        answer = f"echo({state.model}): {req.text}"
        state.history.append(f"assistant:{answer}")
        return ChatResponse(kind="message", message=answer, thread_id=state.thread_id)

    def grant_write_permission(self, thread_id: str) -> None:
        self.session_store.set_permissions(thread_id, write_ok=True)
