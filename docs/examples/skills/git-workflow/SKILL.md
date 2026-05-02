---
name: git-workflow
description: Git workflow guidelines for branching, commits, and pull requests. Use when working with version control, creating branches, or writing commit messages.
version: "1.0"
license: MIT
---

# Git Workflow Guidelines

Follow these guidelines for consistent and effective version control practices.

## Branch Naming

Use the format: `type/short-description`

| Type | Use Case | Example |
|------|----------|---------|
| `feature` | New functionality | `feature/user-authentication` |
| `bugfix` | Bug fixes | `bugfix/login-redirect` |
| `hotfix` | Urgent production fixes | `hotfix/security-patch` |
| `docs` | Documentation updates | `docs/api-reference` |
| `refactor` | Code restructuring | `refactor/simplify-logic` |

## Commit Messages

Format: `type(scope): description`

### Types

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Formatting, missing semicolons (no code change) |
| `refactor` | Code restructuring (no feature/fix) |
| `test` | Adding or updating tests |
| `chore` | Maintenance tasks, dependency updates |

### Examples

```
feat(auth): add JWT token refresh mechanism
fix(api): handle null response in user endpoint
docs(readme): update installation instructions
refactor(utils): extract validation logic to separate module
test(auth): add integration tests for login flow
chore(deps): update dependencies to latest versions
```

### Rules

- Use imperative mood ("add" not "added")
- Keep subject line under 72 characters
- Add body for complex changes
- Reference issues: "Fixes #123"

## Pull Request Process

### 1. Create Branch

```bash
git checkout main
git pull origin main
git checkout -b feature/my-feature
```

### 2. Make Changes

- Make atomic commits (one logical change per commit)
- Write clear commit messages
- Keep commits focused and small

### 3. Write PR Description

```markdown
## Summary
Brief description of changes

## Changes
- List of specific changes
- Another change

## Testing
How to verify the changes work

## Related Issues
Fixes #123
```

### 4. Request Review

- Assign reviewers
- Address feedback promptly
- Re-request review after changes

### 5. Merge

- Squash commits if PR has many small commits
- Use merge commit for complex features
- Delete branch after merge

## Common Scenarios

### Feature Development

```bash
git checkout -b feature/new-feature
# Make changes
git add .
git commit -m "feat(module): add new feature"
git push -u origin feature/new-feature
# Create PR
```

### Bug Fix

```bash
git checkout -b bugfix/fix-description
# Fix the bug
git add .
git commit -m "fix(module): fix the bug description"
git push -u origin bugfix/fix-description
# Create PR
```

### Sync with Main

```bash
git fetch origin
git rebase origin/main
# Resolve conflicts if any
git push --force-with-lease
```
