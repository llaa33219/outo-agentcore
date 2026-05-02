import asyncio
from dataclasses import asdict
from pathlib import Path

from outo_agentcore.config.loader import load_config
from outo_agentcore.core.agent import Agent
from outo_agentcore.core.provider import Provider
from outo_agentcore.core.router import Router
from outo_agentcore.core.runtime import Runtime
from outo_agentcore.core.tool import BashTool
from outo_agentcore.core.wiki_tools import WikiRecordTool, WikiSearchTool
from outo_agentcore.parser.agent_md import parse_agent_md
from outo_agentcore.parser.skill_md import discover_skills
from outo_agentcore.sessions.manager import SessionManager, SessionLoadError


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
            default_max_tokens = provider.max_output_tokens if provider else 0
            agents.append(Agent(
                name=name,
                instructions=parsed.get("instructions", ""),
                model=model,
                provider=provider_name,
                role=parsed.get("role"),
                temperature=parsed.get("temperature", 1.0),
                max_output_tokens=parsed.get("max_output_tokens", default_max_tokens),
            ))

    if not agents:
        print("Error: No agents configured. Run 'outoac setup --agent-md <path>'.")
        return

    tools = [BashTool()]

    if config.wiki.enabled:
        tools.append(WikiRecordTool(config.wiki))
        tools.append(WikiSearchTool(config.wiki))

    skills_dir = Path(config.skills_dir).expanduser()
    skills = discover_skills(skills_dir)

    router = Router(agents, tools, providers, skills=skills)
    runtime = Runtime(router)

    sessions_dir = Path.home() / ".outoac" / "sessions"
    session_mgr = SessionManager(sessions_dir)

    try:
        entry_agent = router.get_agent(args.agent or config.default_agent)
    except Exception as e:
        print(f"Error: {e}")
        return

    history_messages = []
    prev_session = None
    if args.session:
        try:
            prev_session = session_mgr.load(args.session)
        except SessionLoadError as e:
            print(f"Error: {e}")
            return
        
        if prev_session:
            all_msgs = prev_session.messages
            max_messages = args.max_messages if args.max_messages is not None else config.max_recent_messages
            if max_messages is not None:
                all_msgs = all_msgs[-max_messages:]
            history_messages = all_msgs

    result = asyncio.run(runtime.execute(args.message, entry_agent, history=history_messages))

    if args.session and prev_session:
        new_messages = result.messages[len(history_messages):]
        prev_session.messages.extend([asdict(m) for m in new_messages])
        session_mgr.save(prev_session)
        session = prev_session
    elif args.session:
        session = session_mgr.create(agent_name=args.agent, session_id=args.session)
        session.messages = [asdict(m) for m in result.messages]
        session_mgr.save(session)
    else:
        session = session_mgr.create(agent_name=args.agent)
        session.messages = [asdict(m) for m in result.messages]
        session_mgr.save(session)

    print(result.output)
    print(f"\n--- Session: {session.session_id} ---")
