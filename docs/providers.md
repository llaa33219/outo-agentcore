# Provider Integration

This document describes how to configure and use different LLM providers with outo-agentcore.

## Provider Overview

Providers are LLM backends that agents use to generate responses. outo-agentcore supports any OpenAI-compatible API through the `openai` provider kind.

## Supported Providers

| Provider | Base URL | Default Model | Notes |
|----------|----------|---------------|-------|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o` | Official OpenAI API |
| Anthropic | `https://api.anthropic.com/v1` | `claude-3-opus-20240229` | Via OpenAI-compatible proxy |
| Google Gemini | `https://generativelanguage.googleapis.com/v1beta` | `gemini-pro` | Via OpenAI-compatible proxy |
| Ollama | `http://localhost:11434/v1` | `llama3` | Local inference |
| LM Studio | `http://localhost:1234/v1` | (varies) | Local inference |
| vLLM | `http://localhost:8000/v1` | (varies) | Local inference |
| LiteLLM | `http://localhost:4000/v1` | (varies) | Proxy for multiple providers |

## Provider Configuration

### Basic Structure

```json
{
  "providers": {
    "provider_name": {
      "kind": "openai",
      "base_url": "https://api.openai.com/v1",
      "api_key": "sk-xxx",
      "default_model": "gpt-4o",
      "max_output_tokens": 0
    }
  }
}
```

### Configuration Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `kind` | string | Yes | Provider backend type (currently only `openai`) |
| `base_url` | string | Yes | API endpoint URL |
| `api_key` | string | Yes | API authentication key |
| `default_model` | string | Yes | Default model for agents |
| `max_output_tokens` | integer | No | Max output tokens (0 = auto-detect) |

## Provider Setup Examples

### OpenAI

```bash
outoac setup \
  --base-url https://api.openai.com/v1 \
  --api-key sk-xxx \
  --default-model gpt-4o \
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
      "default_model": "gpt-4o",
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
  --default-model llama3 \
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
      "default_model": "llama3",
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

### Anthropic (via Proxy)

Since Anthropic uses a different API format, use a proxy like LiteLLM:

```bash
# Start LiteLLM proxy
litellm --model claude-3-opus-20240229

# Setup outo-agentcore
outoac setup \
  --base-url http://localhost:4000/v1 \
  --api-key your-anthropic-key \
  --default-model claude-3-opus-20240229 \
  --provider-name anthropic
```

### Google Gemini (via Proxy)

```bash
# Start LiteLLM proxy
litellm --model gemini-pro

# Setup outo-agentcore
outoac setup \
  --base-url http://localhost:4000/v1 \
  --api-key your-google-key \
  --default-model gemini-pro \
  --provider-name google
```

## Multi-Provider Setup

Configure multiple providers for different use cases:

```json
{
  "providers": {
    "local": {
      "kind": "openai",
      "base_url": "http://localhost:11434/v1",
      "api_key": "ollama",
      "default_model": "llama3",
      "max_output_tokens": 0
    },
    "openai": {
      "kind": "openai",
      "base_url": "https://api.openai.com/v1",
      "api_key": "sk-xxx",
      "default_model": "gpt-4o",
      "max_output_tokens": 0
    }
  },
  "agents": {
    "main": "~/.outoac/agents/main.md",
    "researcher": "~/.outoac/agents/researcher.md"
  }
}
```

Use different providers for different agents:

```markdown
---
provider: local
model: llama3
---

# Main Agent
You coordinate work using local models.
```

```markdown
---
provider: openai
model: gpt-4o
---

# Researcher
You research using powerful cloud models.
```

## Token Management

### Auto-Detection

When `max_output_tokens` is `0`, the system automatically retrieves the optimal value from the [LCW API](https://lcw-api.blp.sh/context-window):

```python
def get_max_output_tokens(model: str, configured_tokens: int | None) -> int:
    if configured_tokens and configured_tokens > 0:
        return configured_tokens
    try:
        url = f"https://lcw-api.blp.sh/context-window?model={model}"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read())
            if data.get("success"):
                return data["data"]["maxOutputTokens"]
    except Exception:
        pass
    return 4000  # Fallback default
