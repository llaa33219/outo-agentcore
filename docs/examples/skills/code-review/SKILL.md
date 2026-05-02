---
name: code-review
description: Thorough code review with focus on security and performance. Use when reviewing pull requests, code changes, or conducting code audits.
version: "1.0"
license: MIT
---

# Code Review Guidelines

When reviewing code, follow this systematic approach to ensure quality, security, and maintainability.

## Security Checklist

- [ ] **SQL Injection**: Verify all database queries use parameterized statements
- [ ] **XSS Protection**: Check that user input is properly sanitized before rendering
- [ ] **Authentication**: Verify auth checks are in place for all protected endpoints
- [ ] **Authorization**: Ensure users can only access their own resources
- [ ] **Sensitive Data**: Check that secrets, tokens, and PII are not logged or exposed
- [ ] **Input Validation**: Verify all external input is validated before processing

## Performance Checklist

- [ ] **N+1 Queries**: Look for loops that make database calls
- [ ] **Unnecessary Allocations**: Check for objects created in tight loops
- [ ] **Caching Opportunities**: Identify repeated expensive computations
- [ ] **Algorithm Complexity**: Verify O(n) complexity for critical paths
- [ ] **Memory Leaks**: Check for unclosed resources or event listeners

## Code Quality Checklist

- [ ] **Readability**: Clear variable/function names, logical structure
- [ ] **DRY Principle**: No unnecessary code duplication
- [ ] **Error Handling**: Appropriate try/catch blocks, meaningful error messages
- [ ] **Testing**: Adequate test coverage for new functionality
- [ ] **Documentation**: Complex logic has explanatory comments

## Review Process

1. **Read the PR description** - Understand the context and goals
2. **Review the diff** - Focus on changes, not surrounding code
3. **Check security** - Apply security checklist first
4. **Assess performance** - Look for optimization opportunities
5. **Verify tests** - Ensure new code is tested
6. **Provide feedback** - Be constructive and specific

## Feedback Format

When providing feedback:

```
**Severity**: Critical / Major / Minor / Nit
**Location**: file.py:123
**Issue**: Description of the problem
**Suggestion**: How to fix it
```

Example:
```
**Severity**: Critical
**Location**: auth.py:45
**Issue**: SQL injection vulnerability - user input directly interpolated into query
**Suggestion**: Use parameterized query: cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```
