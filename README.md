# outo-agentcore

<p align="center">
  <img src="logo.svg" alt="outo-agentcore" width="420">
</p>

<p align="center">
  <strong>CLI agent tool based on <a href="https://github.com/llaa33219/agentouto">agentouto</a> SDK patterns</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/outo-agentcore/">PyPI</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#cli-commands">CLI</a> •
  <a href="#development">Development</a>
</p>

## Features

- **Agent support**: Agents can call each other recursively
- **OpenAI-compatible**: Works with OpenAI, MiniMax, Ollama, LM Studio, vLLM, etc.
- **Session persistence**: Continue conversations across runs
- **Bash execution**: Built-in shell command tool
- **Simple CLI**: No complex TUI, just commands

## Installation

```bash
pip install outo-agentcore
```

## Quick Start

### 1. Setup

```bash
outoac setup \
  --base-url http://localhost:11434/v1 \
  --api-key your-key \
  --model llama3 \
  --agent-md ~/.outoac/agents/main.md \
  --sub-agents researcher writer reviewer coder tester
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
| `--base-url` | Provider API base URL | - | `https://api.minimax.io/v1` |
| `--api-key` | API key for provider | - | `sk-xxx` |
| `--model` | Default model name | - | `MiniMax-M2.7` |
| `--provider-name` | Provider name | `default` | `openai` |
| `--agent-md` | Path to main agent markdown | - | `~/.outoac/agents/main.md` |
| `--sub-agents` | Sub-agent names | - | `researcher writer reviewer` |

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
      "model": "llama3"
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
  "sub_agents": ["researcher", "writer", "reviewer", "coder", "tester"],
  "skills_dir": "~/.outoac/skills/"
}
```

## Agent Markdown Format

Agent definitions use markdown with optional YAML frontmatter:

```markdown
---
model: MiniMax-M2.7
provider: default
temperature: 1
---

# Research Agent

You are a research specialist. Your job is to find information
and provide detailed analysis.
```

**Frontmatter fields**:
- `model`: Model name (overrides provider default)
- `provider`: Provider name to use
- `temperature`: Sampling temperature (0.0-2.0)

**Body**:
- First `#` heading becomes the agent's role
- Rest becomes the agent's instructions

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
  --model llama3 \
  --agent-md ~/.outoac/agents/main.md \
  --sub-agents researcher writer
```

Now main agent can call researcher and writer using `call_agent` tool.

## Built-in Tools

| Tool | Description |
|------|-------------|
| `bash` | Execute shell commands |
| `call_agent` | Call another agent |
| `finish` | Return final result |

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
├── skills/              # Skill definitions (future)
└── sessions/            # Session persistence
    └── <session-id>.json
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
