# outo-agentcore

<p align="center">
  <img src="logo.svg" alt="outo-agentcore" width="420">
</p>

<p align="center">
  <strong>CLI agent tool powered by <a href="https://github.com/llaa33219/agentouto">agentouto</a> SDK</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/outo-agentcore/">PyPI</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#cli-commands">CLI</a> •
  <a href="#development">Development</a>
</p>

## Features

- **Powered by agentouto**: Full peer-to-peer multi-agent SDK with parallel execution, streaming, background agents
- **Agent support**: Agents call each other recursively with no orchestrator
- **Skills support**: [Agent Skills specification](https://agentskills.io/specification) compliant - reusable instruction packages
- **Multi-provider**: OpenAI, Anthropic, Google Gemini, and any OpenAI-compatible API (Ollama, vLLM, LM Studio, etc.)
- **Session persistence**: Continue conversations across runs
- **Bash execution**: Built-in shell command tool
- **Wiki knowledge base**: Optional [OutoWiki](https://github.com/llaa33219/outowiki) integration for persistent knowledge management
- **Simple CLI**: No complex TUI, just commands

## Installation

```bash
# pip
pip install outo-agentcore

# uv (recommended)
uv tool install outo-agentcore
```

## Uninstall

```bash
# pip
pip uninstall outo-agentcore

# uv
uv tool uninstall outo-agentcore
```

To remove all data:

```bash
rm -rf ~/.outoac
```

## Quick Start

### 1. Setup

```bash
outoac setup \
  --base-url http://localhost:11434/v1 \
  --api-key your-key \
  --default-model llama4:scout \
  --agent-md ~/.outoac/agents/main.md \
  --default-agent main
```

### 2. Create agent definitions

```bash
mkdir -p ~/.outoac/agents
```

Create `~/.outoac/agents/main.md`:

```markdown
# Coordinator

You coordinate work. Call other agents when needed.
```

Create `~/.outoac/agents/researcher.md`:

```markdown
# Researcher

You find and organize information from the web.
```

Create `~/.outoac/agents/writer.md`:

```markdown
# Writer

You create well-structured reports from research.
```

### 3. Start chatting

```bash
outoac chat "What is the capital of France?"
```

### 4. Continue a session

```bash
outoac sessions                    # List sessions
outoac chat "Tell me more" --session <session-id>
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `outoac setup` | Configure providers and agents |
| `outoac chat "message"` | Start a chat session |
| `outoac chat "message" --session <id>` | Continue existing session |
| `outoac chat "message" --agent <name>` | Use specific agent |
| `outoac sessions` | List all sessions |

### Setup Options

| Argument | Description | Default | Example |
|----------|-------------|---------|---------|
| `--base-url` | Provider API base URL | - | `http://localhost:11434/v1` |
| `--api-key` | API key for provider | - | `sk-xxx` |
| `--default-model` | Default model for provider | - | `llama4:scout` |
| `--provider-name` | Provider name | `default` | `openai` |
| `--agent-md` | Path to main agent markdown | - | `~/.outoac/agents/main.md` |
| `--default-agent` | Default agent for chat | `main` | `researcher` |

### Chat Options

| Argument | Description | Default | Example |
|----------|-------------|---------|---------|
| `message` | Message to send (required) | - | `"Hello"` |
| `--session`, `-s` | Session ID to continue | - | `a1b2c3d4...` |
| `--agent`, `-a` | Agent name to use | `main` | `researcher` |
| `--debug` | Enable debug output | `false` | - |

### Sessions Options

| Argument | Description | Default | Example |
|----------|-------------|---------|---------|
| `--limit` | Max sessions to show | `10` | `20` |

## Configuration

Config file: `~/.outoac/config.json`

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
    "writer": "~/.outoac/agents/writer.md",
    "reviewer": "~/.outoac/agents/reviewer.md",
    "coder": "~/.outoac/agents/coder.md",
    "tester": "~/.outoac/agents/tester.md"
  },
  "default_agent": "main",
  "skills_dir": "~/.outoac/skills/",
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

### Provider Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `kind` | Provider type (openai, anthropic) | `openai` |
| `base_url` | API endpoint URL | - |
| `api_key` | API key for authentication | - |
| `default_model` | Default model for agents | - |
| `max_output_tokens` | Default max output tokens (auto-detected if 0) | `0` |

**Note**: If `max_output_tokens` is `0` or not set, the system automatically retrieves the optimal value from the [LCW API](https://lcw-api.blp.sh/context-window). Agent-level settings override provider defaults.

### Wiki Settings

| Parameter | Description | Default |
|-----------|-------------|---------|
| `enabled` | Enable wiki knowledge base tools | `false` |
| `wiki_path` | Path to wiki directory | `~/.outoac/wiki/` |
| `provider` | LLM provider for wiki operations | `openai` |
| `model` | Model for wiki analysis | (empty, uses provider default) |
| `api_key` | API key for wiki provider | (empty, uses provider key) |
| `base_url` | Base URL for wiki provider | (empty, uses provider URL) |
| `max_output_tokens` | Max tokens for wiki responses (auto-detected if not set) | `0` (auto) |
| `debug` | Enable wiki debug logging | `false` |

**Note**: If `max_output_tokens` is `0` or not set, the system automatically retrieves the optimal value from the [LCW API](https://lcw-api.blp.sh/context-window).

## Agent Markdown Format

Agent definitions use markdown with optional YAML frontmatter:

```markdown
---
model: MiniMax-M2.7
provider: default
temperature: 1
max_output_tokens: 4000
---

# Research Agent

You are a research specialist. Your job is to find information
and provide detailed analysis.
```

**Frontmatter fields**:
- `model`: Model name (overrides provider default)
- `provider`: Provider name to use
- `temperature`: Sampling temperature (0.0-2.0)
- `max_output_tokens`: Maximum output tokens (auto-detected if not set)

**Body**:
- First `#` heading becomes the agent's role
- Rest becomes the agent's instructions

**Note**: If `max_output_tokens` is not set, the system automatically retrieves the optimal value from the [LCW API](https://lcw-api.blp.sh/context-window).

## Agent Example

Create multiple agents:

`~/.outoac/agents/main.md`:
```markdown
# Coordinator

You coordinate work. Call other agents when needed.
```

`~/.outoac/agents/researcher.md`:
```markdown
# Researcher

You find and organize information from the web.
```

`~/.outoac/agents/writer.md`:
```markdown
# Writer

You create well-structured reports from research.
```

Setup with all agents:
```bash
outoac setup \
  --base-url http://localhost:11434/v1 \
  --api-key your-key \
  --default-model llama4:scout \
  --agent-md ~/.outoac/agents/main.md \
  --default-agent main
```

Now main agent can call researcher and writer using `call_agent` tool.

## Supported Providers

| Provider | Base URL | Default Model |
|----------|----------|---------------|
| OpenAI | `https://api.openai.com/v1` | `gpt-5.5` |
| Anthropic | `https://api.anthropic.com/v1` | `claude-sonnet-4-6` |
| Google Gemini | `https://generativelanguage.googleapis.com/v1beta` | `gemini-3-1-pro` |
| Ollama | `http://localhost:11434/v1` | `llama4:scout` |
| LM Studio | `http://localhost:1234/v1` | (local model) |
| vLLM | `http://localhost:8000/v1` | (local model) |

## Wiki Integration

Outo-agentcore integrates with [OutoWiki](https://github.com/llaa33219/outowiki) for persistent knowledge management. When enabled, agents can record and search information across conversations.

### Enable Wiki

Add to `~/.outoac/config.json`:

```json
{
  "wiki": {
    "enabled": true,
    "provider": "openai",
    "model": "gpt-5.5",
    "api_key": "sk-..."
  }
}
```

**Note**: If the `wiki` section is not present in the config, wiki features are disabled by default.

### Wiki Tools

When enabled, agents have access to:

- **`wiki_record`**: Save information to the wiki for future reference
- **`wiki_search`**: Search the wiki for relevant knowledge

### Use Cases

- Remember user preferences across sessions
- Build a knowledge base from conversations
- Search for previously discussed topics
- Maintain context for long-running projects

## Skills

Skills are reusable instruction packages that extend agent capabilities. They follow the [Agent Skills specification](https://agentskills.io/specification).

### Creating Skills

```bash
mkdir -p ~/.outoac/skills/my-skill
```

Create `~/.outoac/skills/my-skill/SKILL.md`:

```markdown
---
name: my-skill
description: What this skill does and when to use it.
---

# Instructions

Your detailed instructions go here...
```

### How Skills Work

- Skills are automatically discovered from `~/.outoac/skills/`
- Agents see all available skills in their system prompt
- Agents automatically activate skills based on task description
- Skills are loaded progressively (metadata → instructions → resources)

See [Skills Documentation](docs/skills.md) for details.

## Built-in Tools

| Tool | Description |
|------|-------------|
| `bash` | Execute shell commands |
| `call_agent` | Call another agent |
| `finish` | Return final result |
| `wiki_record` | Record information to wiki (when enabled) |
| `wiki_search` | Search wiki knowledge base (when enabled) |

## Directory Structure

```
~/.outoac/
├── config.json          # Provider and agent settings
├── agents/              # Agent markdown definitions
│   ├── main.md
│   ├── researcher.md
│   ├── writer.md
│   ├── reviewer.md
│   ├── coder.md
│   └── tester.md
├── skills/              # Skill definitions (Agent Skills spec)
│   ├── code-review/
│   │   └── SKILL.md
│   └── git-workflow/
│       └── SKILL.md
├── sessions/            # Session persistence
│   └── <session-id>.json
└── wiki/                # Wiki knowledge base (when enabled)
    └── *.md             # Wiki documents
```

## Development

```bash
# Clone
git clone <repo-url>
cd outo-agentcore

# Install dependencies
uv sync

# Run tests
uv run pytest tests/ -v

# Run CLI
uv run python -m outoac --help
```

## License

Apache-2.0
