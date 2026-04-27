import pytest
from pathlib import Path
from outo_agentcore.sessions.manager import SessionManager, SessionData


def test_create_new_session(tmp_path):
    mgr = SessionManager(tmp_path)
    session = mgr.create(agent_name="main")
    assert session.session_id
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
