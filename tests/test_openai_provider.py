import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from outo_agentcore.providers.openai import OpenAIBackend, _build_messages, _build_tools, _parse_tool_arguments
from outo_agentcore.core.context import Context, ToolCall
from outo_agentcore.core.agent import Agent
from outo_agentcore.core.provider import Provider

def test_build_messages_user_only():
    ctx = Context(system_prompt="test")
    ctx.add_user("hello")
    messages = _build_messages(ctx)
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "hello"

def test_build_messages_with_system():
    ctx = Context(system_prompt="You are helpful")
    messages = _build_messages(ctx)
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "You are helpful"

def test_build_messages_tool_calls():
    ctx = Context(system_prompt="test")
    tc = ToolCall(id="tc1", name="bash", arguments={"command": "ls"})
    ctx.add_assistant_tool_calls([tc], content="Running")
    messages = _build_messages(ctx)
    assert len(messages) == 2
    assert messages[1]["role"] == "assistant"
    assert messages[1]["tool_calls"][0]["id"] == "tc1"

def test_build_messages_tool_results():
    ctx = Context(system_prompt="test")
    ctx.add_tool_result("tc1", "bash", "output")
    messages = _build_messages(ctx)
    assert len(messages) == 2
    assert messages[1]["role"] == "tool"
    assert messages[1]["tool_call_id"] == "tc1"

def test_build_tools_conversion():
    tools = [{
        "name": "bash",
        "description": "Execute command",
        "parameters": {"type": "object", "properties": {"command": {"type": "string"}}}
    }]
    result = _build_tools(tools)
    assert result[0]["type"] == "function"
    assert result[0]["function"]["name"] == "bash"

def test_parse_tool_arguments_valid():
    assert _parse_tool_arguments('{"key": "value"}') == {"key": "value"}

def test_parse_tool_arguments_none():
    assert _parse_tool_arguments(None) == {}

def test_parse_tool_arguments_empty():
    assert _parse_tool_arguments("") == {}

@pytest.mark.asyncio
async def test_call_integration():
    backend = OpenAIBackend()
    assert backend is not None
