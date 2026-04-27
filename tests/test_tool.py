import pytest
from outo_agentcore.core.tool import ToolResult

def test_basic():
    result = ToolResult(content="command output here")
    assert result.content == "command output here"

def test_content_required():
    with pytest.raises(TypeError):
        ToolResult()