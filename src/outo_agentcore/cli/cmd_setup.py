from pathlib import Path
from outo_agentcore.config.schema import AppConfig, ProviderConfig
from outo_agentcore.config.loader import load_config, save_config

def cmd_setup(args):
    config_dir = Path.home() / ".outoac"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "config.json"

    if config_path.exists():
        config = load_config(config_path)
    else:
        config = AppConfig(
            providers={},
            agents={},
            sub_agents=[],
            skills_dir=str(config_dir / "skills")
        )

    if args.base_url or args.api_key or args.model:
        provider = config.providers.get(args.provider_name, ProviderConfig())
        if args.base_url:
            provider.base_url = args.base_url
        if args.api_key:
            provider.api_key = args.api_key
        if args.model:
            provider.model = args.model
        provider.kind = "openai"
        config.providers[args.provider_name] = provider

    if args.agent_md:
        config.agents["main"] = args.agent_md

    if args.sub_agents:
        config.sub_agents = args.sub_agents
        for name in args.sub_agents:
            if name not in config.agents:
                agent_path = config_dir / "agents" / f"{name}.md"
                config.agents[name] = str(agent_path)

    save_config(config_path, config)
    print(f"Configuration saved to {config_path}")