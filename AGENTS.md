# Codex CLI + Task Master AI Integration — Complete Setup and Workflow Guide

**Scope**: From zero to fully operational Codex-powered Task Master on WSL, with interactive development, batch task management, and comprehensive reporting capabilities.

---

## Definition of Done (per Agent)
- GEO: Rules mapped in GEOLOGIC_RULES.md and notebook anchors; visual realism checks passed.
- GEN: Generators return (gray, masks_dict); masks align with palettes; parameters documented.
- UX: Sliders/preview responsive; metrics update; batch export button works.
- STAT: compute_metrics covers Phase 1 & 2; CSV schema stable; unit tests where feasible.
- REP: CSV + per-env PDFs + master PDF generated; legends consistent with PALETTES.md.
- QA: Smoke passes; checklist at top of notebooks fully ticked; no regressions vs previous tag.
- DOC: README/WORKFLOW updated; GEOLOGIC_RULES + anchors in sync; meeting recap saved.

## Daily Loop (Cursor-first)
1. Edit PRDs/AGENTS; update GEOLOGIC_RULES anchors.
2. Pre-commit run; small PR.
3. If ready to implement: switch to Codex+Task Master, work next task.

## Release Loop
1. Smoke + CI green; CHANGELOG entry added.
2. PR with artifacts (CSV/PDF/figures) and PRD references.
3. Review + merge; tag release if applicable.

## Notebook Anchors Discipline
- Every principle implemented in code is referenced in a notebook markdown cell and in GEOLOGIC_RULES.md.
- Update both when refactoring names or logic.
- Anchor IDs must follow `anchor-<env>-<principle>` (lowercase kebab case) and live under `notebooks/<env>.ipynb`.
- Code anchors use fully qualified names from `analog_image_generator`, e.g., ``analog_image_generator.geologic_generators.meander_centerline(...)`` as documented in `docs/GEOLOGIC_RULES.md`.
- During reviews, verify that each changed function appears in both the code anchor column and the notebook anchor column before requesting approval.

## Code Organization (Package-first)
- Core code lives in the Python package `analog_image_generator` (src layout).
- Jupyter notebooks are for demo/lecture usage and import the package; avoid placing core logic in notebooks.
- The package skeleton and build wiring (Hatchling) are created immediately after switching to Codex + Task Master.

---

## 0) Why This Document Exists

Task Master can use multiple AI providers. This document is the single source of truth for integrating **Codex CLI (GPT-5 via ChatGPT subscription)** as the primary AI model on **WSL (Windows Subsystem for Linux)**, ensuring zero API costs for main operations while maintaining full Task Master functionality. It covers authentication, configuration, troubleshooting, and workflow best practices.

---

## 1) Roles (Development Agents)

### System Administrator (SYS)
- Owns WSL configuration, environment setup, and MCP server management
- Validates Codex CLI authentication and Task Master connectivity
- Troubleshoots transport errors and connection issues

### Configuration Engineer (CONFIG)
- Manages `.taskmaster/config.json` and MCP configurations
- Sets up model providers (main, research, fallback)
- Maintains API key security and environment variables

### Workflow Engineer (FLOW)
- Designs and implements development workflows with Task Master
- Creates PRDs (Product Requirements Documents)
- Manages task hierarchies, dependencies, and status tracking

### AI Integration Engineer (AI)
- Optimizes Codex CLI usage patterns
- Configures tool loading modes (core/standard/all)
- Monitors token usage and model performance

### Documentation Engineer (DOC)
- Maintains this document and related guides
- Creates templates for PRDs and task structures
- Documents common patterns and solutions

### QA Engineer (QA)
- Validates Task Master operations
- Tests MCP server connectivity
- Verifies geologic workflow integration

---

## 2) Project Structure

