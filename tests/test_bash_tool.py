import pytest
from outo_agentcore.core.tool import BashTool, ToolResult


def test_schema_structure():
    tool = BashTool()
    schema = tool.to_schema()
    assert schema["name"] == "bash"
    assert "description" in schema
    assert "command" in schema["parameters"]["properties"]
    assert "command" in schema["parameters"]["required"]


@pytest.mark.asyncio
async def test_execute_echo():
    tool = BashTool()
    result = await tool.execute(command="echo hello")
    assert "hello" in result.content


@pytest.mark.asyncio
async def test_execute_stderr():
    tool = BashTool()
    result = await tool.execute(command="echo error >&2")
    assert "error" in result.content


@pytest.mark.asyncio
async def test_execute_multiline():
    tool = BashTool()
    result = await tool.execute(command="echo line1; echo line2")
    assert "line1" in result.content
    assert "line2" in result.content


@pytest.mark.asyncio
async def test_execute_empty_command():
    tool = BashTool()
    result = await tool.execute(command="")
    assert result.content == "" or result.content is not None
