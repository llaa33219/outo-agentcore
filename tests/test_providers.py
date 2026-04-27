import pytest
from outo_agentcore.providers import ProviderBackend, LLMResponse, Usage, get_backend
from outo_agentcore.core.context import Context, ToolCall
from outo_agentcore.core.agent import Agent
from outo_agentcore.core.provider import Provider

def test_usage_add():
    u1 = Usage(input_tokens=100, output_tokens=50)
    u2 = Usage(input_tokens=200, output_tokens=100)
    u3 = u1 + u2
    assert u3.input_tokens == 300
    assert u3.output_tokens == 150

def test_usage_iadd():
    u1 = Usage(input_tokens=100, output_tokens=50)
    u1 += Usage(input_tokens=200, output_tokens=100)
    assert u1.input_tokens == 300
    assert u1.output_tokens == 150

def test_usage_total_tokens():
    u = Usage(input_tokens=100, output_tokens=50)
    assert u.total_tokens == 150

def test_llm_response_defaults():
    resp = LLMResponse()
    assert resp.content is None
    assert resp.tool_calls == []
    assert resp.usage is None

def test_get_backend_openai():
    backend = get_backend("openai")
    assert isinstance(backend, ProviderBackend)

def test_get_backend_unknown_raises():
    with pytest.raises(ValueError):
        get_backend("unknown")