```
analog_image_generator/
├── .taskmaster/
│   ├── config.json                    # AI model configuration
│   ├── state.json                     # Current tag context
│   ├── docs/
│   │   ├── prd.txt                    # Product Requirements Document
│   │   └── research/                  # Research outputs
│   ├── reports/
│   │   └── task-complexity-report.json
│   ├── tasks/
│   │   ├── tasks.json                 # Main task database
│   │   └── *.md                       # Individual task files
│   └── templates/
│       ├── example_prd.txt
│       └── example_prd_rpg.txt
├── .cursor/
│   └── mcp.json                       # Project-local MCP config (WSL-compatible)
├── .codex/
│   ├── auth.json                      # Codex OAuth tokens (auto-managed)
│   └── config.toml                    # Codex CLI preferences
├── src/                               # Your project source code
├── notebooks/                         # Jupyter notebooks
├── AGENTS.md                          # This file
├── docs/                              # Rules, palettes, templates
└── README.md
```

---

## Domain Tags Plan (for later)

When ready to organize tasks by domain, use these tag names (no commands run here):
- `fluvial-v1`: fluvial generators, UX, stats, reporting
- `aeolian-v1`: aeolian dune fields
- `estuarine-v1`: estuarine systems

Each PRD maps to its tag. Parse PRDs and expand tasks only when you are actively working in Codex.

---

## 3) Dependencies & Installation

### Prerequisites
```bash
# Node.js (via nvm - already installed)
node --version  # Should show v22.16.0 or similar

# Codex CLI (already installed)
codex --version  # Should show codex-cli 0.46.0 or similar

# Task Master AI
npm install -g task-master-ai
```

### WSL-Specific Requirements
```bash
# Ensure wsl.exe can access your node/npx
export PATH="/home/cjh5690/.nvm/versions/node/v22.16.0/bin:/usr/bin:/bin:$PATH"

# Test Codex CLI authentication
codex "Hello, test connection"
```

---

## 4) Absolute, Non-Negotiable Acceptance Criteria

1. **Codex Authentication**: Must have valid OAuth tokens in `~/.codex/auth.json` (via ChatGPT subscription)
2. **WSL Compatibility**: MCP server must use `wsl.exe` wrapper for all operations
3. **Task Master Initialization**: Project must have `.taskmaster/config.json` and proper directory structure
4. **Model Configuration**: Codex must be set as main model; research and fallback must be configured
5. **MCP Connectivity**: Cursor must successfully connect to Task Master MCP server without JSON-RPC errors
6. **Feature Parity**: All Task Master features (interactive, analysis, reporting) must work with Codex
7. **Traceability**: Configuration files must be version-controlled and documented

---

## 5) Milestones

### M1 — Codex CLI Authentication (SYS + CONFIG)
**Goal**: Verify Codex CLI is installed and authenticated with ChatGPT subscription

**Tasks**:
- Verify `codex --version` returns valid version
- Check `~/.codex/auth.json` exists and contains tokens
- Test basic Codex query: `codex "What is 2+2?"`

**Acceptance**: Codex CLI responds without authentication errors

---

### M2 — WSL MCP Configuration (SYS + CONFIG)
**Goal**: Configure Task Master MCP server to work on WSL

**Tasks**:
- Create/update global `~/.cursor/mcp.json` with WSL wrapper
- Create/update project-local `.cursor/mcp.json` with WSL wrapper
- Export PATH and API keys in bash command string
- Test MCP server startup without JSON-RPC errors

**Example Configuration**:
```json
{
  "mcpServers": {
    "task-master-ai": {
      "command": "wsl.exe",
      "args": [
        "bash",
        "-c",
        "export PATH='/home/cjh5690/.nvm/versions/node/v22.16.0/bin:/usr/bin:/bin:$PATH' && export TASK_MASTER_TOOLS='all' && export ANTHROPIC_API_KEY='YOUR_KEY' && export PERPLEXITY_API_KEY='YOUR_KEY' && task-master-ai"
      ]
    }
  }
}
```

**Acceptance**: MCP server starts with `[INFO]` messages, no "Configuration file not found" warnings

---

### M3 — Task Master Project Initialization (FLOW)
**Goal**: Initialize Task Master in analog_image_generator project

**Tasks**:
```bash
cd /home/cjh5690/projects/analog_image_generator
task-master init --rules codex,cursor --yes
```

