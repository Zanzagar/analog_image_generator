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
        "export PATH='/home/cjh5690/.nvm/versions/node/v22.16.0/bin:/usr/bin:/bin:$PATH' && \
         export TASK_MASTER_TOOLS='standard' && \
         export ANTHROPIC_API_KEY=\"$ANTHROPIC_API_KEY\" && \
         export PERPLEXITY_API_KEY=\"$PERPLEXITY_API_KEY\" && \
         task-master-ai"
      ]
    }
  }
}
```
- Use `standard` tool mode for day-to-day; `all` only when needed.
- Embed PATH because non-interactive WSL shells don’t load nvm, and forward the Perplexity/Anthropic keys explicitly (WSL ignores `env` blocks).
- Run `task-master init --rules codex,cursor --yes` before enabling the MCP (set `FORCE_PYENV=1` if you need pyenv/nvm in that non-interactive shell) to avoid `[WARN] No configuration file found`.

## Codex CLI
- Ensure `codex --version` works and `~/.codex/auth.json` exists.
- Set main model to `gpt-5-codex` via `task-master models --set-main gpt-5-codex`.
- After each change, run `task-master models` and paste the table output into your meeting notes for traceability.

## Tag Convention
- One PRD → one tag (`fluvial-v1`, `aeolian-v1`, `estuarine-v1`).

## Cadence
- parse-prd → analyze-complexity → expand → implement → set-status → (optional) generate.
- Run `task-master status` before destructive commands to confirm the active tag/context.
