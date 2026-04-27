import pytest
from outo_agentcore.core.provider import Provider

def test_basic():
    provider = Provider(name="openai", kind="openai", api_key="sk-xxx")
    assert provider.name == "openai"
    assert provider.kind == "openai"
    assert provider.api_key == "sk-xxx"
    assert provider.base_url is None

def test_with_base_url():
    provider = Provider(
        name="local",
        kind="openai",
        api_key="not-needed",
        base_url="http://localhost:11434/v1"
    )
    assert provider.base_url == "http://localhost:11434/v1"

def test_default_api_key_empty():
    provider = Provider(name="test", kind="openai")
    assert provider.api_key == ""