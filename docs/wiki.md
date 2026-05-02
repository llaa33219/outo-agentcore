# Wiki Integration

This document describes how to use OutoWiki integration for persistent knowledge management in outo-agentcore.

## Wiki Overview

OutoWiki provides a knowledge base that agents can use to:

- Record information across conversations
- Search for previously recorded knowledge
- Build persistent context over time
- Maintain user preferences and project details

## Enabling Wiki

### Configuration

Add the `wiki` section to your config:

```json
{
  "wiki": {
    "enabled": true,
    "wiki_path": "~/.outoac/wiki/",
    "provider": "openai",
    "model": "gpt-4o",
    "api_key": "sk-xxx",
    "base_url": "https://api.openai.com/v1",
    "max_output_tokens": 0,
    "debug": false
  }
}
```

### Wiki Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable wiki tools |
| `wiki_path` | string | `~/.outoac/wiki/` | Wiki storage directory |
| `provider` | string | `"openai"` | LLM provider for wiki operations |
| `model` | string | `""` (uses provider default) | Model for wiki analysis |
| `api_key` | string | `""` (uses provider key) | API key for wiki provider |
| `base_url` | string | `""` (uses provider URL) | Base URL for wiki provider |
| `max_output_tokens` | integer | `0` (auto-detect) | Max tokens for wiki responses |
| `debug` | boolean | `false` | Enable debug logging |

### Minimal Configuration

```json
{
  "wiki": {
    "enabled": true,
    "provider": "openai",
    "model": "gpt-4o",
    "api_key": "sk-xxx"
  }
}
```

### Full Configuration

```json
{
  "wiki": {
    "enabled": true,
    "wiki_path": "~/.outoac/wiki/",
    "provider": "openai",
    "model": "gpt-4o",
    "api_key": "sk-xxx",
    "base_url": "https://api.openai.com/v1",
    "max_output_tokens": 4000,
    "debug": false
  }
}
```

## Wiki Tools

When enabled, agents have access to two wiki tools:

### `wiki_record`

Record information to the wiki knowledge base.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `content` | string | Yes | The content to record |

**Example Usage**:

```python
# Record user preference
wiki_record(content="User prefers dark mode and concise responses")

# Record research finding
wiki_record(content="Quantum computing uses qubits that can be 0 and 1 simultaneously")

# Record project info
wiki_record(content="Project uses Python 3.11, FastAPI, and PostgreSQL")

# Record meeting notes
wiki_record(content="Meeting on 2024-01-15: Decided to use microservices architecture")
```

**Response**: Returns confirmation message.

### `wiki_search`

Search the wiki knowledge base for relevant information.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | The search query |

**Example Usage**:

```python
# Search for preferences
wiki_search(query="user preferences")

# Search for topic
wiki_search(query="quantum computing")

# Search for project info
wiki_search(query="project setup")

# Search for meeting notes
wiki_search(query="architecture decisions")
```

**Response**: Returns matching wiki entries or "No results found."

## Wiki Storage

Wiki documents are stored as markdown files in the wiki directory:

```
~/.outoac/wiki/
├── abc123.md
├── def456.md
└── ...
```

Each file contains recorded information with metadata.

## Use Cases

### 1. User Preferences

Record and recall user preferences across sessions:

```python
# Session 1: Record preference
wiki_record(content="User prefers Python over JavaScript")
wiki_record(content="User likes concise code comments")
wiki_record(content="User uses VS Code as their editor")

# Session 2: Recall preferences
wiki_search(query="user preferences")
# Returns: "User prefers Python over JavaScript..."
```

### 2. Project Context

Maintain project information:

```python
# Record project details
wiki_record(content="Project: E-commerce API")
wiki_record(content="Tech stack: Python, FastAPI, PostgreSQL, Redis")
wiki_record(content="Deployment: AWS ECS with Docker")

# Later, recall project info
wiki_search(query="e-commerce project tech stack")
```

