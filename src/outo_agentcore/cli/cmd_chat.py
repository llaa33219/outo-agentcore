from __future__ import annotations

import logging
from dataclasses import asdict
from pathlib import Path

import agentouto

from outo_agentcore.config.loader import load_config
from outo_agentcore.parser.agent_md import parse_agent_md
from outo_agentcore.parser.skill_md import discover_skills
from outo_agentcore.sessions.manager import SessionManager, SessionLoadError
from outo_agentcore.tools import bash, make_wiki_record_tool, make_wiki_search_tool


def cmd_chat(args) -> None:
    agentouto_logger = logging.getLogger("agentouto")
    if args.debug:
        agentouto_logger.setLevel(logging.DEBUG)
    else:
        agentouto_logger.setLevel(logging.ERROR)

    config_path = Path.home() / ".outoac" / "config.json"
    if not config_path.exists():
        print("Error: No config found. Run 'outoac setup' first.")
        return

    config = load_config(config_path)

    providers = []
    for name, pc in config.providers.items():
        providers.append(
            agentouto.Provider(
                name=name,
                kind=pc.kind,
                api_key=pc.api_key,
                base_url=pc.base_url if pc.base_url else None,
            )
        )

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
            agents.append(
                agentouto.Agent(
                    name=name,
                    instructions=parsed.get("instructions", ""),
                    model=model,
                    provider=provider_name,
                    role=parsed.get("role"),
                    temperature=parsed.get("temperature", 1.0),
                    max_output_tokens=parsed.get("max_output_tokens", default_max_tokens) or None,
                )
            )

    if not agents:
        print("Error: No agents configured. Run 'outoac setup --agent-md <path>'.")
        return

    tools: list[agentouto.Tool] = [bash]

    if config.wiki.enabled:
        tools.append(make_wiki_record_tool(config.wiki))
        tools.append(make_wiki_search_tool(config.wiki))

    skills_dir = Path(config.skills_dir).expanduser()
    skills = discover_skills(skills_dir)

    extra_instructions = ""
    if skills:
        parts = ["Available skills:"]
        for skill in skills:
            parts.append(f"- {skill.name}: {skill.description}")
        parts.append(
            "To use a skill, read its SKILL.md file when the task matches its description."
        )
        parts.append('Example: bash(command="cat ~/.outoac/skills/<skill-name>/SKILL.md")')
        extra_instructions = "\n".join(parts)

    sessions_dir = Path.home() / ".outoac" / "sessions"
    session_mgr = SessionManager(sessions_dir)

    entry_agent_name = args.agent or config.default_agent
    try:
        entry_agent = next(a for a in agents if a.name == entry_agent_name)
    except StopIteration:
        print(f"Error: Agent '{entry_agent_name}' not found.")
        return

    history: list[agentouto.Message] | None = None
    prev_session = None
    if args.session:
        try:
            prev_session = session_mgr.load(args.session)
        except SessionLoadError as exc:
            print(f"Error: {exc}")
            return

        if prev_session:
            history = []
            for msg in prev_session.messages:
                history.append(
                    agentouto.Message(
                        type=msg["type"],
                        sender=msg["sender"],
                        receiver=msg["receiver"],
                        content=msg["content"],
                        call_id=msg.get("call_id", ""),
                    )
                )
            max_messages = args.max_messages if args.max_messages is not None else config.max_recent_messages
            if max_messages is not None:
                history = history[-max_messages:]

    result = agentouto.run(
        message=args.message,
        starting_agents=[entry_agent],
        run_agents=agents,
        tools=tools,
        providers=providers,
        history=history,
        extra_instructions=extra_instructions if extra_instructions else None,
        extra_instructions_scope="all",
        debug=args.debug,
    )

    session_messages = []
    for msg in result.messages:
        session_messages.append(
            {
                "type": msg.type,
                "sender": msg.sender,
                "receiver": msg.receiver,
                "content": msg.content,
                "call_id": msg.call_id,
            }
        )

    if args.session and prev_session:
        prev_session.messages.extend(session_messages[len(history) if history else 0:])
        session_mgr.save(prev_session)
        session = prev_session
    elif args.session:
        session = session_mgr.create(agent_name=args.agent, session_id=args.session)
        session.messages = session_messages
        session_mgr.save(session)
    else:
        session = session_mgr.create(agent_name=args.agent)
        session.messages = session_messages
        session_mgr.save(session)

    print(result.output)
    print(f"\n--- Session: {session.session_id} ---")
