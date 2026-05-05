# Provider Integration

This document describes how to configure LLM providers with outo-agentcore.

## Provider Overview

Providers are configured in `~/.outoac/config.json` and passed to the [agentouto](https://github.com/llaa33219/agentouto) SDK, which handles all provider backends natively.

## Supported Providers

agentouto supports these provider kinds natively:

| Kind | Provider | Example Models | Compatible With |
|------|----------|----------------|-----------------|
| `"openai"` | OpenAI Chat Completions API | `gpt-5.2`, `gpt-5.3-codex`, `o3`, `o4-mini` | vLLM, Ollama, LM Studio, any OpenAI-compatible API |
| `"openai_responses"` | OpenAI Responses API | `gpt-5.2`, `gpt-5.3-codex`, `o3`, `o4-mini` | — |
| `"anthropic"` | Anthropic API | `claude-opus-4-6`, `claude-sonnet-4-6` | AWS Bedrock, Google Vertex AI, Ollama, LiteLLM |
| `"google"` | Google Gemini API | `gemini-3.1-pro`, `gemini-3-flash` | — |

## Provider Configuration

### Basic Structure

```json
{
  "providers": {
    "provider_name": {
      "kind": "openai",
      "base_url": "https://api.openai.com/v1",
      "api_key": "sk-xxx",
      "default_model": "gpt-5.5",
      "max_output_tokens": 0
    }
  }
}
```

### Configuration Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `kind` | string | Yes | Provider kind: `openai`, `openai_responses`, `anthropic`, `google` |
| `base_url` | string | Yes | API endpoint URL |
| `api_key` | string | Yes | API authentication key |
| `default_model` | string | Yes | Default model for agents |
| `max_output_tokens` | integer | No | Max output tokens (0 = auto-detect via LCW API) |

## Provider Setup Examples

### OpenAI

```bash
outoac setup \
  --base-url https://api.openai.com/v1 \
  --api-key sk-xxx \
  --default-model gpt-5.5 \
  --provider-name openai
```

Config:

```json
{
  "providers": {
    "openai": {
      "kind": "openai",
      "base_url": "https://api.openai.com/v1",
      "api_key": "sk-xxx",
      "default_model": "gpt-5.5",
      "max_output_tokens": 0
    }
  }
}
```

### Anthropic (Native)

```bash
outoac setup \
  --base-url https://api.anthropic.com/v1 \
  --api-key sk-ant-xxx \
  --default-model claude-sonnet-4-6 \
  --provider-name anthropic
```

Config:

```json
{
  "providers": {
    "anthropic": {
      "kind": "anthropic",
      "base_url": "https://api.anthropic.com/v1",
      "api_key": "sk-ant-xxx",
      "default_model": "claude-sonnet-4-6",
      "max_output_tokens": 0
    }
  }
}
```

### Google Gemini (Native)

```bash
outoac setup \
  --base-url https://generativelanguage.googleapis.com/v1beta \
  --api-key AIza... \
  --default-model gemini-3-1-pro \
  --provider-name google
```

Config:

```json
{
  "providers": {
    "google": {
      "kind": "google",
      "base_url": "https://generativelanguage.googleapis.com/v1beta",
      "api_key": "AIza...",
      "default_model": "gemini-3-1-pro",
      "max_output_tokens": 0
    }
  }
}
```

### Ollama (Local)

```bash
outoac setup \
  --base-url http://localhost:11434/v1 \
  --api-key ollama \
  --default-model llama4:scout \
  --provider-name local
```

Config:

```json
{
  "providers": {
    "local": {
      "kind": "openai",
      "base_url": "http://localhost:11434/v1",
      "api_key": "ollama",
      "default_model": "llama4:scout",
      "max_output_tokens": 0
    }
  }
}
```

### LM Studio (Local)

```bash
outoac setup \
  --base-url http://localhost:1234/v1 \
  --api-key lm-studio \
  --default-model local-model \
  --provider-name lmstudio
```

Config:

```json
{
  "providers": {
    "lmstudio": {
      "kind": "openai",
      "base_url": "http://localhost:1234/v1",
      "api_key": "lm-studio",
      "default_model": "local-model",
      "max_output_tokens": 0
    }
  }
}
```

## Multi-Provider Setup

Configure multiple providers for different agents:

```json
{
  "providers": {
    "local": {
      "kind": "openai",
      "base_url": "http://localhost:11434/v1",
      "api_key": "ollama",
      "default_model": "llama4:scout",
      "max_output_tokens": 0
    },
    "openai": {
      "kind": "openai",
      "base_url": "https://api.openai.com/v1",
      "api_key": "sk-xxx",
      "default_model": "gpt-5.5",
      "max_output_tokens": 0
    },
    "anthropic": {
      "kind": "anthropic",
      "base_url": "https://api.anthropic.com/v1",
      "api_key": "sk-ant-xxx",
      "default_model": "claude-sonnet-4-6",
      "max_output_tokens": 0
    }
  },
  "agents": {
    "main": "~/.outoac/agents/main.md",
    "researcher": "~/.outoac/agents/researcher.md",
    "writer": "~/.outoac/agents/writer.md"
  }
}
```

Use different providers per agent via frontmatter:

```markdown
---
provider: local
model: llama4:scout
---

# Main Agent
You coordinate work using local models.
```

```markdown
---
provider: anthropic
model: claude-sonnet-4-6
---

# Researcher
You research using Anthropic models.
```

## Token Management

### Auto-Detection

When `max_output_tokens` is `0`, agentouto automatically retrieves the optimal value from the [LCW API](https://lcw-api.blp.sh/context-window).

### Manual Configuration

Set specific token limits:

**Provider level** (applies to all agents using this provider):

```json
{
  "providers": {
    "default": {
      "kind": "openai",
      "base_url": "http://localhost:11434/v1",
      "api_key": "ollama",
      "default_model": "llama4:scout",
      "max_output_tokens": 4096
    }
  }
}
```

**Agent level** (overrides provider default):

```markdown
---
max_output_tokens: 8000
---

# Writer Agent
You write long-form content.
```

## Best Practices

### 1. Use Local Models for Development

```json
{
  "providers": {
    "local": {
      "kind": "openai",
      "base_url": "http://localhost:11434/v1",
      "api_key": "ollama",
      "default_model": "llama4:scout"
    }
  }
}
```

### 2. Use Cloud Models for Production

```json
{
  "providers": {
    "production": {
      "kind": "openai",
      "base_url": "https://api.openai.com/v1",
      "api_key": "sk-xxx",
      "default_model": "gpt-5.5"
    }
  }
}
```

### 3. Match Models to Tasks

```markdown
---
provider: local
model: llama4:scout
temperature: 0.2
---

# Simple Tasks Agent
You handle simple, factual tasks.
```

```markdown
---
provider: openai
model: gpt-5.5
temperature: 0.7
---

# Complex Tasks Agent
You handle complex reasoning and creative tasks.
```

## Troubleshooting

### Provider not found

```
Error: Provider not found: openai
```

**Solution**: Ensure the provider name in your agent definition matches a provider in your config.

### Connection timeout

```
Error: Request timed out
```

**Solution**: Check if the provider is running and accessible.

### Authentication error

```
Error: Invalid API key
```

**Solution**: Verify your API key in the config.
