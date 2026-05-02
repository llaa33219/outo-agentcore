# Agent System

This document describes the agent system, including how to define agents, configure them, and use them effectively.

## Agent Overview

An agent is a specialized AI assistant defined by a markdown file. Each agent has:

- A **name** (from the config key)
- A **role** (from the markdown heading)
- **Instructions** (from the markdown body)
- Optional **model** and **provider** overrides (from frontmatter)

## Agent Markdown Format

Agent definitions use markdown with optional YAML frontmatter:

```markdown
---
model: gpt-4o
provider: default
temperature: 0.7
max_output_tokens: 4000
---

# Research Agent

You are a research specialist. Your job is to find information
and provide detailed analysis.

When researching:
1. Use multiple sources
2. Verify facts
3. Organize findings clearly
```

### Frontmatter Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `model` | string | Provider default | LLM model to use |
| `provider` | string | First provider | Provider name from config |
| `temperature` | float | `1.0` | Sampling temperature (0.0-2.0) |
| `max_output_tokens` | integer | Auto-detected | Maximum output tokens |

### Body Structure

- **First `#` heading**: Becomes the agent's role
- **Rest of body**: Becomes the agent's instructions

```markdown
# Role Name

Instructions go here...
```

## Creating Agents

### Step 1: Create Agent Directory

```bash
mkdir -p ~/.outoac/agents
```

### Step 2: Define Agent

```bash
cat > ~/.outoac/agents/researcher.md << 'EOF'
# Research Specialist

You are an expert researcher. Your responsibilities:
- Find accurate, up-to-date information
- Verify facts from multiple sources
- Organize findings in a clear structure
- Cite sources when possible

When researching a topic:
1. Start with broad searches
2. Narrow down to specific details
3. Cross-reference information
4. Summarize key findings
EOF
```

### Step 3: Register Agent

Add to your config:

```json
{
  "agents": {
    "researcher": "~/.outoac/agents/researcher.md"
  }
}
```

Or use setup:

```bash
outoac setup --agent-md ~/.outoac/agents/researcher.md
```

### Step 4: Use Agent

```bash
# Use specific agent
outoac chat "Research the latest AI developments" --agent researcher

# Or have main agent delegate to it
outoac chat "Research and summarize the latest AI developments"
```

## Agent Examples

### Coordinator Agent

```markdown
# Coordinator

You are a task coordinator. Your job is to:
1. Analyze incoming requests
2. Break them into subtasks
3. Delegate to appropriate specialist agents
4. Combine results into a coherent response

Available specialists:
- researcher: For finding information
- writer: For creating documents
- coder: For writing code
- reviewer: For quality checks

Always use the call_agent tool to delegate work.
```

### Researcher Agent

```markdown
---
temperature: 0.3
---

# Researcher

You are a research specialist focused on finding accurate information.

Your approach:
1. Start with broad searches to understand the landscape
2. Narrow down to specific details
3. Verify information from multiple sources
4. Organize findings logically

Always cite your sources when possible.
Use the bash tool to run search commands if needed.
```

### Writer Agent

```markdown
---
temperature: 0.7
---

# Technical Writer

You are a technical writer who creates clear, well-structured documents.

Guidelines:
- Use clear, concise language
- Organize content with headings and sections
- Include examples when helpful
- Ensure accuracy and completeness

Output format:
- Use markdown formatting
- Include a table of contents for long documents
- Use code blocks for code examples
```

### Coder Agent

```markdown
---
temperature: 0.2
max_output_tokens: 8000
---

# Software Developer

You are an experienced software developer.

Your responsibilities:
- Write clean, maintainable code
- Follow best practices and conventions
- Include appropriate error handling
- Write clear comments and documentation

When writing code:
1. Understand the requirements fully
2. Plan the implementation
3. Write the code
4. Test and verify
```

### Reviewer Agent

```markdown
# Code Reviewer

You are a thorough code reviewer.

Review checklist:
- [ ] Code follows conventions
- [ ] Error handling is appropriate
- [ ] Performance is acceptable
- [ ] Security considerations addressed
- [ ] Documentation is complete
- [ ] Tests are included

Provide constructive feedback with specific suggestions.
```

