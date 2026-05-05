"""CLI tools for outo-agentcore, built on agentouto SDK."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import agentouto

if TYPE_CHECKING:
    from outo_agentcore.config.schema import WikiSettings


_wiki_cache: dict[str, object] = {}


def _get_wiki(settings: WikiSettings) -> object:
    key = str(settings.wiki_path)
    if key not in _wiki_cache:
        from outowiki import OutoWiki, WikiConfig

        wiki_path = str(Path(settings.wiki_path).expanduser())
        config = WikiConfig(
            provider=settings.provider,
            base_url=settings.base_url or None,
            api_key=settings.api_key or None,
            model=settings.model or None,
            max_output_tokens=settings.max_output_tokens or None,
            wiki_path=wiki_path,
            debug=settings.debug,
        )
        _wiki_cache[key] = OutoWiki(config)
    return _wiki_cache[key]


@agentouto.Tool
def bash(command: str) -> str:
    """Execute a bash command and return its output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout + result.stderr


def make_wiki_record_tool(settings: WikiSettings) -> agentouto.Tool:
    def wiki_record(content: str) -> str:
        """Record information to the wiki knowledge base for future reference."""
        try:
            wiki = _get_wiki(settings)
            result = wiki.record(content)
            return f"Recorded to wiki: {result}"
        except Exception as exc:
            return f"Error recording to wiki: {exc}"

    return agentouto.Tool(wiki_record)


def make_wiki_search_tool(settings: WikiSettings) -> agentouto.Tool:
    def wiki_search(query: str) -> str:
        """Search the wiki knowledge base for relevant information."""
        try:
            wiki = _get_wiki(settings)
            result = wiki.search(query)
            if result.paths:
                paths_str = "\n".join(result.paths)
                return f"Found {len(result.paths)} results:\n{paths_str}"
            return "No results found."
        except Exception as exc:
            return f"Error searching wiki: {exc}"

    return agentouto.Tool(wiki_search)
