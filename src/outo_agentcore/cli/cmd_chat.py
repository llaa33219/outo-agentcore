import asyncio
from dataclasses import asdict
from pathlib import Path

from outo_agentcore.config.loader import load_config
from outo_agentcore.core.agent import Agent
from outo_agentcore.core.provider import Provider
from outo_agentcore.core.router import Router
from outo_agentcore.core.runtime import Runtime
from outo_agentcore.core.tool import BashTool
from outo_agentcore.parser.agent_md import parse_agent_md
from outo_agentcore.sessions.manager import SessionManager


def cmd_chat(args) -> None:
    config_path = Path.home() / ".outoac" / "config.json"
    if not config_path.exists():
        print("Error: No config found. Run 'outoac setup' first.")
        return

    config = load_config(config_path)

    providers = []
    for name, pc in config.providers.items():
        providers.append(Provider(
            name=name,
            kind=pc.kind,
            api_key=pc.api_key,
            base_url=pc.base_url if pc.base_url else None,
        ))

    agents = []
    for name, md_path in config.agents.items():
        md_path = Path(md_path).expanduser()
        if md_path.exists():
            parsed = parse_agent_md(md_path)
            provider_name = parsed.get("provider", list(config.providers.keys())[0])
            provider = config.providers.get(provider_name)
            default_model = provider.default_model if provider else ""
            model = parsed.get("model", default_model)
            agents.append(Agent(
                name=name,
                instructions=parsed.get("instructions", ""),
                model=model,
                provider=provider_name,
                role=parsed.get("role"),
                temperature=parsed.get("temperature", 1.0),
            ))

    if not agents:
        print("Error: No agents configured. Run 'outoac setup --agent-md <path>'.")
        return

    tools = [BashTool()]

    router = Router(agents, tools, providers)
    runtime = Runtime(router)

    sessions_dir = Path.home() / ".outoac" / "sessions"
    session_mgr = SessionManager(sessions_dir)

    try:
        entry_agent = router.get_agent(args.agent or config.default_agent)
    except Exception as e:
        print(f"Error: {e}")
        return

    result = asyncio.run(runtime.execute(args.message, entry_agent))

    session = session_mgr.create(agent_name=args.agent)
    session.messages = [asdict(m) for m in result.messages]
    session_mgr.save(session)

    print(result.output)
    print(f"\n--- Session: {session.session_id} ---")
