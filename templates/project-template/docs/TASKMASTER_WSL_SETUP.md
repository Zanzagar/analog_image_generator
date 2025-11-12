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
- Set main model to `gpt-5-codex` via `task-master models --set-main gpt-5-codex` (later).

## Tag Convention
- One PRD → one tag.

## Cadence
- parse-prd → analyze-complexity → expand → implement → set-status → (optional) generate.

