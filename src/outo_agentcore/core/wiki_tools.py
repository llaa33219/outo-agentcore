from __future__ import annotations

from pathlib import Path
from typing import Any

from outo_agentcore.config.schema import WikiSettings
from outo_agentcore.core.tool import ToolResult
from outo_agentcore.core.token_utils import get_max_output_tokens


class WikiRecordTool:
    name = "wiki_record"
    description = "Record information to the wiki knowledge base for future reference."

    def __init__(self, settings: WikiSettings) -> None:
        self._settings = settings
        self._wiki = None

    def _get_wiki(self):
        if self._wiki is None:
            from outowiki import OutoWiki, WikiConfig
            wiki_path = str(Path(self._settings.wiki_path).expanduser())
            max_tokens = get_max_output_tokens(self._settings.model, self._settings.max_output_tokens)
            config = WikiConfig(
                provider=self._settings.provider,
                base_url=self._settings.base_url,
                api_key=self._settings.api_key,
                model=self._settings.model,
                max_output_tokens=max_tokens,
                wiki_path=wiki_path,
                debug=self._settings.debug
            )
            self._wiki = OutoWiki(config)
        return self._wiki

    def to_schema(self) -> dict[str, Any]:
        return {
            "name": "wiki_record",
            "description": "Record information to the wiki knowledge base for future reference.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content to record to the wiki",
                    },
                },
                "required": ["content"],
            },
        }

    async def execute(self, content: str) -> ToolResult:
        try:
            wiki = self._get_wiki()
            result = wiki.record(content)
            return ToolResult(content=f"Recorded to wiki: {result}")
        except Exception as e:
            return ToolResult(content=f"Error recording to wiki: {e}")


class WikiSearchTool:
    name = "wiki_search"
    description = "Search the wiki knowledge base for relevant information."

    def __init__(self, settings: WikiSettings) -> None:
        self._settings = settings
        self._wiki = None

    def _get_wiki(self):
        if self._wiki is None:
            from outowiki import OutoWiki, WikiConfig
            wiki_path = str(Path(self._settings.wiki_path).expanduser())
            max_tokens = get_max_output_tokens(self._settings.model, self._settings.max_output_tokens)
            config = WikiConfig(
                provider=self._settings.provider,
                base_url=self._settings.base_url,
                api_key=self._settings.api_key,
                model=self._settings.model,
                max_output_tokens=max_tokens,
                wiki_path=wiki_path,
                debug=self._settings.debug
            )
            self._wiki = OutoWiki(config)
        return self._wiki

    def to_schema(self) -> dict[str, Any]:
        return {
            "name": "wiki_search",
            "description": "Search the wiki knowledge base for relevant information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find relevant wiki content",
                    },
                },
                "required": ["query"],
            },
        }

    async def execute(self, query: str) -> ToolResult:
        try:
            wiki = self._get_wiki()
            result = wiki.search(query)
            if result.paths:
                paths_str = "\n".join(result.paths)
                return ToolResult(content=f"Found {len(result.paths)} results:\n{paths_str}")
            return ToolResult(content="No results found.")
        except Exception as e:
            return ToolResult(content=f"Error searching wiki: {e}")
