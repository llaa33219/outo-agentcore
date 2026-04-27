import json
from pathlib import Path
from outo_agentcore.config.schema import AppConfig, ProviderConfig


def load_config(path: Path) -> AppConfig:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path) as f:
        data = json.load(f)

    providers = {}
    for name, pc_data in data.get("providers", {}).items():
        providers[name] = ProviderConfig(**pc_data)

    return AppConfig(
        providers=providers,
        agents=data.get("agents", {}),
        default_agent=data.get("default_agent", "main"),
        skills_dir=data.get("skills_dir", "~/.outoac/skills/")
    )


def save_config(path: Path, config: AppConfig) -> None:
    data = {
        "providers": {
            name: {
                "kind": pc.kind,
                "base_url": pc.base_url,
                "api_key": pc.api_key,
                "model": pc.model
            }
            for name, pc in config.providers.items()
        },
        "agents": config.agents,
        "default_agent": config.default_agent,
        "skills_dir": config.skills_dir
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
