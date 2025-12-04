#!/bin/bash
# sync-template.sh - Sync stock files from project-template
# Version: 1.0.0
#
# Usage:
#   ./scripts/sync-template.sh [options]
#
# Options:
#   --dry-run         Preview changes without applying
#   --template PATH   Use local template path (default: ~/projects/project-template)
#   --git URL         Use git remote URL instead of local path
#   --commands        Also sync .claude/commands/ files
#   --skills          Also sync .claude/skills/ files
#   --all             Sync all template files (rules + commands + skills)
#   --force           Overwrite without prompting
#   --check-versions  Show version info for synced files

set -e

# Configuration
TEMPLATE_PATH="${TEMPLATE_PATH:-$HOME/projects/project-template}"
TEMPLATE_GIT=""
DRY_RUN=false
SYNC_COMMANDS=false
SYNC_SKILLS=false
FORCE=false
CHECK_VERSIONS=false
TEMP_DIR=""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Stock files to sync
STOCK_RULES=(
    "docs/rules/git-workflow.md"
    "docs/rules/python-standards.md"
    "docs/rules/self-improve.md"
    "docs/MCP_SETUP.md"
)

STOCK_COMMANDS=(
    ".claude/commands/lint.md"
    ".claude/commands/test.md"
    ".claude/commands/tasks.md"
    ".claude/commands/task-status.md"
    ".claude/commands/prd.md"
)

STOCK_SKILLS=(
    ".claude/skills/code-review/SKILL.md"
    ".claude/skills/debugging/SKILL.md"
    ".claude/skills/git-recovery/SKILL.md"
)

# Cleanup function
cleanup() {
    if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
    fi
}
trap cleanup EXIT

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true ;;
        --template) TEMPLATE_PATH="$2"; shift ;;
        --git) TEMPLATE_GIT="$2"; shift ;;
        --commands) SYNC_COMMANDS=true ;;
        --skills) SYNC_SKILLS=true ;;
        --all) SYNC_COMMANDS=true; SYNC_SKILLS=true ;;
        --force) FORCE=true ;;
        --check-versions) CHECK_VERSIONS=true ;;
        --help|-h)
            head -20 "$0" | tail -n +2 | sed 's/^# //'
            exit 0
            ;;
        *) echo -e "${RED}Unknown parameter: $1${NC}"; exit 1 ;;
    esac
    shift
done

echo -e "${BLUE}Template Sync Tool v1.0.0${NC}"
echo "=========================="

# Check for saved template source if none provided
if [ -z "$TEMPLATE_GIT" ] && [ "$TEMPLATE_PATH" = "$HOME/projects/project-template" ]; then
    if [ -f ".template/source" ]; then
        SAVED_SOURCE=$(cat .template/source)
        if [[ "$SAVED_SOURCE" == http* ]] || [[ "$SAVED_SOURCE" == git@* ]]; then
            TEMPLATE_GIT="$SAVED_SOURCE"
            echo "Using saved template source: $TEMPLATE_GIT"
        elif [ -d "$SAVED_SOURCE" ]; then
            TEMPLATE_PATH="$SAVED_SOURCE"
            echo "Using saved template path: $TEMPLATE_PATH"
        fi
    fi
fi

# If git URL provided, clone to temp directory
if [ -n "$TEMPLATE_GIT" ]; then
    TEMP_DIR=$(mktemp -d)
    echo "Cloning template from: $TEMPLATE_GIT"
    git clone --depth 1 --quiet "$TEMPLATE_GIT" "$TEMP_DIR"
    TEMPLATE_PATH="$TEMP_DIR"
    echo -e "${GREEN}Cloned successfully${NC}"
else
    echo "Template source: $TEMPLATE_PATH"
fi
echo ""

if [ ! -d "$TEMPLATE_PATH" ]; then
    echo -e "${RED}Error: Template directory not found at $TEMPLATE_PATH${NC}"
    echo ""
    echo "Options:"
    echo "  1. Set TEMPLATE_PATH environment variable"
    echo "  2. Use --template /path/to/template"
    echo "  3. Use --git https://github.com/user/project-template.git"
    exit 1
fi

# Build file list
FILES_TO_SYNC=("${STOCK_RULES[@]}")
if [ "$SYNC_COMMANDS" = true ]; then
    FILES_TO_SYNC+=("${STOCK_COMMANDS[@]}")
