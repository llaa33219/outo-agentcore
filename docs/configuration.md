# Configuration Reference

This document describes all configuration options for outo-agentcore.

## Configuration File Location

```
~/.outoac/config.json
```

## Configuration Schema

```json
{
  "providers": {
    "default": {
      "kind": "openai",
      "base_url": "http://localhost:11434/v1",
      "api_key": "your-key",
      "default_model": "llama4:scout",
      "max_output_tokens": 0
    }
  },
  "agents": {
    "main": "~/.outoac/agents/main.md",
    "researcher": "~/.outoac/agents/researcher.md",
    "writer": "~/.outoac/agents/writer.md"
  },
  "default_agent": "main",
  "skills_dir": "~/.outoac/skills/",
  "max_recent_messages": null,
  "wiki": {
    "enabled": false,
    "wiki_path": "~/.outoac/wiki/",
    "provider": "openai",
    "model": "gpt-5.5",
    "api_key": "",
    "base_url": "",
    "max_output_tokens": 0,
    "debug": false
  }
}
```

## Provider Settings

Each provider is defined under the `providers` key with a unique name.

### `kind`

- **Type**: `string`
- **Default**: `"openai"`
- **Description**: Provider backend type. Currently only `"openai"` is supported, which works with any OpenAI-compatible API (OpenAI, Anthropic, Gemini, Ollama, LM Studio, vLLM, etc.).

### `base_url`

- **Type**: `string`
- **Required**: Yes
- **Description**: API endpoint URL for the provider.

Common values:
| Provider | Base URL |
|----------|----------|
| OpenAI | `https://api.openai.com/v1` |
| Anthropic | `https://api.anthropic.com/v1` |
| Google Gemini | `https://generativelanguage.googleapis.com/v1beta` |
| Ollama | `http://localhost:11434/v1` |
| LM Studio | `http://localhost:1234/v1` |
| vLLM | `http://localhost:8000/v1` |

### `api_key`

- **Type**: `string`
- **Required**: Yes
- **Description**: API key for authentication. For local providers (Ollama, LM Studio), this can be any non-empty string.

### `default_model`

- **Type**: `string`
- **Required**: Yes
- **Description**: Default model to use for agents that don't specify a model.

Common values:
| Provider | Model |
|----------|-------|
| OpenAI | `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo` |
| Anthropic | `claude-3-opus-20240229`, `claude-3-sonnet-20240229` |
| Google | `gemini-pro`, `gemini-ultra` |
| Ollama | `llama3`, `mistral`, `mixtral` |

### `max_output_tokens`