**Acceptance**:
- `.taskmaster/` directory structure created
- `config.json` exists with default models
- Shell aliases added to `.bashrc`
- Git repository initialized (if requested)

---

### M4 — Codex Model Configuration (CONFIG + AI)
**Goal**: Set Codex as primary AI provider

**Tasks**:
```bash
# View available models
task-master models

# Set Codex as main model
task-master models --set-main gpt-5-codex

# Optionally set fallback
task-master models --set-fallback claude-sonnet-4-20250514

# Verify configuration
task-master models
```

**Expected Output**:
```
Active Model Configuration:
┌──────────┬──────────────┬──────────────────┬────────────┬──────────────┐
│ Role     │ Provider     │ Model ID         │ SWE Score  │ Cost         │
├──────────┼──────────────┼──────────────────┼────────────┼──────────────┤
│ Main     │ codex-cli    │ gpt-5-codex      │ 74.9% ★★★  │ Free         │
│ Research │ perplexity   │ sonar-pro        │ N/A        │ $3 in/$15 out│
│ Fallback │ anthropic    │ claude-3-7-...   │ 62.3% ★★☆  │ $3 in/$15 out│
└──────────┴──────────────┴──────────────────┴────────────┴──────────────┘
```

**Acceptance**: Codex-cli shows as main provider with "Free" cost

---

### M5 — PRD Creation & Task Generation (FLOW + AI)
**Goal**: Create Product Requirements Document and generate initial tasks

**Tasks**:
1. Create PRD at `.taskmaster/docs/prd.txt` (use template from `.taskmaster/templates/example_prd.txt`)
2. Parse PRD to generate tasks:
   ```bash
   task-master parse-prd .taskmaster/docs/prd.txt --num-tasks 10 --research
   ```
3. Analyze task complexity:
   ```bash
   task-master analyze-complexity --research
   ```
4. View complexity report:
   ```bash
   task-master complexity-report
   ```

**Acceptance**:
- `tasks.json` created with generated tasks
- Complexity report shows analysis per task
- Tasks align with PRD requirements

---

### M6 — Task Expansion & Workflow (FLOW)
**Goal**: Break down complex tasks into subtasks

**Tasks**:
```bash
# View all tasks
task-master list

# Get next available task
task-master next

# Expand a specific task
task-master expand --id=1 --research --force

# View expanded task
task-master show 1
```

**Acceptance**: Tasks have logical subtask breakdowns ready for implementation

---

### M7 — Cursor Integration & Testing (SYS + FLOW + QA)
**Goal**: Verify end-to-end Cursor + MCP + Task Master workflow

**Tasks**:
1. Restart Cursor completely
2. Enable Task Master MCP in Cursor Settings (Ctrl+Shift+J → MCP tab)
3. Test in AI chat:
   ```
   Can you show me all my tasks?
   What's the next task I should work on?
   Can you help me expand task 2?
   ```

**Acceptance**:
- Cursor connects to MCP without errors
- AI can query and manipulate tasks
- Interactive workflow feels natural

---

## 6) Detailed Configuration Files

