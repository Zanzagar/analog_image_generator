---
name: code-review
description: Systematic code review for quality, security, and maintainability. Use when reviewing PRs, analyzing code quality, or providing feedback on implementations.
---

# Code Review Skill

## When to Use
- User asks to review code or a PR
- User asks "is this code good?" or similar
- After implementing a significant feature
- When user asks about code quality

## Review Checklist

### 1. Correctness
- Does the code do what it's supposed to do?
- Are edge cases handled?
- Are there off-by-one errors, null checks, or boundary conditions?

### 2. Security
- Input validation present?
- SQL injection, XSS, command injection risks?
- Secrets or credentials exposed?
- Proper authentication/authorization?

### 3. Performance
- Unnecessary loops or redundant operations?
- N+1 query problems?
- Large data structures in memory?
- Missing indexes for database queries?

### 4. Maintainability
- Is the code readable without extensive comments?
- Are functions focused (single responsibility)?
- Is there code duplication that should be extracted?
- Are names descriptive?

### 5. Error Handling
- Are errors caught and handled appropriately?
- Are error messages helpful for debugging?
- Is there proper logging?

### 6. Testing
- Are there tests for the new code?
- Do tests cover edge cases?
- Are tests readable and maintainable?

## Review Format

Provide feedback in this structure:
1. **Summary**: One-line assessment
2. **Critical Issues**: Must fix before merge (security, correctness)
3. **Suggestions**: Improvements to consider
4. **Praise**: What's done well (reinforces good patterns)

## Tone
Be constructive and specific. Instead of "this is bad", say "consider X because Y".
