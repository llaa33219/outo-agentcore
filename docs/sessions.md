# Session Management

This document describes how sessions work in outo-agentcore, including persistence, continuation, and best practices.

## Session Overview

Sessions provide conversation continuity across multiple runs. Each session:

- Has a unique **session ID**
- Stores **message history**
- Tracks the **agent** used
- Persists to **JSON files**

## Session Storage

Sessions are stored in:

```
~/.outoac/sessions/
├── abc123def456.json
├── xyz789ghi012.json
└── ...
```

### Session File Format

```json
{
  "session_id": "abc123def456",
  "created_at": "2024-01-15T10:30:00Z",
  "agent_name": "main",
  "messages": [
    {
      "type": "forward",
      "sender": "user",
      "receiver": "main",
      "content": "What is quantum computing?",
      "call_id": "msg001"
    },
    {
      "type": "return",
      "sender": "main",
      "receiver": "user",
      "content": "Quantum computing is...",
      "call_id": "msg001"
    },
    {
      "type": "forward",
      "sender": "main",
      "receiver": "researcher",
      "content": "Find more details about quantum entanglement",
      "call_id": "msg002"
    },
    {
      "type": "return",
      "sender": "researcher",
      "receiver": "main",
      "content": "Quantum entanglement is...",
      "call_id": "msg002"
    }
  ]
}
```

## Using Sessions

### Start New Session

```bash
# New session with default agent
outoac chat "Hello, what can you help with?"

# New session with specific agent
outoac chat "Research AI trends" --agent researcher
```

Each call creates a new session and prints the session ID:

```
...response...

--- Session: abc123def456 ---
```

### Continue Existing Session

```bash
# Continue previous session
outoac chat "Tell me more about that" --session abc123def456

# Continue with different agent
outoac chat "Summarize what we discussed" --session abc123def456 --agent writer
```

### List Sessions

```bash
# List recent sessions
outoac sessions

# List more sessions
outoac sessions --limit 20
```

Output:

```
Session ID                           Agent           Created                    Messages
------------------------------------------------------------------------------------------
abc123def456                         main            2024-01-15T10:30:00Z      8
xyz789ghi012                         researcher      2024-01-15T09:15:00Z      12
```

## Session Continuation

### How It Works

When you continue a session:

1. Previous messages are loaded from the session file
2. Messages are added to the agent's context
3. New messages are appended to the session
4. Session file is updated

### Message Limit

For long sessions, you can limit the number of recent messages:

```bash
# Only include last 20 messages
outoac chat "Continue discussion" --session abc123 --max-messages 20
```

Or set in config:

```json
{
  "max_recent_messages": 50
}
```

This helps manage context window limits for very long conversations.

## Message Types

### Forward Messages

Messages from caller to callee:

```json
{
  "type": "forward",
  "sender": "user",
  "receiver": "main",
  "content": "What is AI?",
  "call_id": "abc123"
}
```

### Return Messages

Messages from callee to caller:

```json
{
  "type": "return",
  "sender": "main",
  "receiver": "user",
  "content": "AI is...",
  "call_id": "abc123"
}
```

### Agent-to-Agent Messages

When agents delegate work:

```json
{
  "type": "forward",
  "sender": "main",
  "receiver": "researcher",
  "content": "Find information about X",
  "call_id": "sub001"
}
```

```json
{
  "type": "return",
  "sender": "researcher",
  "receiver": "main",
  "content": "Found: ...",
  "call_id": "sub001"
}
```

## Session Manager API

The `SessionManager` class handles session operations:

```python
class SessionManager:
    def __init__(self, sessions_dir: Path)
    def create(self, agent_name: str = "main", session_id: str | None = None) -> SessionData
    def load(self, session_id: str) -> SessionData | None
    def save(self, session: SessionData) -> None
    def list_sessions(self) -> list[SessionData]
```

### SessionData

```python
@dataclass
class SessionData:
    session_id: str
    created_at: str
    messages: list[dict] = field(default_factory=list)
    agent_name: str = "main"
```

## Best Practices

### 1. Use Descriptive Agent Names

```bash
# Good: Specific agent
outoac chat "Research quantum computing" --agent researcher

# Bad: Generic agent for everything
outoac chat "Research quantum computing" --agent main
```

### 2. Manage Session Length

For long conversations:

```bash
# Limit messages to avoid context overflow
outoac chat "Continue" --session abc123 --max-messages 30
```

### 3. Use Sessions for Projects

```bash
# Start project session
outoac chat "Let's work on the API documentation" --agent writer

# Continue project work
outoac chat "Add authentication section" --session abc123
outoac chat "Now add error handling" --session abc123
```

### 4. Clean Up Old Sessions

Sessions accumulate over time. Periodically clean up:

```bash
# List sessions to identify old ones
outoac sessions --limit 50

# Manually delete old sessions
rm ~/.outoac/sessions/old_session_id.json
```

## Session History in Context

When continuing a session, previous messages are added to the agent's context:

```python
# In Runtime.execute()
if history:
    for msg in history:
        self._messages.append(Message(
            type=msg["type"],
            sender=msg["sender"],
            receiver=msg["receiver"],
            content=msg["content"],
            call_id=msg.get("call_id", uuid.uuid4().hex)
        ))
```

This allows agents to:

- Remember previous conversation
- Build on earlier responses
- Maintain context across runs

## Error Handling

### Session Not Found

```
Error: Session not found: abc123
```

**Solution**: Check session ID. Use `outoac sessions` to list available sessions.

### Corrupted Session

```
Error: Session file is corrupted: ~/.outoac/sessions/abc123.json
```

**Solution**: Delete the corrupted session file and start a new session.

### Invalid Session Format

```
Error: Session file has invalid format
```

**Solution**: Delete the invalid session file and start a new session.

## Examples

### Research Project

```bash
# Start research session
outoac chat "Research the impact of AI on healthcare" --agent researcher
# Output: --- Session: research001 ---

# Continue research
outoac chat "Focus on diagnostic applications" --session research001

# Get summary
outoac chat "Summarize our findings" --session research001 --agent writer
```

### Code Development

```bash
# Start coding session
outoac chat "Help me build a REST API" --agent coder
# Output: --- Session: code001 ---

# Add features
outoac chat "Add user authentication" --session code001
outoac chat "Now add database integration" --session code001

# Review
outoac chat "Review the code we wrote" --session code001 --agent reviewer
```

### Document Writing

```bash
# Start writing session
outoac chat "Write a technical blog post about microservices" --agent writer
# Output: --- Session: writing001 ---

# Iterate
outoac chat "Add a section about containerization" --session writing001
outoac chat "Include code examples" --session writing001

# Final review
outoac chat "Proofread and improve clarity" --session writing001
```
