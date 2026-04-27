import pytest
import json
from pathlib import Path
from unittest.mock import patch, AsyncMock
from outo_agentcore.config.schema import AppConfig, ProviderConfig
from outo_agentcore.config.loader import save_config
from outo_agentcore.core.agent import Agent
from outo_agentcore.core.provider import Provider
from outo_agentcore.core.tool import BashTool
from outo_agentcore.core.router import Router
from outo_agentcore.core.runtime import Runtime
from outo_agentcore.core.context import ToolCall
from outo_agentcore.providers import LLMResponse, ProviderBackend
from outo_agentcore.sessions.manager import SessionManager
from outo_agentcore.parser.agent_md import parse_agent_md

class FakeBackend(ProviderBackend):
    def __init__(self, responses):
        self._responses = list(responses)
        self._call_count = 0
    
    async def call(self, context, tools, agent, provider):
        resp = self._responses[self._call_count]
        self._call_count += 1
        return resp

@pytest.mark.asyncio
async def test_full_flow_mock_llm(tmp_path):
    config_dir = tmp_path / ".outoac"
    config_dir.mkdir()
    
    agent_md = config_dir / "agents" / "main.md"
    agent_md.parent.mkdir(parents=True)
    agent_md.write_text("# Test Agent\n\nYou are a test agent.")
    
    config = AppConfig(
        providers={"default": ProviderConfig(kind="openai", model="gpt-4", api_key="test")},
        agents={"main": str(agent_md)},
        default_agent="main",
        skills_dir=str(config_dir / "skills")
    )
    save_config(config_dir / "config.json", config)
    
    parsed = parse_agent_md(agent_md)
    assert parsed["role"] == "Test Agent"
    assert "test agent" in parsed["instructions"]
    
    provider = Provider(name="default", kind="openai", api_key="test")
    agent = Agent(
        name="main",
        instructions=parsed["instructions"],
        model="gpt-4",
        provider="default",
        role=parsed["role"]
    )
    
    backend = FakeBackend([
        LLMResponse(tool_calls=[ToolCall(id="tc1", name="finish", arguments={"message": "Integration test passed"})])
    ])
    
    router = Router([agent], [BashTool()], [provider])
    with patch("outo_agentcore.core.router.get_backend", return_value=backend):
        runtime = Runtime(router)
        result = await runtime.execute("Test message", agent)
    
    assert result.output == "Integration test passed"
    
    sessions_dir = config_dir / "sessions"
    session_mgr = SessionManager(sessions_dir)
    session = session_mgr.create(agent_name="main")
    session.messages = [{"output": result.output}]
    session_mgr.save(session)
    
    loaded = session_mgr.load(session.session_id)
    assert loaded is not None
    assert loaded.messages[0]["output"] == "Integration test passed"

@pytest.mark.asyncio
async def test_multi_agent_flow():
    a1 = Agent(name="main", instructions="Main agent", model="gpt-4", provider="openai")
    a2 = Agent(name="researcher", instructions="Research agent", model="gpt-4", provider="openai")
    provider = Provider(name="openai", kind="openai")
    
    backend = FakeBackend([
        LLMResponse(tool_calls=[ToolCall(id="tc1", name="call_agent", arguments={"agent_name": "researcher", "message": "Find info"})]),
        LLMResponse(tool_calls=[ToolCall(id="tc2", name="finish", arguments={"message": "Research complete"})]),
        LLMResponse(tool_calls=[ToolCall(id="tc3", name="finish", arguments={"message": "Got: Research complete"})])
    ])
    
    router = Router([a1, a2], [BashTool()], [provider])
    with patch("outo_agentcore.core.router.get_backend", return_value=backend):
        runtime = Runtime(router)
        result = await runtime.execute("Research task", a1)
    
    assert "Research complete" in result.output
    assert len(result.messages) == 4

def test_session_continuation(tmp_path):
    session_mgr = SessionManager(tmp_path)
    
    session1 = session_mgr.create(agent_name="main")
    session1.messages = [
        {"type": "forward", "sender": "user", "receiver": "main", "content": "Hello"},
        {"type": "return", "sender": "main", "receiver": "user", "content": "Hi there"}
    ]
    session_mgr.save(session1)
    
    loaded = session_mgr.load(session1.session_id)
    assert loaded is not None
    assert len(loaded.messages) == 2
    assert loaded.messages[0]["content"] == "Hello"
    assert loaded.messages[1]["content"] == "Hi there"
