import pytest
from pathlib import Path
from outo_agentcore.sessions.manager import SessionManager, SessionData, SessionLoadError


def test_create_new_session(tmp_path):
    mgr = SessionManager(tmp_path)
    session = mgr.create(agent_name="main")
    assert session.session_id
    assert session.created_at
    assert session.messages == []
    assert session.agent_name == "main"


def test_create_session_with_specific_id(tmp_path):
    mgr = SessionManager(tmp_path)
    session = mgr.create(agent_name="main", session_id="custom-id-123")
    assert session.session_id == "custom-id-123"
    assert session.created_at
    assert session.messages == []
    assert session.agent_name == "main"


def test_save_and_load_roundtrip(tmp_path):
    mgr = SessionManager(tmp_path)
    session = mgr.create(agent_name="main")
    session.messages = [{"type": "forward", "sender": "user", "receiver": "main", "content": "hello"}]
    mgr.save(session)

    loaded = mgr.load(session.session_id)
    assert loaded is not None
    assert loaded.session_id == session.session_id
    assert len(loaded.messages) == 1
    assert loaded.messages[0]["content"] == "hello"


def test_load_nonexistent_returns_none(tmp_path):
    mgr = SessionManager(tmp_path)
    assert mgr.load("nonexistent-id") is None


def test_load_empty_file_raises_error(tmp_path):
    mgr = SessionManager(tmp_path)
    session_file = tmp_path / "empty-session.json"
    session_file.write_text("")
    
    with pytest.raises(SessionLoadError, match="corrupted"):
        mgr.load("empty-session")


def test_load_corrupted_json_raises_error(tmp_path):
    mgr = SessionManager(tmp_path)
    session_file = tmp_path / "corrupted-session.json"
    session_file.write_text("{invalid json content")
    
    with pytest.raises(SessionLoadError, match="corrupted"):
        mgr.load("corrupted-session")


def test_load_invalid_format_raises_error(tmp_path):
    mgr = SessionManager(tmp_path)
    session_file = tmp_path / "bad-format-session.json"
    session_file.write_text('{"wrong_field": "value"}')
    
    with pytest.raises(SessionLoadError, match="invalid format"):
        mgr.load("bad-format-session")


def test_list_sessions(tmp_path):
    mgr = SessionManager(tmp_path)
    s1 = mgr.create(agent_name="main")
    s2 = mgr.create(agent_name="researcher")
    mgr.save(s1)
    mgr.save(s2)

    sessions = mgr.list_sessions()
    assert len(sessions) == 2


def test_list_sessions_sorted_by_date(tmp_path):
    mgr = SessionManager(tmp_path)
    s1 = mgr.create(agent_name="main")
    s2 = mgr.create(agent_name="main")
    mgr.save(s1)
    mgr.save(s2)

    sessions = mgr.list_sessions()
    assert sessions[0].created_at >= sessions[1].created_at


def test_save_overwrites_existing(tmp_path):
    mgr = SessionManager(tmp_path)
    session = mgr.create(agent_name="main")
    mgr.save(session)

    session.messages = [{"content": "updated"}]
    mgr.save(session)

    loaded = mgr.load(session.session_id)
    assert loaded.messages[0]["content"] == "updated"
