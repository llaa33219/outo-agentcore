import json
from pathlib import Path
from outo_agentcore.config.schema import AppConfig, ProviderConfig, WikiSettings


def load_config(path: Path) -> AppConfig:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path) as f:
        data = json.load(f)

    providers = {}
    for name, pc_data in data.get("providers", {}).items():
        providers[name] = ProviderConfig(**pc_data)

    wiki_data = data.get("wiki")
    wiki_settings = WikiSettings(**wiki_data) if wiki_data is not None else WikiSettings()

    return AppConfig(
        providers=providers,
        agents=data.get("agents", {}),
        default_agent=data.get("default_agent", "main"),
        skills_dir=data.get("skills_dir", "~/.outoac/skills/"),
        max_recent_messages=data.get("max_recent_messages"),
        wiki=wiki_settings
    )


def save_config(path: Path, config: AppConfig) -> None:
    data = {
        "providers": {
            name: {
                "kind": pc.kind,
                "base_url": pc.base_url,
                "api_key": pc.api_key,
                "default_model": pc.default_model,
                "max_output_tokens": pc.max_output_tokens
            }
            for name, pc in config.providers.items()
        },
        "agents": config.agents,
        "default_agent": config.default_agent,
        "skills_dir": config.skills_dir,
        "max_recent_messages": config.max_recent_messages
    }

    if config.wiki.enabled:
        data["wiki"] = {
            "enabled": config.wiki.enabled,
            "wiki_path": config.wiki.wiki_path,
            "provider": config.wiki.provider,
            "model": config.wiki.model,
            "base_url": config.wiki.base_url,
            "api_key": config.wiki.api_key,
            "max_output_tokens": config.wiki.max_output_tokens,
            "debug": config.wiki.debug
        }

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
