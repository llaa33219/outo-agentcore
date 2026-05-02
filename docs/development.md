# Development Guide

This guide covers setting up the development environment, understanding the codebase, and contributing to outo-agentcore.

## Development Setup

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Git

### Clone Repository

```bash
git clone https://github.com/your-org/outo-agentcore.git
cd outo-agentcore
```

### Install Dependencies

Using uv (recommended):

```bash
uv sync
```

Using pip:

```bash
pip install -e ".[dev]"
```

### Verify Installation

```bash
uv run python -m outo_agentcore --help
```

## Project Structure

```
outo-agentcore/
├── src/
│   └── outo_agentcore/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── main.py
│       │   ├── cmd_chat.py
│       │   ├── cmd_setup.py
│       │   └── cmd_sessions.py
│       ├── config/
│       │   ├── __init__.py
│       │   ├── loader.py
│       │   └── schema.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── agent.py
│       │   ├── context.py
│       │   ├── message.py
│       │   ├── provider.py
│       │   ├── router.py
│       │   ├── runtime.py
│       │   ├── token_utils.py
│       │   └── wiki_tools.py
│       ├── parser/
│       │   ├── __init__.py
│       │   └── agent_md.py
│       ├── providers/
│       │   ├── __init__.py
│       │   └── openai.py
│       └── sessions/
│           ├── __init__.py
│           └── manager.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_agent.py
│   ├── test_agent_md.py
│   ├── test_bash_tool.py
│   ├── test_config.py
│   ├── test_context.py
│   ├── test_integration.py
│   ├── test_message.py
│   ├── test_openai_provider.py
│   ├── test_provider.py
│   ├── test_providers.py
│   ├── test_router.py
│   ├── test_runtime.py
│   ├── test_sessions.py
│   └── test_tool.py
├── docs/
├── pyproject.toml
├── README.md
└── uv.lock
```

## Running Tests

### Run All Tests

```bash
uv run pytest tests/ -v
```

### Run Specific Test File

```bash
uv run pytest tests/test_runtime.py -v
```

### Run with Coverage

```bash
uv run pytest tests/ --cov=outo_agentcore --cov-report=html
```

### Run Async Tests

Tests use `pytest-asyncio` with `asyncio_mode = "auto"`:

```python
@pytest.mark.asyncio
async def test_execute_simple_finish():
    # Test code here
    pass
```

## Code Architecture

### Core Components

1. **Agent** (`core/agent.py`): Data class representing an agent
2. **Router** (`core/router.py`): Routes calls between agents, providers, and tools
3. **Runtime** (`core/runtime.py`): Executes agent loops and manages tool calls
4. **Context** (`core/context.py`): Manages conversation context for LLM calls
5. **Message** (`core/message.py`): Represents agent-to-agent messages
6. **Provider** (`core/provider.py`): Provider configuration
7. **Tool** (`core/tool.py`): Base tool interface and implementations

### Data Flow

```
User Input
    │
    ▼
CLI (cmd_chat.py)
    │
    ▼
Runtime.execute()
    │
    ▼
Router.call_llm()
    │
    ▼
Provider Backend (openai.py)
    │
    ▼
LLM API
    │
    ▼
Response Parsing
    │
    ▼
Tool Execution (if needed)
    │
    ▼
Result Return
```

## Adding New Features

### Adding a New Tool

1. Create tool class in `core/tool.py` or new file:

```python
class MyTool:
    name = "my_tool"
    description = "Description of what the tool does"

    def to_schema(self) -> dict[str, Any]:
        return {
            "name": "my_tool",
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "Parameter description"
                    }
                },
                "required": ["param1"]
            }
        }

    async def execute(self, param1: str) -> ToolResult:
        # Implementation
        return ToolResult(content="Result")
```

2. Register tool in `cmd_chat.py`:

```python
tools = [BashTool(), MyTool()]
```

3. Add tool description to system prompt in `router.py`:

```python
parts.append("- my_tool: Description of what the tool does.")
```

### Adding a New Provider Backend

1. Create backend class in `providers/`:

```python
class MyBackend(ProviderBackend):
    async def call(
        self,
        context: Context,
        tools: list[dict],
        agent: Agent,
        provider: Provider,
    ) -> LLMResponse:
        # Implementation
        pass
```

2. Register in `providers/__init__.py`:

```python
def get_backend(kind: str) -> ProviderBackend:
    if kind == "openai":
        from outo_agentcore.providers.openai import OpenAIBackend
        return OpenAIBackend()
    if kind == "my_provider":
        from outo_agentcore.providers.my_provider import MyBackend
        return MyBackend()
    raise ValueError(f"Unknown provider backend: {kind}")
```

### Adding a New CLI Command

