from dataclasses import dataclass

@dataclass
class Agent:
    name: str
    instructions: str
    model: str
    provider: str
    role: str | None = None
    max_output_tokens: int | None = None
    temperature: float = 1.0
    context_window: int | None = None