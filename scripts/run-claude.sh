#!/bin/bash

# run-claude.sh - Manual trigger to run Claude Code on the vault

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VAULT_PATH="$PROJECT_DIR/AI_Employee_Vault"

# Verify vault exists
if [ ! -d "$VAULT_PATH" ]; then
    echo "ERROR: Vault path not found: $VAULT_PATH"
    exit 1
fi

echo "=== Running Claude Code on Silver Tier Vault ==="
echo "Vault: $VAULT_PATH"
echo ""

# Process any pending approvals BEFORE Claude runs
echo "Step 1: Processing approved actions..."
bash "$PROJECT_DIR/.claude/skills/approval-workflow/process_approvals.sh" 2>/dev/null || echo "  (No approved actions or approval system not ready)"
echo ""

# Run Claude Code
echo "Step 2: Running Claude reasoning..."
claude code "$VAULT_PATH"

echo ""
echo "Step 3: Processing post-Claude approvals..."
bash "$PROJECT_DIR/.claude/skills/approval-workflow/process_approvals.sh" 2>/dev/null || echo "  (No new approvals)"

echo ""
echo "=== Complete ==="