### 6.1 Global MCP Config (`~/.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "canva-dev": {
      "command": "wsl.exe",
      "args": [
        "bash",
        "-c",
        "cd /home/cjh5690/CursorProjects/byc-flyer && export PATH='/home/cjh5690/.nvm/versions/node/v22.16.0/bin:/usr/bin:/bin:$PATH' && npx -y @canva/cli@latest mcp"
      ]
    },
    "task-master-ai": {
      "command": "wsl.exe",
      "args": [
        "bash",
        "-c",
        "export PATH='/home/cjh5690/.nvm/versions/node/v22.16.0/bin:/usr/bin:/bin:$PATH' && export TASK_MASTER_TOOLS='all' && export ANTHROPIC_API_KEY='YOUR_KEY' && export PERPLEXITY_API_KEY='YOUR_KEY' && export OPENAI_API_KEY='YOUR_KEY' && task-master-ai"
      ]
    }
  }
}
```

**Key Points**:
- `wsl.exe` forces WSL execution
- `export PATH` includes nvm node binaries
- API keys embedded in command (env section doesn't work with wsl.exe)
- No `cd` to project directory needed (Task Master auto-detects)

---

### 6.2 Project-Local MCP Config (`.cursor/mcp.json`)

```json
{
	"mcpServers": {
		"task-master-ai": {
			"command": "wsl.exe",
			"args": [
				"bash",
				"-c",
				"export PATH='/home/cjh5690/.nvm/versions/node/v22.16.0/bin:/usr/bin:/bin:$PATH' && export TASK_MASTER_TOOLS='all' && export ANTHROPIC_API_KEY='YOUR_KEY' && export PERPLEXITY_API_KEY='YOUR_KEY' && task-master-ai"
			]
		}
	}
}
```

**Precedence**: Project-local config overrides global config

---

### 6.3 Task Master Config (`.taskmaster/config.json`)

```json
{
  "models": {
    "main": {
      "provider": "codex-cli",
      "modelId": "gpt-5-codex",
      "maxTokens": 120000,
      "temperature": 0.2
    },
    "research": {
      "provider": "perplexity",
      "modelId": "sonar-pro",
      "maxTokens": 8700,
      "temperature": 0.1
    },
    "fallback": {
      "provider": "anthropic",
      "modelId": "claude-sonnet-4-20250514",
      "maxTokens": 120000,
      "temperature": 0.2
    }
  },
  "global": {
    "logLevel": "info",
    "debug": false,
    "defaultSubtasks": 5,
    "defaultPriority": "medium",
    "projectName": "Analog Image Generator",
    "defaultTag": "master",
    "responseLanguage": "English"
  }
}
```

**Management**: Use `task-master models` command, never edit manually

---

### 6.4 Codex Config (`~/.codex/config.toml`)

```toml
model = "gpt-5-codex"
model_reasoning_effort = "high"

[projects."/home/cjh5690/projects/analog-image-generator"]
trust_level = "trusted"
```

**Key Points**:
- `auth.json` in same directory contains OAuth tokens (auto-managed)
- `trust_level = "trusted"` allows Codex to execute commands
- Model preference set to `gpt-5-codex` (highest capability)

---

## 7) Common Task Master Commands (CLI Reference)

### Initialization
```bash
task-master init --rules codex,cursor --yes
```

### Model Management
```bash
task-master models                              # View current config
task-master models --set-main gpt-5-codex       # Set Codex as main
task-master models --set-research sonar-pro     # Set Perplexity for research
task-master models --set-fallback claude-sonnet-4-20250514
```

### PRD & Task Generation
```bash
task-master parse-prd .taskmaster/docs/prd.txt --num-tasks 10 --research
```

### Task Viewing
```bash
task-master list                                # All tasks
task-master list --status pending               # Only pending
task-master list --with-subtasks                # Include subtasks
task-master next                                # Next available task
task-master show 1                              # Specific task
task-master show 1,2,3                          # Multiple tasks
```

### Task Analysis
```bash
task-master analyze-complexity --research       # Analyze all tasks
task-master complexity-report                   # View report
```

### Task Expansion
```bash
task-master expand --id=1 --research            # Expand with research
task-master expand --id=1 --num=7 --force       # Force 7 subtasks
task-master expand --all --research             # Expand all pending
```

### Task Updates
```bash
task-master set-status --id=1.2 --status=done   # Mark subtask done
task-master update-task --id=1 --prompt="..."   # Update single task
task-master update-subtask --id=1.2 --prompt="..." # Append to subtask
task-master update --from=5 --prompt="..."      # Update tasks 5 onwards
```

### Research (Fresh Internet Data)
```bash
task-master research "Latest Python async best practices"
task-master research "React Query v5 migration" --files src/api.js --save-to 3.2
task-master research "JWT security 2025" --tree --detail high
```

### Dependencies
```bash
task-master add-dependency --id=3 --depends-on=1    # Task 3 depends on Task 1
task-master remove-dependency --id=3 --depends-on=1
task-master validate-dependencies                   # Check for issues
task-master fix-dependencies                        # Auto-fix issues
```

### Task Organization
```bash
task-master move --from=5 --to=2.3              # Move task 5 to subtask 2.3
task-master move --from=10,11,12 --to=16,17,18  # Move multiple tasks
task-master remove-task --id=5 --yes            # Delete task
```

### Tags (Multi-Context Management)
```bash
task-master tags                                # List all tags
task-master add-tag feature-xyz --description "New feature work"
task-master use-tag feature-xyz                 # Switch context
task-master copy-tag master feature-xyz         # Copy tasks to new tag
```

### File Generation
```bash
task-master generate                            # Generate task markdown files
```

---

## 8) MCP Tool Loading Modes (Performance Optimization)

### Tool Modes Overview

| Mode | Tools | Context | Use Case |
|------|-------|---------|----------|
| `all` (default) | 44 | ~21K tokens | Full feature set |
| `standard` | 15 | ~10K tokens | Common operations |
| `core`/`lean` | 7 | ~5K tokens | Daily workflow |
| custom | Variable | Variable | Specific tools only |

### Core Tools (7)
- `get_tasks`, `next_task`, `get_task`
- `set_task_status`, `update_subtask`
- `parse_prd`, `expand_task`

### Standard Tools (15)
Core + `initialize_project`, `analyze_project_complexity`, `expand_all`, `add_subtask`, `remove_task`, `generate`, `add_task`, `complexity_report`

### Configuration
```json
"export TASK_MASTER_TOOLS='standard'"  // in MCP config args
```

**Recommendation for Analog Image Generator**: Use `standard` mode for balanced performance

---

## 9) Workflow Integration with Geologic Modeling

### Phase 1: Project Setup
```bash
# 1. Initialize Task Master with geologic workflow
cd /home/cjh5690/projects/analog_image_generator
task-master init --rules codex,cursor --yes

