<!-- template-version: 1.0.0 -->
<!-- template-file: docs/rules/git-workflow.md -->
# Git Workflow Rules & Commands Reference

## Daily Workflow Rules

### Rule 1: Always Start Fresh
```bash
git checkout main
git pull origin main
git checkout -b feature/descriptive-name
```
**When:** Beginning of every work session

### Rule 2: Commit Frequently
```bash
git add filename.py              # Specific files
git add .                        # All files
git commit -m "Descriptive message about what you did"
```

**When to Commit:**
- Feature/function completed and working
- Bug fixed and tested
- Before breaks (lunch, end of day)
- Before risky experiments
- Before switching tasks

**When NOT to Commit:**
- Code doesn't run/compile
- Broken functionality
- Incomplete features

### Rule 3: Push for Backup
```bash
git push -u origin feature/branch-name    # First time
git push origin feature/branch-name       # Subsequent pushes
```

## Branch Naming Conventions

```bash
feature/add-user-auth       # New features
bugfix/fix-login-error      # Bug fixes
hotfix/critical-security    # Urgent fixes
docs/update-readme          # Documentation
refactor/cleanup-database   # Code improvements
```

## Commit Message Rules

### Good Messages:
```bash
git commit -m "Add user authentication with JWT tokens"
git commit -m "Fix memory leak in image processing"
git commit -m "Update README with installation instructions"
git commit -m "Refactor database queries for better performance"
```

### Bad Messages:
```bash
git commit -m "fix"           # Too vague
git commit -m "updates"       # Meaningless
git commit -m "stuff"         # Useless
```

## Recovery Commands

### Uncommitted Changes
```bash
git status                    # See what changed
git checkout -- filename.py   # Restore single file
git reset --hard HEAD         # Restore all (NUCLEAR)
```

### Committed But Not Pushed
```bash
git reset --soft HEAD~1       # Undo commit, keep changes staged
git reset HEAD~1              # Undo commit, unstage changes
git reset --hard HEAD~1       # Undo commit, delete changes (NUCLEAR)
```

### Already Pushed (Safe)
```bash
git revert HEAD               # Create undo commit
git push origin main
```

### Emergency Recovery
```bash
git reflog                    # See all your actions
git checkout abc1234          # Go back to specific state
git stash                     # Temporarily save work
git stash pop                 # Restore saved work
```

## Team Collaboration Rules

1. **Never commit to main directly** - Always use feature branches
2. **Always pull before push** - `git pull origin main` first
3. **Use meaningful branch names** - Not `test`, `mywork`, `temp`
4. **Merge via Pull Requests** - For code review and history

## Quick Reference

| Command | When to Use | Effect |
|---------|-------------|--------|
| `git add .` | Before committing | Stages all changes |
| `git commit -m "msg"` | Save working code | Creates checkpoint |
| `git push origin branch` | Backup/share work | Uploads to GitHub |
| `git pull origin main` | Start of day | Gets latest changes |
| `git checkout -b feature/name` | New work | Creates new branch |
| `git status` | Check state | Shows what changed |
| `git log --oneline` | See history | Shows commits |
| `git revert HEAD` | Undo safely | Creates undo commit |

## Danger Commands (Use with Caution)

```bash
git reset --hard HEAD       # Deletes all uncommitted work
git reset --hard HEAD~5     # Deletes last 5 commits locally
git push --force            # Overwrites history (AVOID)
git branch -D branch-name   # Force delete branch
```