### 3. Research Knowledge Base

Build knowledge from research sessions:

```python
# Research session 1
wiki_record(content="Quantum computing uses qubits that can exist in superposition")
wiki_record(content="Quantum entanglement allows instant correlation between particles")

# Research session 2
wiki_search(query="quantum computing basics")
# Returns previously recorded information
```

### 4. Meeting Notes

Record and search meeting notes:

```python
# Record meeting
wiki_record(content="2024-01-15 Sprint Planning: Committed to 5 user stories")
wiki_record(content="2024-01-15 Sprint Planning: API refactoring is high priority")

# Later search
wiki_search(query="sprint planning commitments")
```

### 5. Learning Progress

Track learning and knowledge accumulation:

```python
# Record what was learned
wiki_record(content="Learned about FastAPI dependency injection system")
wiki_record(content="Learned about SQLAlchemy async sessions")

# Review what was learned
wiki_search(query="FastAPI learning progress")
```

## Wiki Implementation

### WikiRecordTool

```python
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

    async def execute(self, content: str) -> ToolResult:
        try:
            wiki = self._get_wiki()
            result = wiki.record(content)
            return ToolResult(content=f"Recorded to wiki: {result}")
        except Exception as e:
            return ToolResult(content=f"Error recording to wiki: {e}")
```

### WikiSearchTool

```python
class WikiSearchTool:
    name = "wiki_search"
    description = "Search the wiki knowledge base for relevant information."

    def __init__(self, settings: WikiSettings) -> None:
        self._settings = settings
        self._wiki = None

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
```

## Best Practices

### 1. Record Important Information

```python
# Good: Record specific, useful information
wiki_record(content="User's production database is PostgreSQL 15 on AWS RDS")

# Bad: Record vague information
wiki_record(content="User has a database")
```

### 2. Use Clear, Searchable Content

```python
# Good: Clear and searchable
wiki_record(content="Project authentication uses JWT tokens with RS256 algorithm")

# Bad: Not easily searchable
wiki_record(content="We use tokens for auth")
```

### 3. Record Context for Future Sessions

```python
# At the end of a session
wiki_record(content="Session summary: Discussed API design, decided on REST with OpenAPI spec")
wiki_record(content="Next steps: Implement user authentication, add rate limiting")
```

### 4. Search Before Asking

```python
# Good: Check wiki first
result = wiki_search(query="user preferences")
if "No results" not in result:
    # Use existing knowledge
    pass
else:
    # Ask user
    pass
```

### 5. Keep Wiki Organized

Record information with context:

```python
# Good: With context
wiki_record(content="[2024-01-15] Decided to use FastAPI for the new API project")

# Bad: Without context
wiki_record(content="Use FastAPI")
```

## Troubleshooting

### Wiki tools not available

```
wiki_record is not available
```

**Solution**: Enable wiki in config:

```json
{
  "wiki": {
    "enabled": true
  }
}
```

### Wiki not recording

```
Error recording to wiki: ...
```

**Solution**:
- Check wiki directory permissions
- Verify API key and model settings
- Enable debug logging: `"debug": true`

### Wiki search not finding results

```
No results found.
```

**Solution**:
- Verify information was recorded
- Try different search terms
- Check wiki directory for recorded files

### Wiki provider errors

```
Error: Invalid API key
```

**Solution**: Check wiki provider settings in config.

## Dependencies

Wiki integration requires the `outowiki` package:

```bash
pip install outowiki
```

Or with uv:

```bash
uv add outowiki
```

## Future Enhancements

Planned features for wiki integration:

- **Automatic Recording**: Agents automatically record important information
- **Knowledge Graphs**: Visual representation of knowledge relationships
- **Export/Import**: Share wiki knowledge between instances
- **Advanced Search**: Semantic search with embeddings
- **Versioning**: Track changes to wiki entries over time
