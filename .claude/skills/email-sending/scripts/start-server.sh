#!/bin/bash

# start-server.sh - Start the Email MCP Server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="${HOME}/.logs"
PID_FILE="${LOG_DIR}/email_mcp.pid"

# Create log directory
mkdir -p "$LOG_DIR"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    echo "Install Node.js v24+ from https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 24 ]; then
    echo "ERROR: Node.js v24+ required (you have $(node --version))"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "$SKILL_DIR/node_modules" ]; then
    echo "Installing Node.js dependencies..."
    cd "$SKILL_DIR"
    npm install
fi

# Check if .env exists
if [ ! -f "$SKILL_DIR/.env" ]; then
    echo "ERROR: .env file not found in $SKILL_DIR"
    echo "Create .env with your email provider configuration"
    echo "See SKILL.md for configuration examples"
    exit 1
fi

# Start the server
echo "Starting Email MCP Server..."
cd "$SKILL_DIR"

node scripts/server.js \
    > "$LOG_DIR/email_mcp.log" 2>&1 &

SERVER_PID=$!
echo $SERVER_PID > "$PID_FILE"

# Wait a moment for server to start
sleep 2

# Check if server started successfully
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "ERROR: Server failed to start"
    echo "Check logs: tail -f $LOG_DIR/email_mcp.log"
    exit 1
fi

echo "✓ Email MCP Server started (PID: $SERVER_PID)"
echo "✓ Listening on port 3001"
echo ""
echo "To verify the server:"
echo "  python3 $SCRIPT_DIR/verify.py"
echo ""
echo "To stop the server:"
echo "  bash $SCRIPT_DIR/stop-server.sh"
echo ""
echo "To view logs:"
echo "  tail -f $LOG_DIR/email_mcp.log"