```

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
      "default_model": "llama3",
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

## Provider Backend Architecture

### Backend Interface

```python
class ProviderBackend(ABC):
    @abstractmethod
    async def call(
        self,
        context: Context,
        tools: list[dict],
        agent: Agent,
        provider: Provider,
    ) -> LLMResponse
```

### OpenAI Backend

The `OpenAIBackend` handles:

1. **Client Management**: Caches `AsyncOpenAI` clients per provider
2. **Message Conversion**: Converts `Context` to OpenAI message format
3. **Tool Schema Conversion**: Converts tool schemas to OpenAI format
4. **API Calls**: Makes async calls to OpenAI-compatible APIs
5. **Response Parsing**: Parses responses into `LLMResponse`

```python
class OpenAIBackend(ProviderBackend):
    def __init__(self) -> None:
        self._clients: dict[str, AsyncOpenAI] = {}

    def _get_client(self, provider: Provider) -> AsyncOpenAI:
        key = (provider.api_key, provider.name)
        if key not in self._clients:
            kwargs: dict[str, Any] = {"api_key": provider.api_key}
            if provider.base_url:
                kwargs["base_url"] = provider.base_url
            self._clients[key] = AsyncOpenAI(**kwargs)
        return self._clients[key]
```

### Message Format Conversion

Context messages are converted to OpenAI format:

```python
def _build_messages(context: Context) -> list[dict]:
    messages = [{"role": "system", "content": context.system_prompt}]
    
    for msg in context.messages:
        if msg.role == "user":
            messages.append({"role": "user", "content": msg.content})
        elif msg.role == "assistant":
            if msg.tool_calls:
                # Include tool calls
                openai_tc = []
                for tc in msg.tool_calls:
                    openai_tc.append({
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": json.dumps(tc.arguments),
                        },
                    })
                entry = {"role": "assistant", "tool_calls": openai_tc}
                if msg.content:
                    entry["content"] = msg.content
                messages.append(entry)
            else:
                messages.append({"role": "assistant", "content": msg.content})
        elif msg.role == "tool":
            messages.append({
                "role": "tool",
                "tool_call_id": msg.tool_call_id,
                "content": msg.content,
            })
    
    return messages
```

## Error Handling

### Common Errors

**Authentication Error**:
```
Error: Invalid API key
```
**Solution**: Check your API key in the config.

**Connection Error**:
```
Error: Connection refused
```
**Solution**: Ensure the provider is running and accessible.

**Model Not Found**:
```
Error: Model not found
```
**Solution**: Check the model name and provider availability.

**Rate Limiting**:
```
Error: Rate limit exceeded
```
**Solution**: Wait and retry, or upgrade your API plan.

## Best Practices

### 1. Use Local Models for Development

```json
{
  "providers": {
    "local": {
      "kind": "openai",
      "base_url": "http://localhost:11434/v1",
      "api_key": "ollama",
      "default_model": "llama3"
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
      "default_model": "gpt-4o"
    }
  }
}
```

### 3. Match Models to Tasks

```markdown
---
provider: local
model: llama3
temperature: 0.2
---

# Simple Tasks Agent
You handle simple, factual tasks.
```

```markdown
---
provider: openai
model: gpt-4o
temperature: 0.7
---

# Complex Tasks Agent
You handle complex reasoning and creative tasks.
```

### 4. Set Appropriate Token Limits

```markdown
---
max_output_tokens: 2000
---

# Concise Agent
You provide brief, focused responses.
```

```markdown
---
max_output_tokens: 8000
---

# Detailed Agent
You provide comprehensive, detailed responses.
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

**Solution**: 
- Check if the provider is running
- Verify the base URL is correct
- Check network connectivity

### Invalid response format

```
Error: Invalid response from provider
```

**Solution**: Ensure the provider is OpenAI-compatible. Some providers may need a proxy.

### Token limit exceeded

```
Error: Maximum context length exceeded
```

**Solution**:
- Reduce `max_output_tokens`
- Use `--max-messages` to limit session history
- Use a model with larger context window
