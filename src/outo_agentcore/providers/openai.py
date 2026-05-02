from __future__ import annotations
import json
from typing import Any
from openai import AsyncOpenAI
from outo_agentcore.providers import ProviderBackend, LLMResponse, Usage
from outo_agentcore.core.context import Context, ToolCall, ContextMessage
from outo_agentcore.core.agent import Agent
from outo_agentcore.core.provider import Provider
from outo_agentcore.core.token_utils import get_max_output_tokens


class OpenAIBackend(ProviderBackend):
    def __init__(self) -> None:
        self._clients: dict[str, AsyncOpenAI] = {}

    def _get_client(self, provider: Provider) -> AsyncOpenAI:
        key = (provider.api_key, provider.name)
        if key not in self._clients:
            kwargs: dict[str, Any] = {"api_key": provider.api_key}
            if provider.base_url:
                kwargs["base_url"] = provider.base_url
            self._clients[key] = AsyncOpenAI(**kwargs)
        return self._clients[key]

    async def call(
        self,
        context: Context,
        tools: list[dict],
        agent: Agent,
        provider: Provider,
    ) -> LLMResponse:
        client = self._get_client(provider)
        messages = _build_messages(context)
        openai_tools = _build_tools(tools) if tools else None

        max_tokens = get_max_output_tokens(agent.model, agent.max_output_tokens)

        params: dict[str, Any] = {
            "model": agent.model,
            "messages": messages,
        }
        if openai_tools:
            params["tools"] = openai_tools
        if max_tokens:
            params["max_completion_tokens"] = max_tokens

        response = await client.chat.completions.create(**params)
        choice = response.choices[0]

        content = choice.message.content
        tool_calls: list[ToolCall] = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_calls.append(
                    ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=_parse_tool_arguments(tc.function.arguments),
                    )
                )

        usage = None
        if response.usage:
            usage = Usage(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
            )

        return LLMResponse(content=content, tool_calls=tool_calls, usage=usage)


def _build_messages(context: Context) -> list[dict]:
    messages: list[dict] = [{"role": "system", "content": context.system_prompt}]

    for msg in context.messages:
        if msg.role == "user":
            messages.append({"role": "user", "content": msg.content})
        elif msg.role == "assistant":
            if msg.tool_calls:
                openai_tc = []
                for tc in msg.tool_calls:
                    openai_tc.append(
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.name,
                                "arguments": json.dumps(tc.arguments),
                            },
                        }
                    )
                entry: dict[str, Any] = {"role": "assistant", "tool_calls": openai_tc}
                if msg.content:
                    entry["content"] = msg.content
                messages.append(entry)
            else:
                messages.append({"role": "assistant", "content": msg.content})
        elif msg.role == "tool":
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": msg.tool_call_id,
                    "content": msg.content,
                }
            )

    return messages


def _build_tools(tools: list[dict]) -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t["description"],
                "parameters": t["parameters"],
            },
        }
        for t in tools
    ]


def _parse_tool_arguments(raw: str | None) -> dict:
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}
