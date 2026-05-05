import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import agentouto
import pytest

from outo_agentcore.config.loader import save_config
from outo_agentcore.config.schema import AppConfig, ProviderConfig
from outo_agentcore.sessions.manager import SessionManager


class Args:
    def __init__(self, message="Hello", session=None, agent="main", max_messages=None, debug=False):
        self.message = message
        self.session = session
        self.agent = agent
        self.max_messages = max_messages
        self.debug = debug


@pytest.fixture
def setup_config(tmp_path):
    config_dir = tmp_path / ".outoac"
    config_dir.mkdir()

    agents_dir = config_dir / "agents"
    agents_dir.mkdir()

    main_md = agents_dir / "main.md"
    main_md.write_text("# Main Agent\n\nYou are the main coordinator.")

    config = AppConfig(
        providers={
            "default": ProviderConfig(
                kind="openai", base_url="http://localhost:11434/v1", api_key="test-key", default_model="llama4:scout"
            )
        },
        agents={"main": str(main_md)},
        default_agent="main",
        skills_dir=str(config_dir / "skills"),
    )
    save_config(config_dir / "config.json", config)

    return config_dir


@patch("agentouto.run")
def test_chat_basic(mock_run, setup_config, capsys):
    mock_run.return_value = agentouto.RunResult(
        output="Hello from agent",
        messages=[
            agentouto.Message(type="forward", sender="user", receiver="main", content="Hello"),
            agentouto.Message(type="return", sender="main", receiver="user", content="Hello from agent"),
        ],
    )

    from outo_agentcore.cli.cmd_chat import cmd_chat

    with patch.dict("os.environ", {"HOME": str(setup_config.parent)}):
        cmd_chat(Args(message="Hello"))

    captured = capsys.readouterr()
    assert "Hello from agent" in captured.out
    assert "Session:" in captured.out

    mock_run.assert_called_once()
    call_kwargs = mock_run.call_args.kwargs
    assert call_kwargs["message"] == "Hello"
    assert len(call_kwargs["starting_agents"]) == 1
    assert call_kwargs["starting_agents"][0].name == "main"
    assert call_kwargs["debug"] is False


@patch("agentouto.run")
def test_chat_with_session(mock_run, setup_config, capsys):
    session_mgr = SessionManager(setup_config / "sessions")
    session = session_mgr.create(agent_name="main")
    session.messages = [
        {"type": "forward", "sender": "user", "receiver": "main", "content": "Previous message", "call_id": "abc"},
        {"type": "return", "sender": "main", "receiver": "user", "content": "Previous response", "call_id": "def"},
    ]
    session_mgr.save(session)

    mock_run.return_value = agentouto.RunResult(
        output="Follow-up response",
        messages=[
            agentouto.Message(type="forward", sender="user", receiver="main", content="Previous message"),
            agentouto.Message(type="return", sender="main", receiver="user", content="Previous response"),
            agentouto.Message(type="forward", sender="user", receiver="main", content="Follow-up"),
            agentouto.Message(type="return", sender="main", receiver="user", content="Follow-up response"),
        ],
    )

    from outo_agentcore.cli.cmd_chat import cmd_chat

    with patch.dict("os.environ", {"HOME": str(setup_config.parent)}):
        cmd_chat(Args(message="Follow-up", session=session.session_id))

    captured = capsys.readouterr()
    assert "Follow-up response" in captured.out

    mock_run.assert_called_once()
    call_kwargs = mock_run.call_args.kwargs
    assert call_kwargs["history"] is not None
    assert len(call_kwargs["history"]) == 2


@patch("agentouto.run")
def test_chat_with_wiki(mock_run, setup_config, capsys):
    config_dir = setup_config
    config_path = config_dir / "config.json"
    data = json.loads(config_path.read_text())
    data["wiki"] = {
        "enabled": True,
        "wiki_path": str(config_dir / "wiki"),
        "provider": "default",
        "model": "",
        "api_key": "",
        "base_url": "",
        "max_output_tokens": 0,
        "debug": False,
    }
    config_path.write_text(json.dumps(data))

    mock_run.return_value = agentouto.RunResult(
        output="Wiki enabled",
        messages=[
            agentouto.Message(type="forward", sender="user", receiver="main", content="Hello"),
            agentouto.Message(type="return", sender="main", receiver="user", content="Wiki enabled"),
        ],
    )

    from outo_agentcore.cli.cmd_chat import cmd_chat

    with patch.dict("os.environ", {"HOME": str(config_dir.parent)}):
        cmd_chat(Args(message="Hello"))

    mock_run.assert_called_once()
    call_kwargs = mock_run.call_args.kwargs
    tools = call_kwargs["tools"]
    tool_names = [t.name for t in tools]
    assert "bash" in tool_names
    assert "wiki_record" in tool_names
    assert "wiki_search" in tool_names


@patch("agentouto.run")
def test_chat_skills_in_extra_instructions(mock_run, setup_config, capsys):
    config_dir = setup_config
    skills_dir = config_dir / "skills"
    skills_dir.mkdir()

    skill_dir = skills_dir / "test-skill"
    skill_dir.mkdir()
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text("---\nname: test-skill\ndescription: A test skill for testing.\n---\n# Instructions\nDo testing.")

    mock_run.return_value = agentouto.RunResult(
        output="Done",
        messages=[
            agentouto.Message(type="forward", sender="user", receiver="main", content="Hello"),
            agentouto.Message(type="return", sender="main", receiver="user", content="Done"),
        ],
    )

    from outo_agentcore.cli.cmd_chat import cmd_chat

    with patch.dict("os.environ", {"HOME": str(config_dir.parent)}):
        cmd_chat(Args(message="Hello"))

    mock_run.assert_called_once()
    call_kwargs = mock_run.call_args.kwargs
    assert call_kwargs["extra_instructions"] is not None
    assert "test-skill" in call_kwargs["extra_instructions"]
    assert call_kwargs["extra_instructions_scope"] == "all"


@patch("agentouto.run")
def test_chat_no_config(mock_run, capsys):
    from outo_agentcore.cli.cmd_chat import cmd_chat

    with patch.dict("os.environ", {"HOME": "/nonexistent_home_12345"}):
        cmd_chat(Args(message="Hello"))

    captured = capsys.readouterr()
    assert "No config found" in captured.out
    mock_run.assert_not_called()
