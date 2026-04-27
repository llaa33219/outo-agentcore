import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from outo_agentcore.core.runtime import Runtime, RunResult
from outo_agentcore.core.router import Router
from outo_agentcore.core.agent import Agent
from outo_agentcore.core.provider import Provider
from outo_agentcore.core.tool import BashTool
from outo_agentcore.core.context import ToolCall
from outo_agentcore.providers import LLMResponse, ProviderBackend

class FakeBackend(ProviderBackend):
    def __init__(self, responses):
        self._responses = list(responses)
        self._call_count = 0
    
    async def call(self, context, tools, agent, provider):
        resp = self._responses[self._call_count]
        self._call_count += 1
        return resp

@pytest.mark.asyncio
async def test_execute_simple_finish():
    """Agent calls finish immediately."""
    agent = Agent(name="main", instructions="test", model="gpt-4", provider="openai")
    provider = Provider(name="openai", kind="openai")
    
    # Setup fake backend that returns finish tool call
    backend = FakeBackend([
        LLMResponse(tool_calls=[ToolCall(id="tc1", name="finish", arguments={"message": "Hello!"})])
    ])
    
    router = Router([agent], [BashTool()], [provider])
    # Patch get_backend to return our fake
    with patch("outo_agentcore.core.router.get_backend", return_value=backend):
        runtime = Runtime(router)
        result = await runtime.execute("Hi", agent)
    
    assert result.output == "Hello!"
    assert len(result.messages) == 2  # forward + return

@pytest.mark.asyncio
async def test_execute_text_nudge_then_finish():
    """Agent responds with text, gets nudged, then finishes."""
    agent = Agent(name="main", instructions="test", model="gpt-4", provider="openai")
    provider = Provider(name="openai", kind="openai")
    
    backend = FakeBackend([
        LLMResponse(content="I'll help"),  # Text response - should nudge
        LLMResponse(tool_calls=[ToolCall(id="tc1", name="finish", arguments={"message": "Done"})])
    ])
    
    router = Router([agent], [BashTool()], [provider])
    with patch("outo_agentcore.core.router.get_backend", return_value=backend):
        runtime = Runtime(router)
        result = await runtime.execute("Help me", agent)
    
    assert result.output == "Done"

@pytest.mark.asyncio
async def test_execute_bash_tool():
    """Agent calls bash tool, gets result, then finishes."""
    agent = Agent(name="main", instructions="test", model="gpt-4", provider="openai")
    provider = Provider(name="openai", kind="openai")
    
    backend = FakeBackend([
        LLMResponse(tool_calls=[ToolCall(id="tc1", name="bash", arguments={"command": "echo hello"})]),
        LLMResponse(tool_calls=[ToolCall(id="tc2", name="finish", arguments={"message": "Command ran"})])
    ])
    
    router = Router([agent], [BashTool()], [provider])
    with patch("outo_agentcore.core.router.get_backend", return_value=backend):
        runtime = Runtime(router)
        result = await runtime.execute("Run echo", agent)
    
    assert result.output == "Command ran"

@pytest.mark.asyncio
async def test_execute_call_agent():
    a1 = Agent(name="main", instructions="Main agent", model="gpt-4", provider="openai")
    a2 = Agent(name="worker", instructions="Worker", model="gpt-4", provider="openai")
    provider = Provider(name="openai", kind="openai")
    
    backend = FakeBackend([
        LLMResponse(tool_calls=[ToolCall(id="tc1", name="call_agent", arguments={"agent_name": "worker", "message": "Do work"})]),
        LLMResponse(tool_calls=[ToolCall(id="tc2", name="finish", arguments={"message": "Worker done"})]),
        LLMResponse(tool_calls=[ToolCall(id="tc3", name="finish", arguments={"message": "Main got: Worker done"})])
    ])
    
    router = Router([a1, a2], [BashTool()], [provider])
    with patch("outo_agentcore.core.router.get_backend", return_value=backend):
        runtime = Runtime(router)
        result = await runtime.execute("Start work", a1)
    
    assert "Worker done" in result.output