fi
if [ "$SYNC_SKILLS" = true ]; then
    FILES_TO_SYNC+=("${STOCK_SKILLS[@]}")
fi

# Check versions mode
if [ "$CHECK_VERSIONS" = true ]; then
    echo -e "${BLUE}Version Check${NC}"
    echo "-------------"
    for file in "${FILES_TO_SYNC[@]}"; do
        local_file="./$file"
        template_file="$TEMPLATE_PATH/$file"

        local_ver="(not found)"
        template_ver="(not found)"

        if [ -f "$local_file" ]; then
            local_ver=$(grep -oP '(?<=template-version: )[0-9.]+' "$local_file" 2>/dev/null || echo "(no version)")
        fi
        if [ -f "$template_file" ]; then
            template_ver=$(grep -oP '(?<=template-version: )[0-9.]+' "$template_file" 2>/dev/null || echo "(no version)")
        fi

        if [ "$local_ver" = "$template_ver" ]; then
            echo -e "  $file: ${GREEN}$local_ver${NC}"
        else
            echo -e "  $file: ${YELLOW}$local_ver -> $template_ver${NC}"
        fi
    done
    exit 0
fi

# Ensure directories exist
mkdir -p docs/rules
if [ "$SYNC_COMMANDS" = true ]; then
    mkdir -p .claude/commands
fi
if [ "$SYNC_SKILLS" = true ]; then
    mkdir -p .claude/skills/code-review
    mkdir -p .claude/skills/debugging
    mkdir -p .claude/skills/git-recovery
fi

# Sync files
for file in "${FILES_TO_SYNC[@]}"; do
    template_file="$TEMPLATE_PATH/$file"
    local_file="./$file"

    if [ ! -f "$template_file" ]; then
        echo -e "${YELLOW}Skip: $file (not in template)${NC}"
        continue
    fi

    if [ ! -f "$local_file" ]; then
        echo -e "${GREEN}New: $file${NC}"
        if [ "$DRY_RUN" = false ]; then
            mkdir -p "$(dirname "$local_file")"
            cp "$template_file" "$local_file"
            echo "  -> Created"
        fi
        continue
    fi

    # Check if files differ
    if diff -q "$template_file" "$local_file" > /dev/null 2>&1; then
        echo -e "Same: $file"
    else
        echo -e "${YELLOW}Changed: $file${NC}"
        if [ "$DRY_RUN" = true ]; then
            echo "  Diff preview:"
            diff --color=always "$local_file" "$template_file" 2>/dev/null | head -15 || true
        elif [ "$FORCE" = true ]; then
            cp "$template_file" "$local_file"
            echo -e "  ${GREEN}Updated (forced)${NC}"
        else
            echo "  Local file differs from template."
            read -p "  Overwrite with template version? [y/N/d(iff)] " -n 1 -r
            echo
            case $REPLY in
                y|Y)
                    cp "$template_file" "$local_file"
                    echo -e "  ${GREEN}Updated${NC}"
                    ;;
                d|D)
                    diff --color=always "$local_file" "$template_file" || true
                    read -p "  Overwrite? [y/N] " -n 1 -r
                    echo
                    if [[ $REPLY =~ ^[Yy]$ ]]; then
                        cp "$template_file" "$local_file"
                        echo -e "  ${GREEN}Updated${NC}"
                    else
                        echo "  Skipped"
                    fi
                    ;;
                *)
                    echo "  Skipped"
                    ;;
            esac
        fi
    fi
done

echo ""
if [ "$DRY_RUN" = true ]; then
    echo "Dry run complete. No files were modified."
    echo "Run without --dry-run to apply changes."
else
    # Record template source for future syncs
    mkdir -p .template
    if [ -n "$TEMPLATE_GIT" ]; then
        echo "$TEMPLATE_GIT" > .template/source
    else
        echo "$TEMPLATE_PATH" > .template/source
    fi

    # Record template version if available
    if [ -f "$TEMPLATE_PATH/.template-version" ]; then
        cp "$TEMPLATE_PATH/.template-version" .template/version
    fi

    echo -e "${GREEN}Sync complete.${NC}"
    echo "Template source saved to .template/source"
fi
