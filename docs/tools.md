# Tools Reference

This document describes all built-in tools available to agents.

## Tool Overview

Tools are functions that agents can call to perform actions. Each tool has:

- **name**: Unique identifier
- **description**: What the tool does
- **parameters**: Input schema
- **execute**: Async function that runs the tool

## Built-in Tools

### `bash`

Execute shell commands and return output.

**Description**: Execute a bash command and return its output.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `command` | string | Yes | The bash command to execute |

**Example Usage**:

```python
# Simple command
bash(command="echo Hello, World!")

# List files
bash(command="ls -la")

# Run Python script
bash(command="python script.py")

# curl request
bash(command="curl -s https://api.example.com/data")

# Pipe commands
bash(command="cat file.txt | grep pattern | wc -l")
```

**Response**: Returns stdout and stderr combined.

**Implementation**:

```python
class BashTool:
    name = "bash"
    description = "Execute a bash command and return its output."

    async def execute(self, command: str) -> ToolResult:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        output = stdout.decode() + stderr.decode()
        return ToolResult(content=output)
```

**Use Cases**:
- Running scripts
- File operations
- System commands
- API calls via curl
- Data processing

**Security Notes**:
- Commands run with the same permissions as the outo-agentcore process
- Be cautious with commands that modify system state
- Avoid running untrusted commands

---

### `call_agent`

Call another agent to delegate work.

**Description**: Call another agent. The agent will process your message and return a result.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_name` | string | Yes | Name of the agent to call |
| `message` | string | Yes | Message to send to the agent |

**Example Usage**:

```python
# Call researcher agent
call_agent(
    agent_name="researcher",
    message="Find information about quantum computing"
)

# Call writer agent
call_agent(
    agent_name="writer",
    message="Write a summary of these findings: ..."
)

# Call with specific instructions
call_agent(
    agent_name="coder",
    message="Write a Python function that sorts a list using quicksort"
)
```

**Response**: Returns the called agent's final result.

**Behavior**:
1. Creates a new agent execution context
2. Sends the message to the target agent
3. Target agent executes its workflow
4. Returns the agent's final result (via `finish` tool)

**Nesting**: Agents can call other agents recursively:

```
Main → Researcher → Web Search Agent
                  → Data Analysis Agent
     → Writer → Editor Agent
```

**Error Cases**:
- Agent not found: Raises `RoutingError`
- Agent doesn't finish: Loop continues until `finish` is called

---

### `finish`

Return final result to the caller.

**Description**: Return your final result to the caller. This is the ONLY way to deliver your response.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | string | Yes | Result message to return |

**Example Usage**:

```python
# Simple result
finish(message="The capital of France is Paris.")

# Detailed result
finish(message="""
## Research Findings

1. Finding one...
2. Finding two...
3. Finding three...

## Summary
Overall conclusion...
""")

# With data
finish(message="Found 42 results. Top 5: ...")
```

**Behavior**:
- Returns the message to the caller
- Ends the agent's execution loop
- Result is delivered to parent agent or user

**IMPORTANT**: 
- Agents MUST call `finish` to return results
- Plain text responses are NOT delivered to the caller
- If an agent responds with text instead of calling `finish`, it receives a nudge message:

```
[SYSTEM] Your plain text response was NOT delivered to the caller. 
You MUST use the finish tool to return results. 
Call finish(message="your result") now.
```

---

### `wiki_record`

Record information to the wiki knowledge base.

**Description**: Record information to the wiki knowledge base for future reference.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `content` | string | Yes | The content to record to the wiki |

**Example Usage**:

```python
# Record user preference
wiki_record(content="User prefers dark mode and concise responses")

# Record research finding
wiki_record(content="Quantum computing uses qubits that can be 0 and 1 simultaneously")

# Record project info
wiki_record(content="Project uses Python 3.11, FastAPI, and PostgreSQL")
```

**Response**: Returns confirmation of recording.

**Availability**: Only available when wiki is enabled in config:

```json
{
  "wiki": {
    "enabled": true,
    ...
  }
}
```

**Use Cases**:
- Remembering user preferences
- Building knowledge base from conversations
- Recording research findings
- Storing project context

---

### `wiki_search`

Search the wiki knowledge base.

**Description**: Search the wiki knowledge base for relevant information.

**Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | string | Yes | The search query to find relevant wiki content |

**Example Usage**:

```python
# Search for preferences
wiki_search(query="user preferences")

# Search for topic
wiki_search(query="quantum computing")

# Search for project info
wiki_search(query="project setup")
```

**Response**: Returns matching wiki entries or "No results found."

**Availability**: Only available when wiki is enabled in config.

**Use Cases**:
- Recalling previous conversations
- Finding recorded information
- Checking user preferences
- Retrieving project context

## Tool Schema Format

Tools are defined using JSON Schema:

```json
{
  "name": "tool_name",
  "description": "Tool description",
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
```

## Custom Tools

Currently, only built-in tools are supported. Future versions may support custom tool definitions.

## Tool Execution Flow

```
Agent decides to call tool
         │
         ▼
┌─────────────────┐
│ Parse arguments  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Execute tool     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Return result    │
│ to agent context │
└─────────────────┘
```

## Best Practices

### 1. Use Appropriate Tools

```python
# Good: Use bash for system commands
bash(command="ls -la")

# Bad: Don't try to simulate bash with other tools
```

### 2. Handle Tool Errors

Tools may return errors. Handle them gracefully:

```python
result = bash(command="cat nonexistent.txt")
# Result: "cat: nonexistent.txt: No such file or directory"
```

### 3. Always Finish

```python
# Good: Always call finish
finish(message="Here are the results: ...")

# Bad: Responding with text only
"Here are the results: ..."  # NOT delivered!
```

### 4. Delegate Effectively

```python
# Good: Clear delegation
call_agent(
    agent_name="researcher",
    message="Find the latest statistics on AI adoption in healthcare"
)

# Bad: Vague delegation
call_agent(
    agent_name="researcher",
    message="Do research"
)
```

### 5. Use Wiki for Persistence

```python
# Record important information
wiki_record(content="User's company uses AWS for all cloud infrastructure")

# Later, recall it
wiki_search(query="cloud infrastructure")
```

## Troubleshooting

### Tool not found

```
Error: Tool not found: custom_tool
```

**Solution**: Only built-in tools are available. Check tool name spelling.

### Command failed

```python
result = bash(command="invalid_command")
# Returns: "bash: invalid_command: command not found"
```

**Solution**: Check command syntax and availability.

### Wiki not available

```
wiki_record is not available
```

**Solution**: Enable wiki in config:

```json
{
  "wiki": {
    "enabled": true
  }
}
```
