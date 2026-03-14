#!/bin/bash

# process_approvals.sh - Process approved actions via approval workflow
# This script is called by Claude Code or scheduled task to execute approvals

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")"
VAULT_PATH="${VAULT_PATH:-$PROJECT_DIR/AI_Employee_Vault}"

echo "Processing approved actions from: $VAULT_PATH"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

# Set environment variable
export VAULT_PATH="$VAULT_PATH"

# Run approval workflow processor
python3 "$SCRIPT_DIR/approval_workflow.py"

echo ""
echo "✓ Approval processing complete"
