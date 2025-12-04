<!-- template-version: 1.0.0 -->
<!-- template-file: docs/rules/self-improve.md -->
# Rule Self-Improvement Guidelines

Guidelines for continuously improving AI assistant rules based on emerging code patterns and best practices.

## Rule Improvement Triggers

Consider updating rules when you observe:
- New code patterns not covered by existing rules
- Repeated similar implementations across files
- Common error patterns that could be prevented
- New libraries or tools being used consistently
- Emerging best practices in the codebase

## Analysis Process

When reviewing code changes:
- Compare new code with existing rules
- Identify patterns that should be standardized
- Look for references to external documentation
- Check for consistent error handling patterns
- Monitor test patterns and coverage

## When to Add New Rules

Add a new rule when:
- A new technology/pattern is used in 3+ files
- Common bugs could be prevented by a rule
- Code reviews repeatedly mention the same feedback
- New security or performance patterns emerge

## When to Modify Existing Rules

Update an existing rule when:
- Better examples exist in the codebase
- Additional edge cases are discovered
- Related rules have been updated
- Implementation details have changed

## Rule Quality Checks

Good rules should be:
- Actionable and specific
- Based on actual code examples
- Kept up to date with current practices
- Consistently enforced across the codebase

## Continuous Improvement

Ongoing maintenance:
- Monitor code review comments for patterns
- Track common development questions
- Update rules after major refactors
- Add links to relevant documentation
- Cross-reference related rules

## Rule Deprecation

When patterns become obsolete:
- Mark outdated patterns as deprecated
- Remove rules that no longer apply
- Update references to deprecated rules
- Document migration paths for old patterns

## Documentation Sync

Keep documentation current:
- Synchronize examples with actual code
- Update references to external docs
- Maintain links between related rules
- Document breaking changes
