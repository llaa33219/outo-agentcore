import pytest
import json
from pathlib import Path
from outo_agentcore.config.schema import AppConfig, ProviderConfig
from outo_agentcore.config.loader import load_config, save_config


def test_load_valid_config(tmp_path):
    config_data = {
        "providers": {
            "default": {
                "kind": "openai",
                "base_url": "https://api.openai.com/v1",
                "api_key": "sk-xxx",
                "default_model": "gpt-4o"
            }
        },
        "agents": {"main": "~/agents/main.md"},
        "default_agent": "main",
        "skills_dir": "~/.outoac/skills/"
    }
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config_data))

    config = load_config(config_file)
    assert "default" in config.providers
    assert config.providers["default"].kind == "openai"
    assert config.providers["default"].default_model == "gpt-4o"
    assert config.agents["main"] == "~/agents/main.md"
    assert config.default_agent == "main"


def test_save_and_reload(tmp_path):
    config = AppConfig(
        providers={"test": ProviderConfig(kind="openai", default_model="gpt-4")},
        agents={"main": "/path/to/main.md"},
        default_agent="main",
        skills_dir="/skills"
    )
    config_file = tmp_path / "config.json"
    save_config(config_file, config)

    loaded = load_config(config_file)
    assert loaded.providers["test"].default_model == "gpt-4"
    assert loaded.agents["main"] == "/path/to/main.md"
    assert loaded.default_agent == "main"


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "nonexistent.json")


def test_load_invalid_json_raises(tmp_path):
    config_file = tmp_path / "bad.json"
    config_file.write_text("not json{{{")
    with pytest.raises(json.JSONDecodeError):
        load_config(config_file)


def test_default_skills_dir():
    config = AppConfig(providers={}, agents={})
    assert config.skills_dir == "~/.outoac/skills/"
    assert config.default_agent == "main"


def test_provider_config_defaults():
    pc = ProviderConfig()
    assert pc.kind == "openai"
    assert pc.base_url == ""
    assert pc.api_key == ""
    assert pc.default_model == ""
