#!/bin/bash

# stop-server.sh - Stop the Email MCP Server

LOG_DIR="${HOME}/.logs"
PID_FILE="${LOG_DIR}/email_mcp.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "⚠ No PID file found. Server may not be running."
    echo "Attempting to kill all email-sending processes..."
    pkill -f "node.*server.js" || true
    exit 0
fi

PID=$(cat "$PID_FILE")

if ! kill -0 $PID 2>/dev/null; then
    echo "⚠ Process $PID is not running"
    rm -f "$PID_FILE"
    exit 0
fi

echo "Stopping Email MCP Server (PID: $PID)..."
kill $PID

# Wait for graceful shutdown
sleep 1

if kill -0 $PID 2>/dev/null; then
    echo "Force killing..."
    kill -9 $PID
fi

rm -f "$PID_FILE"
echo "✓ Email MCP Server stopped"