# 2. Create PRD based on AGENTS.md requirements
cp AGENTS.md .taskmaster/docs/fluvial_analogs_prd.txt
# Edit to focus on specific milestones

# 3. Generate tasks from PRD
task-master parse-prd .taskmaster/docs/fluvial_analogs_prd.txt --num-tasks 15 --research
```

### Phase 2: Task Organization by Milestone
```bash
# Create tags for each milestone
task-master add-tag m1-generators --description "M1: Baseline Generators & Masks"
task-master add-tag m2-geologic-index --description "M2: Geologic Principles Index"
task-master add-tag m3-interactive --description "M3: Interactive v20a"
task-master add-tag m4-stats --description "M4: Full Stats (Phase 1 & 2)"
task-master add-tag m5-reporting --description "M5: Reporting"
task-master add-tag m6-qa --description "M6: QA Pass & Recap"

# Move tasks to appropriate milestones
task-master move --from=1,2,3 --to-tag=m1-generators
task-master move --from=4 --to-tag=m2-geologic-index
# ... etc
```

### Phase 3: Iterative Development
```bash
# Work on M1 tasks
task-master use-tag m1-generators
task-master next                    # Get next M1 task
task-master expand --id=1 --research
task-master show 1                  # Review subtasks

# Implement subtask 1.1
# ... code ...

# Log progress
task-master update-subtask --id=1.1 --prompt="Implemented meander_centerline() with variable amplitude control. Tested with 5 different seeds."

# Mark complete
task-master set-status --id=1.1 --status=done
```

### Phase 4: Research Integration
```bash
# Research latest techniques before implementation
task-master research "fluvial geomorphology meandering river modeling 2024" \
  --save-to 1.1 \
  --detail high \
  --files src/geologic_generators.py

# Research validates against current science
task-master research "point bar scroll bar spacing empirical relationships" \
  --save-file
```

### Phase 5: Cross-Milestone Updates
```bash
# If M1 implementation changes M3 requirements
task-master use-tag m3-interactive
task-master update --from=1 --prompt="M1 generators now expose amplitude_range and drift_frac parameters. Update sliders to match new API."
```

---

## 10) Cursor AI Chat Patterns

### Natural Language Commands

Instead of CLI, use Cursor AI chat:

```
"Initialize taskmaster-ai in my project with codex rules"