## Multi-Agent Workflows

### Sequential Workflow

```
User Request
     │
     ▼
┌─────────┐
│ Coordinator │
└────┬────┘
     │
     ├─→ Researcher → "Find information"
     │
     ├─→ Writer → "Create report"
     │
     └─→ Reviewer → "Quality check"
```

### Parallel Delegation

The coordinator can call multiple agents:

```markdown
# Coordinator

When receiving a complex task:
1. Identify independent subtasks
2. Call appropriate agents for each
3. Combine results

Example workflow:
- Call researcher to find information
- Call writer to create draft
- Call reviewer to check quality
```

### Recursive Delegation

Agents can call other agents, creating a hierarchy:

```
Main Agent
     │
     ├─→ Research Agent
     │        │
     │        └─→ Web Search Agent
     │
     └─→ Writer Agent
              │
              └─→ Editor Agent
```

## Agent Communication

### How Agents Communicate

Agents communicate through the `call_agent` tool:

```python
# Agent A calls Agent B
call_agent(agent_name="researcher", message="Find information about X")

# Agent B returns result
finish(message="Found the following: ...")
```

### Message Format

Messages are tracked with forward/return types:

```json
{
  "type": "forward",
  "sender": "main",
  "receiver": "researcher",
  "content": "Find information about X",
  "call_id": "abc123"
}
```

```json
{
  "type": "return",
  "sender": "researcher",
  "receiver": "main",
  "content": "Found the following: ...",
  "call_id": "abc123"
}
```

## Built-in Agent Tools

All agents have access to these tools:

### `bash`

Execute shell commands:

```bash
# Example usage by agent
bash(command="curl -s https://api.example.com/data")
bash(command="python script.py")
bash(command="ls -la")
```

### `call_agent`

Call another agent:

```python
call_agent(
    agent_name="researcher",
    message="Find information about quantum computing"
)
```

### `finish`

Return final result (REQUIRED):

```python
finish(message="Here are my findings: ...")
```

**Important**: Agents MUST use `finish` to return results. Plain text responses are NOT delivered to the caller.

### `wiki_record` (when enabled)

Record information to wiki:

```python
wiki_record(content="User prefers dark mode and concise responses")
```

### `wiki_search` (when enabled)

Search wiki knowledge base:

```python
wiki_search(query="user preferences")
```

## System Prompt Construction

The system prompt is built automatically:

```
You are "agent_name". [Role]

INSTRUCTIONS:
[Full instructions]

INVOKED BY: You have been called by 'caller'.
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

## Best Practices

### 1. Clear Role Definition

```markdown
# Good
# Research Specialist
You are an expert researcher focused on finding accurate information.

# Bad
# Helper
You help with stuff.
```

### 2. Specific Instructions

```markdown
# Good
When researching:
1. Start with broad searches
2. Narrow down to specific details
3. Verify facts from multiple sources
4. Organize findings clearly

# Bad
Do research and find information.
```

### 3. Appropriate Temperature

- **Low (0.1-0.3)**: For factual, deterministic tasks (coding, research)
- **Medium (0.4-0.7)**: For balanced tasks (writing, analysis)
- **High (0.8-1.0)**: For creative tasks (brainstorming, ideation)

### 4. Token Limits

Set `max_output_tokens` based on expected output:

- **Short responses**: 1000-2000
- **Medium responses**: 2000-4000
- **Long responses**: 4000-8000
- **Very long**: 8000+ (use with caution)

### 5. Agent Specialization

Create focused agents rather than generalists:

```markdown
# Good: Specialized
# Python Developer
You write Python code following PEP 8...

# Bad: Too general
# Developer
You write code in any language...
```

## Troubleshooting

### Agent not found

```
Error: Agent not found: researcher
```

**Solution**: Ensure the agent name in your config matches the key in `agents` dict.

### Agent not finishing

If an agent keeps responding without calling `finish`:

1. Check that instructions mention using `finish`
2. Ensure the system prompt is clear about requiring `finish`
3. Add explicit instructions: "You MUST call finish to return results"

### Wrong model being used

If an agent uses the wrong model:

1. Check frontmatter `model` field
2. Verify provider has the model available
3. Check `default_model` in provider config
