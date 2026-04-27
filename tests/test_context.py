import pytest
from outo_agentcore.core.context import Context, ContextMessage, ToolCall

def test_initial_state():
    ctx = Context(system_prompt="You are helpful")
    assert ctx.system_prompt == "You are helpful"
    assert ctx.messages == []

def test_add_user():
    ctx = Context(system_prompt="test")
    ctx.add_user("hello")
    assert len(ctx.messages) == 1
    assert ctx.messages[0].role == "user"
    assert ctx.messages[0].content == "hello"

def test_add_assistant_text():
    ctx = Context(system_prompt="test")
    ctx.add_assistant_text("I can help")
    assert len(ctx.messages) == 1
    assert ctx.messages[0].role == "assistant"
    assert ctx.messages[0].content == "I can help"

def test_add_assistant_tool_calls():
    ctx = Context(system_prompt="test")
    tc = ToolCall(id="tc1", name="bash", arguments={"command": "ls"})
    ctx.add_assistant_tool_calls([tc], content="Running command")
    assert len(ctx.messages) == 1
    assert ctx.messages[0].role == "assistant"
    assert ctx.messages[0].content == "Running command"
    assert len(ctx.messages[0].tool_calls) == 1
    assert ctx.messages[0].tool_calls[0].id == "tc1"

def test_add_tool_result():
    ctx = Context(system_prompt="test")
    ctx.add_tool_result("tc1", "bash", "file1.txt\nfile2.txt")
    assert len(ctx.messages) == 1
    assert ctx.messages[0].role == "tool"
    assert ctx.messages[0].tool_call_id == "tc1"
    assert ctx.messages[0].tool_name == "bash"
    assert ctx.messages[0].content == "file1.txt\nfile2.txt"

def test_messages_returns_copy():
    ctx = Context(system_prompt="test")
    ctx.add_user("hello")
    msgs = ctx.messages
    msgs.clear()
    assert len(ctx.messages) == 1