"Can you parse my PRD at .taskmaster/docs/prd.txt?"

"What's the next task I should work on?"

"Can you help me expand task 4 with research?"

"Show me tasks 1, 3, and 5"

"Mark subtask 2.3 as done"

"Research the latest best practices for implementing variograms in Python"

"Update all tasks from task 5 onwards to reflect the new API we just implemented"

"Can you help me implement task 1.2?"
```

### Interactive Workflow Example

```
You: "What's next?"

AI: "The next task is Task 1.2: 'Implement variable width channel'
     Dependencies: ✅ Task 1.1 is complete
     Details: Channel width should vary along belt based on bankfull parameters..."

You: "Can you expand this task?"

AI: "I'll expand Task 1.2 into subtasks...
     Created 5 subtasks:
     1.2.1: Define width variation function
     1.2.2: Implement spline-based width interpolation
     ..."

You: "Help me implement 1.2.1"

AI: "Let me research current best practices first..."
    [Uses research tool]
    "Based on recent geomorphology literature, here's the implementation..."
    [Writes code]
```

---

## 11) Troubleshooting Guide

### Issue: "TaskMaster MCP transport error: Unexpected token 'N'"

**Cause**: Task Master outputting non-JSON text during startup (usually "Configuration file not found")

**Solution**:
```bash
# Initialize project first to create config.json
cd /home/cjh5690/projects/analog_image_generator
task-master init --yes

# Verify config exists
ls -la .taskmaster/config.json
```

**Prevention**: Always run `task-master init` before connecting MCP

---

### Issue: "No such command: 'task-master'"

**Cause**: Task Master not in PATH or not installed globally

**Solution**:
```bash
# Install globally
npm install -g task-master-ai

# Or use npx
npx task-master-ai --version

# Add to PATH in .bashrc
export PATH="$HOME/.nvm/versions/node/v22.16.0/bin:$PATH"
source ~/.bashrc
```

---

### Issue: Codex CLI "Authentication failed"

**Cause**: OAuth tokens expired or invalid

**Solution**:
```bash
# Re-authenticate with Codex
codex auth logout
codex auth login

# Verify auth
codex "test query"

# Check auth file exists
ls -la ~/.codex/auth.json
```

---

### Issue: MCP server shows "[WARN] No configuration file found"

**Cause**: MCP server starting before initialization complete

**Solution**: This is expected on first run. Initialize the project:
```bash
task-master init --yes
```

After initialization, restart Cursor and the warning should disappear.

---

### Issue: "API key missing" for Codex

**Cause**: Misunderstanding - Codex CLI doesn't need an API key (uses OAuth)

**Solution**: No action needed! Codex CLI uses OAuth tokens in `~/.codex/auth.json`, not API keys.

API keys are only needed for:
- Perplexity (research role)
- Anthropic (fallback role)
- Other optional providers

---

### Issue: Widgets don't render in Jupyter

**Solution**:
```bash
pip install ipywidgets
jupyter nbextension enable --py widgetsnbextension

# For JupyterLab
pip install jupyterlab_widgets

