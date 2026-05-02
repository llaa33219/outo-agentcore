import pytest
from outo_agentcore.config.schema import WikiSettings
from outo_agentcore.core.wiki_tools import WikiRecordTool, WikiSearchTool


def test_wiki_record_schema_structure():
    settings = WikiSettings(enabled=True, wiki_path="/tmp/test_wiki")
    tool = WikiRecordTool(settings)
    schema = tool.to_schema()
    assert schema["name"] == "wiki_record"
    assert "description" in schema
    assert "content" in schema["parameters"]["properties"]
    assert "content" in schema["parameters"]["required"]


def test_wiki_search_schema_structure():
    settings = WikiSettings(enabled=True, wiki_path="/tmp/test_wiki")
    tool = WikiSearchTool(settings)
    schema = tool.to_schema()
    assert schema["name"] == "wiki_search"
    assert "description" in schema
    assert "query" in schema["parameters"]["properties"]
    assert "query" in schema["parameters"]["required"]


def test_wiki_record_tool_name():
    settings = WikiSettings(enabled=True)
    tool = WikiRecordTool(settings)
    assert tool.name == "wiki_record"


def test_wiki_search_tool_name():
    settings = WikiSettings(enabled=True)
    tool = WikiSearchTool(settings)
    assert tool.name == "wiki_search"


def test_wiki_settings_defaults():
    settings = WikiSettings()
    assert settings.enabled is False
    assert settings.wiki_path == "~/.outoac/wiki/"
    assert settings.provider == "openai"
    assert settings.model == ""
    assert settings.debug is False
