# Architecture

This document describes the system architecture of outo-agentcore.

## High-Level Overview

outo-agentcore is a CLI wrapper around the [agentouto](https://github.com/llaa33219/agentouto) SDK. It handles:

- **Configuration**: JSON-based config with providers, agents, and settings
- **Agent Definitions**: Markdown files with YAML frontmatter
- **Tools**: Custom tools (bash, wiki) using agentouto's `@Tool` decorator
- **Sessions**: JSON-based conversation persistence
- **CLI**: Simple command-line interface

The heavy lifting (agent loops, LLM calls, tool dispatch, parallel execution, streaming, background agents) is all handled by agentouto.

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI Layer                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │   setup   │  │   chat   │  │ sessions │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    outo-agentcore Layer                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Config   │  │  Parser  │  │  Tools   │  │ Sessions │   │
│  │  (JSON)   │  │ (agent   │  │(bash,    │  │  (JSON)  │   │
│  │           │  │  md,     │  │ wiki)    │  │          │   │
│  │           │  │ skills)  │  │          │  │          │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      agentouto SDK                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Agent    │  │ Router   │  │ Runtime  │  │ Context  │   │
│  │  Loop     │  │          │  │          │  │          │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌─────────────────────────┐  │
│  │  Provider │  │   Tool   │  │  Provider Backends      │  │
│  │  Backend  │  │  Dispatch│  │  (OpenAI, Anthropic,   │  │
│  │  (multi)  │  │          │  │   Google, Responses)    │  │
│  └──────────┘  └──────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Components

### CLI (`cli/`)

- **main.py**: Argument parsing and command dispatch
- **cmd_setup.py**: Creates `~/.outoac/config.json`
- **cmd_chat.py**: Loads config, builds agentouto objects, calls `agentouto.run()`
- **cmd_sessions.py**: Lists saved sessions

### Config (`config/`)

- **schema.py**: Dataclasses for config structure
- **loader.py**: JSON load/save

### Parser (`parser/`)

- **agent_md.py**: Parses agent markdown files into dicts
- **skill_md.py**: Discovers and parses skill directories

### Tools (`tools/`)

- **`__init__.py`**: `bash` tool via `@agentouto.Tool`, wiki tool factories

Tools are created using agentouto's `@Tool` decorator or `Tool()` constructor. The SDK automatically generates JSON schemas from function signatures and docstrings.

### Sessions (`sessions/`)

- **manager.py**: JSON-based session persistence

Sessions store agentouto `Message` objects serialized as dicts.

## Data Flow

```
User runs: outoac chat "Hello"
    │
    ▼
cmd_chat.py
    │
    ├── Load config.json
    ├── Parse agent markdown files
    ├── Build agentouto.Provider list
    ├── Build agentouto.Agent list
    ├── Build agentouto.Tool list (bash, wiki?)
    ├── Discover skills → extra_instructions
    ├── Load session history (if --session)
    │
    ▼
agentouto.run(
    message="Hello",
    starting_agents=[entry_agent],
    run_agents=all_agents,
    tools=tools,
    providers=providers,
    history=history,
    extra_instructions=skills_text,
    extra_instructions_scope="all",
)
    │
    ▼
Agent Loop (handled by agentouto SDK)
    │
    ▼
RunResult with output + messages
    │
    ▼
Save session messages to JSON
```

## What AgentOutO Handles

All of these are provided by the agentouto SDK:

- **Agent loops**: LLM call → tool dispatch → recursion → finish
- **Parallel execution**: `asyncio.gather` for concurrent agent calls
- **Provider backends**: OpenAI Chat Completions, OpenAI Responses, Anthropic, Google Gemini
- **Tool schema generation**: Auto JSON schema from Python type hints
- **Message protocol**: Forward/return with call_id tracking
- **Self-summarization**: Auto context summarization at 70% threshold
- **Streaming**: Token-by-token output with `async_run_stream`
- **Background agents**: Isolated loops with message injection
- **Debug mode**: Event logs and call tree traces

## Design Principles

1. **Thin CLI Wrapper**: outo-agentcore handles config, parsing, and persistence. Agent execution is delegated to agentouto.
2. **Markdown-First Agents**: Agent definitions are markdown files with optional YAML frontmatter.
3. **JSON Config**: Simple JSON configuration for providers and settings.
4. **Session Continuity**: Conversations can be resumed across runs.
