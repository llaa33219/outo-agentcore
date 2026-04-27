from dataclasses import dataclass, field


@dataclass
class ProviderConfig:
    kind: str = "openai"
    base_url: str = ""
    api_key: str = ""
    model: str = ""


@dataclass
class AppConfig:
    providers: dict[str, ProviderConfig]
    agents: dict[str, str]
    sub_agents: list[str]
    skills_dir: str = "~/.outoac/skills/"