@pytest.mark.asyncio
async def test_execute_nested_call_agent():
    a1 = Agent(name="main", instructions="Main", model="gpt-4", provider="openai")
    a2 = Agent(name="middle", instructions="Middle", model="gpt-4", provider="openai")
    a3 = Agent(name="leaf", instructions="Leaf", model="gpt-4", provider="openai")
    provider = Provider(name="openai", kind="openai")
    
    backend = FakeBackend([
        LLMResponse(tool_calls=[ToolCall(id="tc1", name="call_agent", arguments={"agent_name": "middle", "message": "Go"})]),
        LLMResponse(tool_calls=[ToolCall(id="tc2", name="call_agent", arguments={"agent_name": "leaf", "message": "Work"})]),
        LLMResponse(tool_calls=[ToolCall(id="tc3", name="finish", arguments={"message": "Leaf done"})]),
        LLMResponse(tool_calls=[ToolCall(id="tc4", name="finish", arguments={"message": "Middle got Leaf done"})]),
        LLMResponse(tool_calls=[ToolCall(id="tc5", name="finish", arguments={"message": "Main got Middle got Leaf done"})])
    ])
    
    router = Router([a1, a2, a3], [BashTool()], [provider])
    with patch("outo_agentcore.core.router.get_backend", return_value=backend):
        runtime = Runtime(router)
        result = await runtime.execute("Start", a1)
    
    assert "Leaf done" in result.output

@pytest.mark.asyncio
async def test_execute_unknown_agent_raises():
    """call_agent with bad name raises RoutingError."""
    agent = Agent(name="main", instructions="test", model="gpt-4", provider="openai")
    provider = Provider(name="openai", kind="openai")
    
    backend = FakeBackend([
        LLMResponse(tool_calls=[ToolCall(id="tc1", name="call_agent", arguments={"agent_name": "nonexistent", "message": "Hi"})])
    ])
    
    router = Router([agent], [BashTool()], [provider])
    with patch("outo_agentcore.core.router.get_backend", return_value=backend):
        runtime = Runtime(router)
        with pytest.raises(Exception):  # Should raise RoutingError
            await runtime.execute("Call bad agent", agent)

@pytest.mark.asyncio
async def test_messages_tracking():
    """Verify messages list has forward/return pairs."""
    agent = Agent(name="main", instructions="test", model="gpt-4", provider="openai")
    provider = Provider(name="openai", kind="openai")
    
    backend = FakeBackend([
        LLMResponse(tool_calls=[ToolCall(id="tc1", name="finish", arguments={"message": "Done"})])
    ])
    
    router = Router([agent], [BashTool()], [provider])
    with patch("outo_agentcore.core.router.get_backend", return_value=backend):
        runtime = Runtime(router)
        result = await runtime.execute("Test", agent)
    
    assert result.messages[0].type == "forward"
    assert result.messages[0].sender == "user"
    assert result.messages[0].receiver == "main"
    assert result.messages[1].type == "return"
    assert result.messages[1].sender == "main"
    assert result.messages[1].receiver == "user"

@pytest.mark.asyncio
async def test_run_result_output():
    """Verify RunResult.output matches finish message."""
    agent = Agent(name="main", instructions="test", model="gpt-4", provider="openai")
    provider = Provider(name="openai", kind="openai")
    
    backend = FakeBackend([
        LLMResponse(tool_calls=[ToolCall(id="tc1", name="finish", arguments={"message": "Final answer"})])
    ])
    
    router = Router([agent], [BashTool()], [provider])
    with patch("outo_agentcore.core.router.get_backend", return_value=backend):
        runtime = Runtime(router)
        result = await runtime.execute("Question", agent)
    
    assert result.output == "Final answer"
