# Task Master MCP on WSL (Cursor)

## MCP Config (project-local `.cursor/mcp.json`)
```json
{
  "mcpServers": {
    "task-master-ai": {
      "command": "wsl.exe",
      "args": [
        "bash",
        "-c",
        "export PATH='/home/USER/.nvm/versions/node/vXX/bin:/usr/bin:/bin:$PATH' && export TASK_MASTER_TOOLS='standard' && task-master-ai"
      ]
    }
  }
}
```
- Use `standard` tool mode for day-to-day; `all` only when needed.
- Embed PATH because non-interactive WSL shells don’t load nvm.

## Codex CLI
- Ensure `codex --version` works and `~/.codex/auth.json` exists.
- Set main model to `gpt-5.1-codex-max` via `task-master models --set-main gpt-5.1-codex-max` (later).

## Tag Convention
- One PRD → one tag.

## Cadence
- parse-prd → analyze-complexity → expand → implement → set-status → (optional) generate.

## Context7 MCP (Optional)
Add Context7 to `.cursor/mcp.json` so Cursor can pull fresh docs:

### Remote
```json
{
  "mcpServers": {
    "context7": {
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "YOUR_CONTEXT7_API_KEY"
      }
    }
  }
}
```

### Local `npx`
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp", "--api-key", "YOUR_CONTEXT7_API_KEY"]
    }
  }
}
```

> Tip: add a Cursor rule instructing the assistant to “use context7” automatically for library/setup questions.
