from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from outo_agentcore.core.context import Context, ToolCall
from outo_agentcore.core.agent import Agent
from outo_agentcore.core.provider import Provider


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def __add__(self, other: Usage) -> Usage:
        return Usage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
        )

    def __iadd__(self, other: Usage) -> Usage:
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens
        return self


@dataclass
class LLMResponse:
    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    usage: Usage | None = None


class ProviderBackend(ABC):
    @abstractmethod
    async def call(
        self,
        context: Context,
        tools: list[dict],
        agent: Agent,
        provider: Provider,
    ) -> LLMResponse: ...


def get_backend(kind: str) -> ProviderBackend:
    if kind == "openai":
        from outo_agentcore.providers.openai import OpenAIBackend
        return OpenAIBackend()
    raise ValueError(f"Unknown provider backend: {kind}")
