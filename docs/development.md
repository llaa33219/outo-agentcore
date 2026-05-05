# Development Guide

This guide covers setting up the development environment and contributing to outo-agentcore.

## Development Setup

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Git

### Clone Repository

```bash
git clone https://github.com/llaa33219/outo-agentcore.git
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
│       │   ├── main.py          # CLI argument parsing
│       │   ├── cmd_chat.py      # Chat command (uses agentouto.run)
│       │   ├── cmd_setup.py     # Setup command
│       │   └── cmd_sessions.py  # Sessions command
│       ├── config/
│       │   ├── __init__.py
│       │   ├── loader.py        # JSON config load/save
│       │   └── schema.py        # Config dataclasses
│       ├── parser/
│       │   ├── __init__.py
│       │   ├── agent_md.py      # Agent markdown parser
│       │   └── skill_md.py      # Skill markdown parser
│       ├── sessions/
│       │   ├── __init__.py
│       │   └── manager.py       # Session persistence
│       └── tools/
│           └── __init__.py      # Custom tools (bash, wiki)
├── tests/
│   ├── test_config.py
│   ├── test_agent_md.py
│   ├── test_sessions.py
│   └── test_integration.py
├── docs/
├── pyproject.toml
├── README.md
└── uv.lock
```

The core agent execution engine is provided by the [agentouto](https://github.com/llaa33219/agentouto) SDK (listed as a dependency).

## Running Tests

### Run All Tests

```bash
uv run pytest tests/ -v
```

### Run with Coverage

```bash
uv run pytest tests/ --cov=outo_agentcore --cov-report=html
```

## Code Architecture

### CLI Layer

The CLI is the entry point. `cmd_chat.py` is the most complex command:

1. Load config from `~/.outoac/config.json`
2. Parse agent markdown files into `agentouto.Agent` objects
3. Build `agentouto.Provider` objects from config
4. Create tools using `agentouto.Tool` decorator
5. Discover skills and build `extra_instructions` string
6. Load session history (if continuing)
7. Call `agentouto.run()` with all parameters
8. Save resulting messages to session

### Adding a New Tool

Tools use agentouto's `@Tool` decorator:

```python
import agentouto

@agentouto.Tool
def my_tool(param: str) -> str:
    """Description shown to the LLM."""
    return f"Result: {param}"
```

Register in `cmd_chat.py`:

```python
tools = [bash, my_tool]
```

For tools that need config access (like wiki tools), use a factory:

```python
def make_my_tool(settings):
    @agentouto.Tool
    def my_tool(param: str) -> str:
        """Description."""
        # Use settings here
        return "result"
    return my_tool
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
mycommand_parser = subparsers.add_parser("mycommand", help="My command help")
mycommand_parser.add_argument("--option", help="Option help")

elif args.command == "mycommand":
    from outo_agentcore.cli.cmd_mycommand import cmd_mycommand
    cmd_mycommand(args)
```

## Testing

### Test Structure

- `test_config.py`: Config load/save tests
- `test_agent_md.py`: Agent markdown parser tests
- `test_sessions.py`: Session persistence tests
- `test_integration.py`: CLI + agentouto integration tests (mocked)

### Writing Integration Tests

Mock `agentouto.run` to test CLI behavior without real LLM calls:

```python
from unittest.mock import patch
import agentouto

@patch("agentouto.run")
def test_chat_basic(mock_run):
    mock_run.return_value = agentouto.RunResult(
        output="Hello",
        messages=[...],
    )
    # Call cmd_chat and assert behavior
```

### Mocking Guidelines

- Mock `agentouto.run` for integration tests
- Mock file system using `tmp_path` fixture
- Use `patch.dict("os.environ", {"HOME": ...})` for config paths

## Code Style

### Formatting

- Follow PEP 8
- Use type hints
- Use dataclasses for data structures

### Naming Conventions

- **Classes**: PascalCase
- **Functions**: snake_case
- **Variables**: snake_case
- **Constants**: UPPER_CASE

## Debugging

### Enable Debug Output

```bash
outoac chat "message" --debug
```

This passes `debug=True` to `agentouto.run()`, enabling event logs and traces.

### Common Issues

**Import Errors**:
```bash
uv sync
```

**Test Failures**:
```bash
uv run pytest tests/test_integration.py -v -s
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

## Release Process

### Version Bumping

Update version in `pyproject.toml`:

```toml
[project]
version = "0.3.0"
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

- `agentouto>=0.27.0`: Multi-agent SDK (peer-to-peer agent communication)
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

- [agentouto SDK](https://github.com/llaa33219/agentouto)
- [Python Documentation](https://docs.python.org/3/)
- [pytest Documentation](https://docs.pytest.org/)
- [uv Documentation](https://github.com/astral-sh/uv)
