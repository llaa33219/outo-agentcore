import pytest
from outo_agentcore.core.agent import Agent

def test_defaults():
    agent = Agent(name="test", instructions="do stuff", model="gpt-4", provider="openai")
    assert agent.name == "test"
    assert agent.instructions == "do stuff"
    assert agent.model == "gpt-4"
    assert agent.provider == "openai"
    assert agent.role is None
    assert agent.max_output_tokens is None
    assert agent.temperature == 1.0
    assert agent.context_window is None

def test_custom_values():
    agent = Agent(
        name="researcher",
        instructions="Research things",
        model="gpt-4o",
        provider="default",
        role="Research expert",
        max_output_tokens=4096,
        temperature=0.7,
        context_window=128000
    )
    assert agent.role == "Research expert"
    assert agent.max_output_tokens == 4096
    assert agent.temperature == 0.7
    assert agent.context_window == 128000

def test_name_required():
    with pytest.raises(TypeError):
        Agent(instructions="x", model="y", provider="z")