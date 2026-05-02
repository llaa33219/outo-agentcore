# outo-agentcore Documentation

<p align="center">
  <img src="../logo.svg" alt="outo-agentcore" width="420">
</p>

<p align="center">
  <strong>CLI agent tool based on <a href="https://github.com/llaa33219/agentouto">agentouto</a> SDK patterns</strong>
</p>

## Table of Contents

- [Getting Started](getting-started.md) - Installation, setup, and first steps
- [Architecture](architecture.md) - System design and component overview
- [Configuration](configuration.md) - Complete configuration reference
- [Agents](agents.md) - Agent system and markdown format
- [Tools](tools.md) - Built-in tools (bash, call_agent, finish, wiki)
- [Sessions](sessions.md) - Session management and persistence
- [Providers](providers.md) - LLM provider integration
- [Wiki Integration](wiki.md) - OutoWiki knowledge base
- [Development](development.md) - Contributing and development guide

## Overview

outo-agentcore is a CLI-based multi-agent system that allows you to define and orchestrate multiple AI agents that can collaborate to solve complex tasks. Each agent can call other agents recursively, execute bash commands, and optionally integrate with a wiki knowledge base.

### Key Features

- **Multi-Agent Architecture**: Define multiple specialized agents that can call each other
- **OpenAI-Compatible**: Works with OpenAI, Anthropic, Gemini, Ollama, LM Studio, vLLM, and more
- **Session Persistence**: Continue conversations across multiple runs
- **Bash Execution**: Built-in shell command tool for system interaction
- **Wiki Knowledge Base**: Optional OutoWiki integration for persistent knowledge management
- **Simple CLI**: Command-line interface without complex TUI dependencies

### Quick Example

```bash
# Setup
outoac setup \
  --base-url http://localhost:11434/v1 \
  --api-key your-key \
  --default-model llama4:scout \
  --agent-md ~/.outoac/agents/main.md

# Chat
outoac chat "What is the capital of France?"

# Continue session
outoac chat "Tell me more" --session <session-id>
```

## License

Apache-2.0
