# MCP Server Setup for Claude Code

Model Context Protocol (MCP) servers extend Claude Code's capabilities with specialized tools. This guide covers setting up commonly used MCPs globally so they're available across all projects.

## Global vs Project-Level Configuration

- **Global MCPs** (`~/.claude/mcp.json`): Available in all projects
- **Project MCPs** (`.mcp.json` in project root): Project-specific servers

## Recommended Global MCPs

### 1. Task Master AI

Task management and project planning directly in Claude Code.

```bash
# Install
npm install -g task-master-ai

# Add to ~/.claude/mcp.json
```

```json
{
  "mcpServers": {
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "--package=task-master-ai", "task-master-ai"],
      "env": {
        "ANTHROPIC_API_KEY": "your-api-key"
      }
    }
  }
}
```

**Key Commands:**
- `task-master list` - List all tasks
- `task-master next` - Get next task to work on
- `task-master init` - Initialize task tracking in a project

### 2. Context7

Access up-to-date documentation for libraries and frameworks.

```bash
# Add to ~/.claude/mcp.json
```

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

**Usage:** When working with libraries, Context7 provides current documentation so Claude has accurate, version-specific information.

### 3. GitHub MCP

Direct GitHub integration for issues, PRs, and repository management.

```bash
# Add to ~/.claude/mcp.json
```

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your-github-token"
      }
    }
  }
}
```

**Key Capabilities:**
- Create/manage issues and PRs
- Search repositories
- Read file contents from repos
- Manage branches

## Complete Example Configuration

Here's a full `~/.claude/mcp.json` with all three servers:

```json
{
  "mcpServers": {
    "task-master-ai": {
      "command": "npx",
      "args": ["-y", "--package=task-master-ai", "task-master-ai"],
      "env": {
        "ANTHROPIC_API_KEY": "${ANTHROPIC_API_KEY}"
      }
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

## Setup Steps

1. **Create the config file:**
   ```bash
   mkdir -p ~/.claude
   touch ~/.claude/mcp.json
   ```

2. **Add your configuration** (copy from examples above)

3. **Set environment variables** (add to `~/.bashrc` or `~/.zshrc`):
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   export GITHUB_TOKEN="ghp_..."
   ```

4. **Restart Claude Code** to load the new MCPs

## Verifying MCP Setup

After configuration, Claude Code will have access to tools from each MCP server. You can verify by asking Claude to:
- "List my tasks" (Task Master)
- "Look up the latest React documentation" (Context7)
- "Show my open GitHub issues" (GitHub)

## Troubleshooting

### MCP server not starting
- Check `npx` is installed: `npm install -g npx`
- Verify environment variables are set
- Check Claude Code logs for errors

### Authentication errors
- Regenerate API keys/tokens
- Ensure tokens have required permissions
- Check token hasn't expired

## Security Notes

- Never commit `~/.claude/mcp.json` to version control
- Use environment variables for sensitive values
- Regularly rotate API keys and tokens
- Review MCP server permissions before installing
