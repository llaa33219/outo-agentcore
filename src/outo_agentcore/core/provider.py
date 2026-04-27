from dataclasses import dataclass

@dataclass
class Provider:
    name: str
    kind: str  # "openai" for now
    api_key: str = ""
    base_url: str | None = None