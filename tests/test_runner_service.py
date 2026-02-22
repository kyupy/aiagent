from runner.service import ChatRequest, RunnerService


def test_write_permission_flow() -> None:
    service = RunnerService()

    denied = service.handle_chat(ChatRequest(thread_id="t1", user_id="u1", text="[WRITE] update note"))
    assert denied.kind == "need_permission"

    service.grant_write_permission("t1")
    allowed = service.handle_chat(ChatRequest(thread_id="t1", user_id="u1", text="[WRITE] update note"))
    assert allowed.kind == "message"


def test_session_persists_by_thread() -> None:
    service = RunnerService()

    first = service.handle_chat(ChatRequest(thread_id="thread-x", user_id="u1", text="hello"))
    second = service.handle_chat(ChatRequest(thread_id="thread-x", user_id="u1", text="again"))

    assert first.thread_id == second.thread_id == "thread-x"
