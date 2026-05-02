# Skills

This document describes the skills system in outo-agentcore, which follows the [Agent Skills specification](https://agentskills.io/specification).

## Overview

Skills are reusable instruction packages that extend agent capabilities. They are defined as directories containing a `SKILL.md` file with YAML frontmatter and Markdown instructions.

Skills follow a **progressive disclosure** model:
1. **Metadata** (name + description) - Always loaded at startup (~100 tokens per skill)
2. **Instructions** (SKILL.md body) - Loaded when skill is activated (<5000 tokens recommended)
3. **Resources** (scripts/, references/, assets/) - Loaded as needed

## Directory Structure

```
~/.outoac/skills/
├── code-review/
│   ├── SKILL.md          # Required: metadata + instructions
│   ├── scripts/          # Optional: executable code
│   ├── references/       # Optional: documentation
│   └── assets/           # Optional: templates, resources
└── security-audit/
    └── SKILL.md
```

## SKILL.md Format

Each skill has a `SKILL.md` file with YAML frontmatter followed by Markdown content:

```markdown
---
name: code-review
description: Code review guidelines for security, performance, and readability.
version: "1.0"
license: MIT
---

# Code Review Guidelines

When reviewing code, follow this checklist:

1. **Security**: Check for injection vulnerabilities, auth bypasses
2. **Performance**: Look for N+1 queries, unnecessary allocations
3. **Readability**: Clear naming, appropriate comments
4. **Testing**: Adequate test coverage
```

### Frontmatter Fields

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | Max 64 chars, lowercase letters, numbers, hyphens. Must match directory name. |
| `description` | Yes | Max 1024 chars. Describes what the skill does and when to use it. |
| `version` | No | Semantic version (e.g., "1.0.0") |
| `license` | No | SPDX license identifier |
| `compatibility` | No | Environment requirements |
| `allowed-tools` | No | Space-separated list of tools the skill may use |

### Body Content

The Markdown body contains the actual skill instructions. There are no format restrictions. Write whatever helps agents perform the task effectively.

Recommended sections:
- Step-by-step instructions
- Examples of inputs and outputs
- Common edge cases

## Creating Skills

### Step 1: Create Skill Directory

```bash
mkdir -p ~/.outoac/skills/my-skill
```

### Step 2: Create SKILL.md

```bash
cat > ~/.outoac/skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: Description of what this skill does and when to use it.
---

# Instructions

Your detailed instructions go here...
EOF
```

### Step 3: Test the Skill

The skill will be automatically discovered when you start a chat session:

```bash
outoac chat "Your message here"
```

## How Skills Work

### Discovery

At startup, outo-agentcore scans `~/.outoac/skills/` for directories containing `SKILL.md` files. Only the metadata (name + description) is loaded.

### Activation

Skills are activated **automatically** based on the task description. The agent reads the skill catalog in its system prompt and decides when a skill is relevant.

When a skill is activated, the agent reads the full `SKILL.md` file using the bash tool:

```bash
cat ~/.outoac/skills/code-review/SKILL.md
```

### System Prompt Injection

All discovered skills are listed in the agent's system prompt:

```
Available skills:
- code-review: Code review guidelines for security, performance, and readability.
- security-audit: Security audit checklist for vulnerability assessment.

To use a skill, read its SKILL.md file when the task matches its description.
Example: bash(command="cat ~/.outoac/skills/<skill-name>/SKILL.md")
```

## Examples

### Code Review Skill

```markdown
---
name: code-review
description: Thorough code review with focus on security and performance. Use when reviewing pull requests or code changes.
version: "1.0"
---

# Code Review Guidelines

## Security Checklist
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] Authentication bypasses
- [ ] Sensitive data exposure

## Performance Checklist
- [ ] N+1 query detection
- [ ] Unnecessary allocations
- [ ] Caching opportunities
- [ ] Algorithm complexity

## Review Process
1. Read the PR description and related issues
2. Review code changes systematically
3. Check for security vulnerabilities
4. Assess performance implications
5. Verify test coverage
6. Provide constructive feedback
```

### Git Workflow Skill

```markdown
---
name: git-workflow
description: Git workflow guidelines for branching, commits, and PRs. Use when working with version control.
---

# Git Workflow

## Branch Naming
- Feature: `feature/description`
- Bugfix: `bugfix/description`
- Hotfix: `hotfix/description`

## Commit Messages
Format: `type(scope): description`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

## Pull Request Process
1. Create branch from main
2. Make changes with atomic commits
3. Write PR description
4. Request review
5. Address feedback
6. Merge after approval
```

## Best Practices

### 1. Clear Descriptions

The description is the primary mechanism for skill activation. Be specific about when to use the skill:

```markdown
# Good
description: Code review guidelines for security and performance. Use when reviewing pull requests.

# Bad
description: Helps with code.
```

### 2. Focused Skills

Each skill should cover one concern. If your SKILL.md covers multiple topics, split into separate skills.

### 3. Concise Instructions

Target under 500 lines for SKILL.md. Move detailed documentation to `references/` directory.

### 4. Include Examples

Provide concrete examples of inputs and outputs to guide the agent.

### 5. Document Failure Modes

What breaks? What does the error look like? What's the fix?

## Troubleshooting

### Skills Not Discovered

Ensure:
- Skill directory is in `~/.outoac/skills/`
- `SKILL.md` file exists in the directory
- `name` and `description` fields are present in frontmatter

### Skill Not Activating

Check:
- Description clearly states when to use the skill
- Task description matches skill's description
- SKILL.md is readable and well-formed

### Token Limit Issues

If responses are truncated:
- Keep SKILL.md under 500 lines
- Move detailed docs to `references/`
- Use progressive loading (only load what's needed)

## Compatibility

outo-agentcore follows the [Agent Skills specification](https://agentskills.io/specification) and is compatible with:
- Claude Code
- GitHub Copilot
- Cursor
- Gemini CLI
- Other spec-compliant tools

Skills created for other tools can be used in outo-agentcore without modification.