1. Create command file in `cli/`:

```python
# cli/cmd_mycommand.py
def cmd_mycommand(args):
    # Implementation
    pass
```

2. Register in `cli/main.py`:

```python
# Add subparser
mycommand_parser = subparsers.add_parser("mycommand", help="My command help")
mycommand_parser.add_argument("--option", help="Option help")

# Add to command dispatch
elif args.command == "mycommand":
    from outo_agentcore.cli.cmd_mycommand import cmd_mycommand
    cmd_mycommand(args)
```

## Testing

### Test Structure

Tests are organized by component:

- `test_agent.py`: Agent data class tests
- `test_context.py`: Context management tests
- `test_message.py`: Message format tests
- `test_provider.py`: Provider configuration tests
- `test_router.py`: Router logic tests
- `test_runtime.py`: Runtime execution tests
- `test_sessions.py`: Session persistence tests
- `test_tool.py`: Tool execution tests
- `test_integration.py`: End-to-end integration tests

### Writing Tests

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from outo_agentcore.core.runtime import Runtime, RunResult
from outo_agentcore.core.router import Router
from outo_agentcore.core.agent import Agent
from outo_agentcore.core.provider import Provider
from outo_agentcore.core.tool import BashTool
from outo_agentcore.providers import LLMResponse, ProviderBackend

class FakeBackend(ProviderBackend):
    def __init__(self, responses):
        self._responses = list(responses)
        self._call_count = 0
    
    async def call(self, context, tools, agent, provider):
        resp = self._responses[self._call_count]
        self._call_count += 1
        return resp

@pytest.mark.asyncio
async def test_execute_simple_finish():
    """Agent calls finish immediately."""
    agent = Agent(name="main", instructions="test", model="gpt-4", provider="openai")
    provider = Provider(name="openai", kind="openai")
    
    backend = FakeBackend([
        LLMResponse(tool_calls=[ToolCall(id="tc1", name="finish", arguments={"message": "Hello!"})])
    ])
    
    router = Router([agent], [BashTool()], [provider])
    with patch("outo_agentcore.core.router.get_backend", return_value=backend):
        runtime = Runtime(router)
        result = await runtime.execute("Hi", agent)
    
    assert result.output == "Hello!"
    assert len(result.messages) == 2
```

### Mocking Guidelines

- Mock external dependencies (LLM APIs, file system)
- Use `FakeBackend` for provider tests
- Use `AsyncMock` for async functions
- Use `patch` for module-level dependencies

## Code Style

### Formatting

- Follow PEP 8
- Use type hints
- Use dataclasses for data structures
- Use async/await for async operations

### Naming Conventions

- **Classes**: PascalCase (`Agent`, `Router`, `Runtime`)
- **Functions**: snake_case (`execute`, `call_llm`, `build_system_prompt`)
- **Variables**: snake_case (`agent_name`, `tool_schemas`)
- **Constants**: UPPER_CASE (`CALL_AGENT`, `FINISH`)

### Documentation

- Use docstrings for public functions
- Use comments for complex logic
- Keep README and docs updated

## Debugging

### Enable Debug Output

```bash
outoac chat "message" --debug
```

### Debug Logging

Add debug logging in your code:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### Common Issues

**Import Errors**:
```bash
# Ensure package is installed in development mode
uv sync
```

**Test Failures**:
```bash
# Run specific test with verbose output
uv run pytest tests/test_runtime.py -v -s
```

**Async Issues**:
```bash
# Ensure pytest-asyncio is installed
uv add --dev pytest-asyncio
```

## Contributing

### Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run tests
6. Submit a pull request

### Commit Messages

Use conventional commits:

```
feat: Add new feature
fix: Fix bug
docs: Update documentation
test: Add tests
refactor: Refactor code
```

### Pull Request Guidelines

- Include description of changes
- Reference related issues
- Ensure all tests pass
- Update documentation if needed

## Release Process

### Version Bumping

Update version in `pyproject.toml`:

```toml
[project]
version = "0.2.0"
```

### Building

```bash
uv build
```

### Publishing

```bash
uv publish
```

## Dependencies

### Core Dependencies

- `openai>=1.50.0`: OpenAI API client
- `outowiki>=0.7.8`: OutoWiki integration

### Development Dependencies

- `pytest>=8.0`: Testing framework
- `pytest-asyncio>=0.23`: Async test support
- `mypy>=1.8`: Type checking

### Adding Dependencies

```bash
# Add runtime dependency
uv add new-package

# Add development dependency
uv add --dev new-package
```

## Resources

- [Python Documentation](https://docs.python.org/3/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [pytest Documentation](https://docs.pytest.org/)
- [uv Documentation](https://github.com/astral-sh/uv)