# Restart kernel
```

---

### Issue: Task Master commands work in terminal but not in Cursor AI

**Cause**: MCP server not enabled in Cursor

**Solution**:
1. Open Cursor Settings (Ctrl+Shift+J)
2. Click MCP tab on left
3. Find `task-master-ai`
4. Toggle it **ON**
5. Restart Cursor

---

## 12) Best Practices

### DO ✅

1. **Always initialize before using MCP**
   ```bash
   task-master init --rules codex,cursor --yes
   ```

2. **Use research for complex tasks**
   ```bash
   task-master expand --id=1 --research
   ```

3. **Log implementation progress in subtasks**
   ```bash
   task-master update-subtask --id=1.2 --prompt="Implemented X, found Y works better than Z"
   ```

4. **Use tags for milestone organization**
   ```bash
   task-master add-tag milestone-1 --description "Generators"
   ```

5. **Commit task changes to git**
   ```bash
   git add .taskmaster/tasks/
   git commit -m "Updated task 1.2 status to done"
   ```

6. **Use Cursor AI for natural interaction**
   - "What's next?" instead of `task-master next`
   - "Help me implement task 5" for full assistance

### DON'T ❌

1. **Don't manually edit `.taskmaster/config.json`**
   - Use `task-master models` commands

2. **Don't use `npx` in MCP config on WSL**
   - Always use global install + `wsl.exe` wrapper

3. **Don't skip PRD creation**
   - Tasks generated from PRDs are higher quality

4. **Don't ignore complexity analysis**
   ```bash
   # Always analyze before expanding
   task-master analyze-complexity --research
   ```

5. **Don't forget to update dependent tasks**
   ```bash
   # If task 3 changes, update downstream
   task-master update --from=4 --prompt="Task 3 API changed..."
   ```

6. **Don't mix environments (WSL vs Windows)**
   - Always run Task Master commands in WSL
   - Cursor runs on Windows but connects via wsl.exe

---

## 13) Integration with Existing Geologic Workflow

### Mapping AGENTS.md Roles to Task Master Tags

```bash
# Create tags for each agent role
task-master add-tag geo --description "Lead Geologic Modeler tasks"
task-master add-tag gen --description "Generator Engineer tasks"
task-master add-tag ux --description "UX Engineer tasks"
task-master add-tag stat --description "Stats Engineer tasks"
task-master add-tag rep --description "Reporting Engineer tasks"
task-master add-tag qa --description "QA / Non-Regression tasks"
task-master add-tag doc --description "Doc Steward tasks"
```

### Task Master + Jupyter Notebooks Workflow

1. **PRD Phase**: Create PRD from AGENTS.md milestones
2. **Task Generation**: Parse PRD into tasks
3. **Task Expansion**: Break down into notebook cells
4. **Implementation**: Code in notebooks while updating subtasks
5. **Validation**: QA checks task completion criteria
6. **Documentation**: Update GEOLOGIC_RULES.md from task notes

### Example: Implementing M1 with Task Master

```bash
# 1. Switch to M1 context
task-master use-tag m1-generators

# 2. Get next M1 task
task-master next
# Output: "Task 1: Implement Meandering Generator"

# 3. Research best approaches
task-master research "Python river meandering simulation techniques" \
  --files src/geologic_generators.py \
  --save-to 1

# 4. Expand into subtasks
task-master expand --id=1 --research --num=6

# 5. Work on subtask 1.1
task-master show 1.1
# Implement meander_centerline() in notebook

# 6. Log findings
task-master update-subtask --id=1.1 --prompt="
Implemented centerline with cubic spline interpolation.
Found that n_ctrl=5-7 gives realistic sinuosity.
drift_frac=0.3 prevents excessive wandering.
Tested with seeds 42, 123, 999 - all produce geologically plausible results.
"

# 7. Mark complete
task-master set-status --id=1.1 --status=done

# 8. Move to next subtask
task-master next
```

---

## 14) Advanced Features

### Multi-Environment Development

```bash
# Development on feature branch
git checkout -b feature/braided-generator
task-master add-tag --from-branch  # Creates "feature-braided-generator" tag
task-master use-tag feature-braided-generator

# ... work on feature ...

# Merge back to main
git checkout main
git merge feature/braided-generator
task-master use-tag master
```

### Batch Operations

```bash
# Expand all pending tasks
task-master expand --all --research --force

# Mark multiple tasks done
task-master set-status --id=1,2,3 --status=done

# Move multiple tasks to new parent
task-master move --from=10,11,12 --to=5,6,7
```

### Research-Driven Development

```bash
# Before implementing statistics
task-master research "variogram analysis Python scikit-gstat vs gstools" \
  --detail high \
  --save-to 4.1

# Review research results
task-master show 4.1  # Research appended to task details

