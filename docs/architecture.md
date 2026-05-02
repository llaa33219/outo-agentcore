# Architecture

This document describes the system architecture and design principles of outo-agentcore.

## High-Level Overview

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
│                      Core Layer                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Router   │  │ Runtime  │  │  Agent   │  │ Context  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  Provider │  │   Tool   │  │ Message  │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Provider Layer                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                OpenAI Backend                         │  │
│  │  (OpenAI, Anthropic, Gemini, Ollama, LM Studio...)   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### Agent (`core/agent.py`)

The fundamental unit of work. Each agent has:

- **name**: Unique identifier
- **instructions**: System prompt defining behavior
- **model**: LLM model to use
- **provider**: Which provider backend to use
- **role**: Optional short role description
- **temperature**: Sampling temperature (0.0-2.0)
- **max_output_tokens**: Maximum output tokens

```python
@dataclass
class Agent:
    name: str
    instructions: str
    model: str
    provider: str
    role: str | None = None
    max_output_tokens: int | None = None
    temperature: float = 1.0
    context_window: int | None = None
```

### Router (`core/router.py`)

The routing layer that:

1. Manages agent, provider, and tool registries
2. Builds system prompts for agents
3. Constructs tool schemas for LLM calls
4. Routes LLM calls to the appropriate provider backend

```python
class Router:
    def __init__(self, agents: list[Agent], tools: list, providers: list[Provider])
    def get_agent(self, name: str) -> Agent
    def get_provider(self, name: str) -> Provider
    def get_tool(self, name: str)
    def build_system_prompt(self, agent: Agent, caller: str | None = None) -> str
    def build_tool_schemas(self, current_agent: str) -> list[dict]
    async def call_llm(self, agent: Agent, context: Context, tool_schemas: list[dict]) -> LLMResponse
```

### Runtime (`core/runtime.py`)

The execution engine that:

1. Manages the agent execution loop
2. Handles tool call dispatch
3. Manages agent-to-agent delegation
4. Tracks message history

```python
class Runtime:
    def __init__(self, router: Router)
    async def execute(self, forward_message: str, agent: Agent, history: list[dict] | None = None) -> RunResult
```

**Execution Flow**:
1. User sends message to entry agent
2. Runtime creates context with system prompt
3. LLM is called with context and available tools
4. If LLM returns tool calls:
   - `call_agent`: Recursively execute target agent
   - `bash`: Execute shell command
   - `finish`: Return result to caller
   - Other tools: Execute and return result
5. If LLM returns text (no tools): Nudge to use `finish` tool
6. Loop continues until `finish` is called

### Context (`core/context.py`)

Manages the conversation context for LLM calls:

```python
class Context:
    def __init__(self, system_prompt: str)
    def add_user(self, content: str) -> None
    def add_assistant_text(self, content: str) -> None
    def add_assistant_tool_calls(self, tool_calls: list[ToolCall], content: str | None = None) -> None
    def add_tool_result(self, tool_call_id: str, tool_name: str, content: str) -> None
    def add_history(self, history: list[dict]) -> None
```

### Message (`core/message.py`)

Represents a message in the agent communication protocol:

```python
@dataclass
class Message:
    type: Literal["forward", "return"]  # Direction of message
    sender: str                          # Who sent the message
    receiver: str                        # Who receives the message
    content: str                         # Message content
    call_id: str                         # Unique call identifier
```

**Message Types**:
- `forward`: Message from caller to callee
- `return`: Message from callee to caller

### Provider (`core/provider.py`)

Represents an LLM provider configuration:

```python
@dataclass
class Provider:
    name: str
    kind: str        # "openai" (currently only supported)
    api_key: str
    base_url: str | None = None
```

### Tool (`core/tool.py`)

Base tool interface and built-in implementations:

```python
@dataclass
class ToolResult:
    content: str

class BashTool:
    name = "bash"
    async def execute(self, command: str) -> ToolResult
```

## Data Flow

### Single Agent Call

```
User Message
     │
     ▼
┌─────────┐
│ Runtime  │
└────┬────┘
     │
     ▼
┌─────────┐
│ Context  │ ← System Prompt + Message
└────┬────┘
     │
     ▼
┌─────────┐
│  Router  │ ← Selects Provider
└────┬────┘
     │
     ▼
┌─────────┐
│ Provider │ ← Calls LLM API
└────┬────┘
     │
     ▼
┌─────────┐
│ Response │ ← Tool Calls or Text
└────┬────┘
     │
     ├─→ finish → Return to User
     ├─→ bash → Execute → Loop
     └─→ call_agent → Recursive Call
```

### Multi-Agent Delegation

```
User → Main Agent
           │
           ├─→ call_agent("researcher", "Find info")
           │         │
           │         ▼
           │    Researcher Agent
           │         │
           │         ├─→ bash("curl ...")
           │         │
           │         └─→ finish("Found: ...")
           │
           ├─→ call_agent("writer", "Write report")
           │         │
           │         ▼
           │    Writer Agent
           │         │
           │         └─→ finish("Report: ...")
           │
           └─→ finish("Combined results: ...")
```

## System Prompt Construction

The Router builds system prompts dynamically:

```
You are "agent_name". [Role or first 50 chars of instructions]

INSTRUCTIONS:
[Full instructions from agent definition]

INVOKED BY: You have been called by 'caller_name'.
Consider their request carefully and fulfill it.

Available agents:
- agent1: Role description
- agent2: Role description

Available tools:
- bash: Execute a bash command and return its output.
- call_agent: Call another agent.
- finish: Return your final result to the caller.

IMPORTANT: You MUST call the finish tool to return your final result.
Plain text responses are NOT delivered to the caller.
Use call_agent to delegate work to other agents.
```

## Provider Backend System

Providers are implemented as backends:

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

Currently implemented:
- `OpenAIBackend`: Works with any OpenAI-compatible API

The backend:
1. Converts Context to provider-specific message format
2. Converts tool schemas to provider-specific format
3. Makes API call
4. Parses response into `LLMResponse`

## Session Persistence

Sessions are stored as JSON files in `~/.outoac/sessions/`:

```json
{
  "session_id": "abc123...",
  "created_at": "2024-01-01T00:00:00Z",
  "agent_name": "main",
  "messages": [
    {
      "type": "forward",
      "sender": "user",
      "receiver": "main",
      "content": "Hello",
      "call_id": "xyz789..."
    },
    {
      "type": "return",
      "sender": "main",
      "receiver": "user",
      "content": "Hi there!",
      "call_id": "xyz789..."
    }
  ]
}
```

## Error Handling

- `RoutingError`: Raised when agent, provider, or tool not found
- `SessionLoadError`: Raised when session file is corrupted
- Provider errors: Propagated from LLM API calls
- Tool errors: Caught and returned as tool results

## Design Principles

1. **Separation of Concerns**: Each component has a single responsibility
2. **Provider Agnostic**: Core logic doesn't depend on specific LLM providers
3. **Recursive Delegation**: Agents can call other agents without depth limits
4. **Explicit Results**: Agents must use `finish` tool to return results
5. **Session Continuity**: Conversations can be resumed across runs
