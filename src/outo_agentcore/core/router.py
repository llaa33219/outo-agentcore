from __future__ import annotations
from typing import TYPE_CHECKING
from outo_agentcore.core.agent import Agent
from outo_agentcore.core.provider import Provider
from outo_agentcore.core.skill import Skill
from outo_agentcore.core.tool import BashTool
from outo_agentcore.core.context import Context
from outo_agentcore.providers import get_backend, LLMResponse

if TYPE_CHECKING:
    pass

CALL_AGENT = "call_agent"
FINISH = "finish"


class RoutingError(Exception):
    pass


class Router:
    def __init__(self, agents: list[Agent], tools: list, providers: list[Provider], skills: list[Skill] | None = None):
        self._agents = {a.name: a for a in agents}
        self._providers = {p.name: p for p in providers}
        self._tools = {t.name: t for t in tools}
        self._skills = skills or []

    def get_agent(self, name: str) -> Agent:
        if name not in self._agents:
            raise RoutingError(f"Agent not found: {name}")
        return self._agents[name]

    def get_provider(self, name: str) -> Provider:
        if name not in self._providers:
            raise RoutingError(f"Provider not found: {name}")
        return self._providers[name]

    def get_tool(self, name: str):
        if name not in self._tools:
            raise RoutingError(f"Tool not found: {name}")
        return self._tools[name]

    def build_system_prompt(self, agent: Agent, caller: str | None = None) -> str:
        parts = []

        role = agent.role or agent.instructions[:50]
        parts.append(f'You are "{agent.name}". {role}')

        parts.append(f"\nINSTRUCTIONS:\n{agent.instructions}")

        if caller:
            parts.append(f"\nINVOKED BY: You have been called by '{caller}'.")
            parts.append("Consider their request carefully and fulfill it.")

        other_agents = [a for a in self._agents.values() if a.name != agent.name]
        if other_agents:
            parts.append("\nAvailable agents:")
            for a in other_agents:
                a_role = a.role or a.instructions[:50]
                parts.append(f"- {a.name}: {a_role}")

        parts.append("\nAvailable tools:")
        parts.append("- bash: Execute a bash command and return its output.")
        parts.append("- call_agent: Call another agent.")
        parts.append("- finish: Return your final result to the caller.")

        if "wiki_record" in self._tools:
            parts.append("- wiki_record: Record information to the wiki knowledge base.")
        if "wiki_search" in self._tools:
            parts.append("- wiki_search: Search the wiki knowledge base for information.")

        if self._skills:
            parts.append("\nAvailable skills:")
            for skill in self._skills:
                parts.append(f"- {skill.name}: {skill.description}")
            parts.append("\nTo use a skill, read its SKILL.md file when the task matches its description.")
            parts.append("Example: bash(command=\"cat ~/.outoac/skills/<skill-name>/SKILL.md\")")

        parts.append("\nIMPORTANT: You MUST call the finish tool to return your final result.")
        parts.append("Plain text responses are NOT delivered to the caller.")
        parts.append("Use call_agent to delegate work to other agents.")

        return "\n".join(parts)

    def build_tool_schemas(self, current_agent: str) -> list[dict]:
        schemas = []

        for tool in self._tools.values():
            schemas.append(tool.to_schema())

        schemas.append(self.build_call_agent_schema())
        schemas.append(self.build_finish_schema())

        return schemas

    def build_call_agent_schema(self) -> dict:
        return {
            "name": "call_agent",
            "description": "Call another agent. The agent will process your message and return a result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "agent_name": {"type": "string", "description": "Name of the agent to call"},
                    "message": {"type": "string", "description": "Message to send to the agent"},
                },
                "required": ["agent_name", "message"],
            },
        }

    def build_finish_schema(self) -> dict:
        return {
            "name": "finish",
            "description": "Return your final result to the caller. This is the ONLY way to deliver your response.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Result message to return"},
                },
                "required": ["message"],
            },
        }

    async def call_llm(self, agent: Agent, context: Context, tool_schemas: list[dict]) -> LLMResponse:
        provider = self._providers.get(agent.provider)
        if provider is None:
            raise RoutingError(f"Provider not found: {agent.provider}")
        backend = get_backend(provider.kind)
        return await backend.call(context, tool_schemas, agent, provider)
