# Getting Started

This guide will help you install, configure, and start using outo-agentcore.

## Installation

### Using pip

```bash
pip install outo-agentcore
```

### Using uv (recommended)

```bash
uv tool install outo-agentcore
```

### From source

```bash
git clone https://github.com/your-org/outo-agentcore.git
cd outo-agentcore
uv sync
```

## Uninstallation

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

## Initial Setup

### 1. Configure a Provider

First, set up your LLM provider. This example uses Ollama (local):

```bash
outoac setup \
  --base-url http://localhost:11434/v1 \
  --api-key your-key \
  --default-model llama4:scout
```

For OpenAI:

```bash
outoac setup \
  --base-url https://api.openai.com/v1 \
  --api-key sk-xxx \
  --default-model gpt-4o
```

### 2. Create Agent Definitions

Create a directory for your agents:

```bash
mkdir -p ~/.outoac/agents
```

Create a main agent definition file:

```bash
cat > ~/.outoac/agents/main.md << 'EOF'
# Coordinator

You are a helpful assistant that coordinates work between specialized agents.

When you receive a task:
1. Analyze what needs to be done
2. Delegate to appropriate specialized agents
3. Combine results into a coherent response

You can call other agents using the call_agent tool.
EOF
```

### 3. Link the Agent

```bash
outoac setup --agent-md ~/.outoac/agents/main.md --default-agent main
```

### 4. Start Chatting

```bash
outoac chat "Hello, what can you help me with?"
```

## Creating Multiple Agents

You can define multiple specialized agents:

```bash
# Researcher agent
cat > ~/.outoac/agents/researcher.md << 'EOF'
# Researcher

You are a research specialist. Your job is to:
- Find accurate information
- Verify facts from multiple sources
- Organize findings clearly
EOF

# Writer agent
cat > ~/.outoac/agents/writer.md << 'EOF'
# Writer

You are a technical writer. Your job is to:
- Create clear, well-structured documentation
- Use appropriate formatting
- Ensure accuracy and completeness
EOF
```

Update your config to include all agents:

```bash
outoac setup --agent-md ~/.outoac/agents/main.md
```

Now your main agent can call other agents:

```bash
outoac chat "Research the latest AI developments and write a summary"
```

## Command Reference

### `outoac setup`

Configure providers and agents.

```bash
outoac setup [OPTIONS]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--base-url` | Provider API base URL | - |
| `--api-key` | API key for provider | - |
| `--default-model` | Default model for provider | - |
| `--provider-name` | Provider name | `default` |
| `--agent-md` | Path to main agent markdown file | - |
| `--default-agent` | Default agent name | `main` |

### `outoac chat`

Start or continue a chat session.

```bash
outoac chat "message" [OPTIONS]
```

| Option | Description | Default |
|--------|-------------|---------|
| `message` | Message to send (required) | - |
| `--session`, `-s` | Session ID to continue | - |
| `--agent`, `-a` | Agent name to use | `main` |
| `--max-messages`, `-m` | Max recent messages to attach from session | - |
| `--debug` | Enable debug output | `false` |

### `outoac sessions`

List all sessions.

```bash
outoac sessions [OPTIONS]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--limit` | Max sessions to show | `10` |

## Next Steps

- Learn about [Agent Definitions](agents.md) to create sophisticated agent workflows
- Explore [Tools](tools.md) to understand what agents can do
- Read [Configuration](configuration.md) for advanced settings
- Enable [Wiki Integration](wiki.md) for persistent knowledge management
