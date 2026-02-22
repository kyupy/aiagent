from pathlib import Path

from runner.service import ChatRequest, RunnerService
from runner.session import SessionStore


def test_write_permission_flow(tmp_path: Path) -> None:
    store = SessionStore(db_path=str(tmp_path / "db.sqlite3"))
    service = RunnerService(session_store=store)

    denied = service.handle_chat(ChatRequest(thread_id="t1", user_id="u1", text="[WRITE] update note"))
    assert denied.kind == "need_permission"

    service.update_permissions(thread_id="t1", user_id="u1", write_ok=True)
    allowed = service.handle_chat(ChatRequest(thread_id="t1", user_id="u1", text="[WRITE] update note"))
    assert allowed.kind == "message"


def test_session_persists_after_restart(tmp_path: Path) -> None:
    db_file = tmp_path / "db.sqlite3"

    store1 = SessionStore(db_path=str(db_file))
    service1 = RunnerService(session_store=store1)
    service1.handle_chat(ChatRequest(thread_id="thread-x", user_id="u1", text="hello"))

    store2 = SessionStore(db_path=str(db_file))
    service2 = RunnerService(session_store=store2)
    service2.handle_chat(ChatRequest(thread_id="thread-x", user_id="u1", text="again"))

    state = store2.get_or_create(thread_id="thread-x", user_id="u1")
    assert len(state.history) == 4
    assert state.history[0] == "user:hello"
    assert state.history[-1].startswith("assistant:echo")
