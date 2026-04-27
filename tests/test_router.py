import pytest
from outo_agentcore.core.router import Router, CALL_AGENT, FINISH
from outo_agentcore.core.agent import Agent
from outo_agentcore.core.provider import Provider
from outo_agentcore.core.tool import BashTool
from outo_agentcore.core.context import Context
from outo_agentcore.providers import LLMResponse

def test_agent_registration():
    agents = [Agent(name="main", instructions="test", model="gpt-4", provider="openai")]
    providers = [Provider(name="openai", kind="openai", api_key="sk-xxx")]
    tools = [BashTool()]
    router = Router(agents, tools, providers)
    assert router.get_agent("main") is not None

def test_get_agent():
    agent = Agent(name="main", instructions="test", model="gpt-4", provider="openai")
    router = Router([agent], [BashTool()], [Provider(name="openai", kind="openai")])
    assert router.get_agent("main").name == "main"

def test_get_agent_unknown_raises():
    router = Router([], [], [])
    with pytest.raises(Exception):
        router.get_agent("nonexistent")

def test_provider_registration():
    provider = Provider(name="openai", kind="openai", api_key="sk-xxx")
    router = Router([], [], [provider])
    assert router.get_provider("openai") is not None

def test_system_prompt_basic():
    agent = Agent(name="main", instructions="Be helpful", model="gpt-4", provider="openai", role="Assistant")
    router = Router([agent], [BashTool()], [Provider(name="openai", kind="openai")])
    prompt = router.build_system_prompt(agent)
    assert "main" in prompt
    assert "Assistant" in prompt
    assert "Be helpful" in prompt

def test_system_prompt_with_caller():
    agent = Agent(name="worker", instructions="Work", model="gpt-4", provider="openai")
    router = Router([agent], [BashTool()], [Provider(name="openai", kind="openai")])
    prompt = router.build_system_prompt(agent, caller="main")
    assert "INVOKED BY" in prompt
    assert "main" in prompt

def test_system_prompt_lists_other_agents():
    a1 = Agent(name="main", instructions="Main", model="gpt-4", provider="openai")
    a2 = Agent(name="worker", instructions="Work", model="gpt-4", provider="openai")
    router = Router([a1, a2], [BashTool()], [Provider(name="openai", kind="openai")])
    prompt = router.build_system_prompt(a1)
    assert "worker" in prompt
    assert "main" not in prompt or "You are" in prompt  # Self not in available list

def test_system_prompt_no_agents():
    agent = Agent(name="solo", instructions="Alone", model="gpt-4", provider="openai")
    router = Router([agent], [BashTool()], [Provider(name="openai", kind="openai")])
    prompt = router.build_system_prompt(agent)
    assert "Available agents" not in prompt or "No other agents" in prompt

def test_tool_schemas_contains_bash():
    agent = Agent(name="main", instructions="test", model="gpt-4", provider="openai")
    router = Router([agent], [BashTool()], [Provider(name="openai", kind="openai")])
    schemas = router.build_tool_schemas("main")
    names = [s["name"] for s in schemas]
    assert "bash" in names

def test_tool_schemas_contains_call_agent():
    a1 = Agent(name="main", instructions="test", model="gpt-4", provider="openai")
    a2 = Agent(name="worker", instructions="test", model="gpt-4", provider="openai")
    router = Router([a1, a2], [BashTool()], [Provider(name="openai", kind="openai")])
    schemas = router.build_tool_schemas("main")
    names = [s["name"] for s in schemas]
    assert "call_agent" in names

def test_tool_schemas_contains_finish():
    agent = Agent(name="main", instructions="test", model="gpt-4", provider="openai")
    router = Router([agent], [BashTool()], [Provider(name="openai", kind="openai")])
    schemas = router.build_tool_schemas("main")
    names = [s["name"] for s in schemas]
    assert "finish" in names

def test_constants():
    assert CALL_AGENT == "call_agent"
    assert FINISH == "finish"
