from dataclasses import dataclass, field


@dataclass
class ProviderConfig:
    kind: str = "openai"
    base_url: str = ""
    api_key: str = ""
    default_model: str = ""
    max_output_tokens: int = 0


@dataclass
class WikiSettings:
    enabled: bool = False
    wiki_path: str = "~/.outoac/wiki/"
    provider: str = "openai"
    model: str = ""
    base_url: str = ""
    api_key: str = ""
    max_output_tokens: int = 0
    debug: bool = False


@dataclass
class AppConfig:
    providers: dict[str, ProviderConfig]
    agents: dict[str, str]
    default_agent: str = "main"
    skills_dir: str = "~/.outoac/skills/"
    max_recent_messages: int | None = None
    wiki: WikiSettings = field(default_factory=WikiSettings)