- **Type**: `integer`
- **Default**: `0`
- **Description**: Maximum number of tokens in the LLM response. When set to `0`, the system automatically retrieves the optimal value from the [LCW API](https://lcw-api.blp.sh/context-window). Agent-level settings override this value.

## Agent Settings

The `agents` key maps agent names to their markdown definition files.

```json
{
  "agents": {
    "main": "~/.outoac/agents/main.md",
    "researcher": "~/.outoac/agents/researcher.md",
    "writer": "~/.outoac/agents/writer.md",
    "reviewer": "~/.outoac/agents/reviewer.md",
    "coder": "~/.outoac/agents/coder.md",
    "tester": "~/.outoac/agents/tester.md"
  }
}
```

- **Key**: Agent name (used in `call_agent` tool and `--agent` flag)
- **Value**: Path to agent markdown file (supports `~` expansion)

See [Agents](agents.md) for the markdown format specification.

## `default_agent`

- **Type**: `string`
- **Default**: `"main"`
- **Description**: Default agent to use when `--agent` flag is not specified in `outoac chat`.

## `skills_dir`

- **Type**: `string`
- **Default**: `"~/.outoac/skills/"`
- **Description**: Directory for skill definitions (reserved for future use).

## `max_recent_messages`

- **Type**: `integer | null`
- **Default**: `null`
- **Description**: Maximum number of recent messages to include when continuing a session. When `null`, all messages are included. This helps manage context window limits for long sessions.

```json
{
  "max_recent_messages": 50
}
```

## Wiki Settings

The `wiki` key configures OutoWiki integration for persistent knowledge management.

### `enabled`

- **Type**: `boolean`
- **Default**: `false`
- **Description**: Enable or disable wiki tools (`wiki_record`, `wiki_search`).

### `wiki_path`

- **Type**: `string`
- **Default**: `"~/.outoac/wiki/"`
- **Description**: Directory where wiki documents are stored.

### `provider`

- **Type**: `string`
- **Default**: `"openai"`
- **Description**: LLM provider to use for wiki operations (embedding, analysis).

### `model`

- **Type**: `string`
- **Default**: `""` (uses provider default)
- **Description**: Model to use for wiki operations. If empty, uses the provider's default model.

### `api_key`

- **Type**: `string`
- **Default**: `""` (uses provider key)
- **Description**: API key for wiki provider. If empty, uses the main provider's API key.

### `base_url`

- **Type**: `string`
- **Default**: `""` (uses provider URL)
- **Description**: Base URL for wiki provider. If empty, uses the main provider's base URL.

### `max_output_tokens`

- **Type**: `integer`
- **Default**: `0` (auto-detected)
- **Description**: Maximum tokens for wiki responses. When `0`, automatically retrieves optimal value from LCW API.

### `debug`

- **Type**: `boolean`
- **Default**: `false`
- **Description**: Enable debug logging for wiki operations.

## Environment Variables

Configuration can also be set via environment variables:

| Variable | Description |
|----------|-------------|
| `OUTOAC_CONFIG` | Custom config file path (default: `~/.outoac/config.json`) |
| `OUTOAC_API_KEY` | Override API key for default provider |
| `OUTOAC_BASE_URL` | Override base URL for default provider |
| `OUTOAC_MODEL` | Override default model |

## Configuration Precedence

Settings are applied in this order (highest priority first):

1. Command-line arguments
2. Environment variables
3. Configuration file
4. Default values

## Examples

### Minimal Configuration (Ollama)

```json
{
  "providers": {
    "default": {
      "kind": "openai",
      "base_url": "http://localhost:11434/v1",
      "api_key": "ollama",
      "default_model": "llama3"
    }
  },
  "agents": {
    "main": "~/.outoac/agents/main.md"
  }
}
```

### Multi-Provider Configuration

```json
{
  "providers": {
    "local": {
      "kind": "openai",
      "base_url": "http://localhost:11434/v1",
      "api_key": "ollama",
      "default_model": "llama3"
    },
    "openai": {
      "kind": "openai",
      "base_url": "https://api.openai.com/v1",
      "api_key": "sk-xxx",
      "default_model": "gpt-4o"
    }
  },
  "agents": {
    "main": "~/.outoac/agents/main.md",
    "researcher": "~/.outoac/agents/researcher.md"
  }
}
```

### Full Configuration with Wiki

```json
{
  "providers": {
    "default": {
      "kind": "openai",
      "base_url": "http://localhost:11434/v1",
      "api_key": "ollama",
      "default_model": "llama3",
      "max_output_tokens": 4096
    }
  },
  "agents": {
    "main": "~/.outoac/agents/main.md",
    "researcher": "~/.outoac/agents/researcher.md",
    "writer": "~/.outoac/agents/writer.md"
  },
  "default_agent": "main",
  "skills_dir": "~/.outoac/skills/",
  "max_recent_messages": 50,
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

## Validation

The configuration is validated on load:

- **Missing file**: Raises `FileNotFoundError`
- **Invalid JSON**: Raises `json.JSONDecodeError`
- **Invalid provider kind**: Raises `ValueError` at runtime
- **Missing required fields**: Uses defaults where possible

## Troubleshooting

### Config not found

```
Error: No config found. Run 'outoac setup' first.
```

**Solution**: Run `outoac setup` with your provider details.

### Invalid provider

```
Error: Provider not found: openai
```

**Solution**: Ensure the provider name in your agent definition matches a provider in your config.

### Token limit issues

If responses are truncated:

1. Set `max_output_tokens` in provider config
2. Or set `max_output_tokens` in agent frontmatter
3. Or leave at `0` for auto-detection (requires internet for LCW API)
