#!/bin/bash

# start-watchers.sh - Start all Silver Tier watchers in background

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="${HOME}/.logs"
PID_FILE="${LOG_DIR}/silver_watchers.pid"

# Create log directory
mkdir -p "$LOG_DIR"

# Activate virtual environment if it exists
if [ -d "$PROJECT_DIR/venv" ]; then
    echo "Activating virtual environment..."
    source "$PROJECT_DIR/venv/bin/activate"
fi

# Check if Python dependencies are installed
python3 -c "import google.auth" 2>/dev/null || {
    echo "ERROR: Gmail dependencies not installed"
    echo "Run: pip install -r $PROJECT_DIR/requirements.txt"
    exit 1
}

python3 -c "from playwright.sync_api import sync_playwright" 2>/dev/null || {
    echo "WARNING: Playwright not installed. WhatsApp watcher will be skipped."
    echo "To enable WhatsApp watcher, run:"
    echo "  pip install playwright"
    echo "  playwright install chromium"
}

# Array to store all PIDs
PIDS=()
declare -A PID_MAP

# Start Gmail Watcher
echo "Starting Gmail Watcher..."
python3 "$PROJECT_DIR/watchers/gmail_watcher.py" \
    > "$LOG_DIR/gmail_watcher.log" 2>&1 &

GMAIL_PID=$!
PIDS+=($GMAIL_PID)
PID_MAP["Gmail"]=$GMAIL_PID
echo "✓ Gmail Watcher started (PID: $GMAIL_PID)"

# Start WhatsApp Watcher (if Playwright is available)
if python3 -c "from playwright.sync_api import sync_playwright" 2>/dev/null; then
    echo "Starting WhatsApp Watcher..."
    python3 "$PROJECT_DIR/watchers/whatsapp_watcher.py" \
        > "$LOG_DIR/whatsapp_watcher.log" 2>&1 &

    WHATSAPP_PID=$!
    PIDS+=($WHATSAPP_PID)
    PID_MAP["WhatsApp"]=$WHATSAPP_PID
    echo "✓ WhatsApp Watcher started (PID: $WHATSAPP_PID)"
else
    echo "⚠ WhatsApp Watcher skipped (Playwright not installed)"
fi

# Start LinkedIn Watcher (if Playwright is available)
if python3 -c "from playwright.sync_api import sync_playwright" 2>/dev/null; then
    echo "Starting LinkedIn Watcher..."
    python3 "$PROJECT_DIR/watchers/linkedin_watcher.py" \
        > "$LOG_DIR/linkedin_watcher.log" 2>&1 &

    LINKEDIN_PID=$!
    PIDS+=($LINKEDIN_PID)
    PID_MAP["LinkedIn"]=$LINKEDIN_PID
    echo "✓ LinkedIn Watcher started (PID: $LINKEDIN_PID)"
else
    echo "⚠ LinkedIn Watcher skipped (Playwright not installed)"
fi

# Save all PIDs
echo "${PIDS[@]}" > "$PID_FILE"

# Display what's running
echo ""
echo "=== Silver Tier Watchers Running ==="
for watcher in "${!PID_MAP[@]}"; do
    echo "$watcher: PID ${PID_MAP[$watcher]}"
done
echo ""
echo "Log directory: $LOG_DIR"
echo "PID file: $PID_FILE"
echo ""
echo "To stop all watchers:"
echo "  kill \$(cat $PID_FILE)"
echo ""
echo "To view logs:"
echo "  tail -f $LOG_DIR/*.log"