# Implement based on research
# ... code ...
```

---

## 15) Version Control & Collaboration

### What to Commit

```bash
# Always commit
git add .taskmaster/tasks/tasks.json
git add .taskmaster/tasks/*.md
git add .taskmaster/docs/prd.txt

# Sometimes commit (if customized)
git add .taskmaster/config.json
git add .cursor/mcp.json

# Never commit
echo ".taskmaster/reports/" >> .gitignore
echo "**/.env" >> .gitignore
```

### Collaboration Patterns

**Solo Development**: Use `master` tag for main work

**Feature Development**: Create branch + tag per feature
```bash
git checkout -b feature/anastomosing
task-master add-tag --from-branch
```

**Milestone-Based**: Tag per milestone (M1, M2, etc.)
```bash
task-master add-tag m1 --copy-from-current
```

---

## 16) Monitoring & Optimization

### Check Model Usage

```bash
# View current config including costs
task-master models

# Monitor which provider is being used
# Codex shows "Free" - perfect! ✅
```

### Optimize Token Usage

```bash
# Use core mode for simple operations
export TASK_MASTER_TOOLS='core'

# Use standard for daily work
export TASK_MASTER_TOOLS='standard'

# Use all for complex operations
export TASK_MASTER_TOOLS='all'
```

### Performance Tips

1. **Use `--research` flag sparingly** (costs money via Perplexity)
2. **Batch similar operations** (expand all at once)
3. **Keep complexity reports** (guides expansion targets)
4. **Archive completed tags** (reduces active context)

---

## 17) Quick Start Checklist

### First-Time Setup

- [ ] Verify Codex CLI installed: `codex --version`
- [ ] Verify Codex authenticated: `codex "test"`
- [ ] Install Task Master: `npm install -g task-master-ai`
- [ ] Configure global MCP: Edit `~/.cursor/mcp.json`
- [ ] Restart Cursor
- [ ] Enable Task Master MCP in settings
- [ ] Test MCP connection: "Can you list available MCP tools?"

### Per-Project Setup

- [ ] Initialize Task Master: `task-master init --rules codex,cursor --yes`
- [ ] Set Codex as main model: `task-master models --set-main gpt-5-codex`
- [ ] Verify config: `task-master models`
- [ ] Create PRD: `.taskmaster/docs/prd.txt`
- [ ] Generate tasks: `task-master parse-prd .taskmaster/docs/prd.txt`
- [ ] Analyze complexity: `task-master analyze-complexity --research`
- [ ] Expand tasks: `task-master expand --all --research`
- [ ] Start coding: `task-master next`

---

## 18) Support & Resources

### Official Documentation
- Task Master: https://task-master.dev
- Codex CLI: Check `codex --help`
- Cursor MCP: https://docs.cursor.com/mcp

### Configuration Files
- Global MCP: `~/.cursor/mcp.json`
- Project MCP: `.cursor/mcp.json`
- Task Master: `.taskmaster/config.json`
- Codex: `~/.codex/config.toml`

### Common Commands Reference Card
```bash
task-master models              # View/configure AI models
task-master list                # View all tasks
task-master next                # Get next task
task-master show <id>           # View task details
task-master expand --id=<id>    # Break down task
task-master set-status --id=<id> --status=done  # Mark complete
task-master research "<query>"  # Get fresh internet data
```

### Getting Help
```bash
task-master --help              # General help
task-master <command> --help    # Command-specific help
task-master models              # Model configuration help
```

---

## 19) Final Word

This guide ensures Codex CLI (GPT-5 via ChatGPT subscription) is properly integrated with Task Master on WSL, providing:

- **Zero API costs** for main task operations
- **Full Task Master functionality** (interactive, analysis, reporting)
- **Seamless Cursor integration** via MCP
- **Research capabilities** via Perplexity (optional, costs apply)
- **Traceability** from geologic principles → tasks → code

Follow the milestones in order (M1 → M7), verify acceptance criteria at each step, and maintain this document as the single source of truth. When configuration changes, update this file and commit to git.

Your geologic modeling workflow (AGENTS.md) now has intelligent task management powered by state-of-the-art AI at zero additional cost! 🚀

---

**Document Version**: 1.0
**Last Updated**: 2025-10-27
**Maintained By**: DOC + CONFIG
**Next Review**: After M7 completion
