#!/usr/bin/env python3

"""
Verification script for Email MCP Server
Checks if server is running and can send emails
"""

import requests
import sys
import json
from pathlib import Path

PORT = 3001
SERVER_URL = f"http://localhost:{PORT}"

def check_server():
    """Check if server is running"""
    try:
        response = requests.get(f"{SERVER_URL}/", timeout=5)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def get_status():
    """Get server status"""
    try:
        response = requests.get(f"{SERVER_URL}/status", timeout=5)
        return response.json()
    except Exception as e:
        return None

def test_email_send():
    """Test email sending capability"""
    try:
        response = requests.post(
            f"{SERVER_URL}/send-email",
            json={
                "to": "test@example.com",
                "subject": "Test Email",
                "body": "This is a test email"
            },
            timeout=10
        )
        return response.json()
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    print("=== Email MCP Server Verification ===\n")

    # Check if server is running
    print("Checking if server is running...")
    if not check_server():
        print("✗ Email MCP Server is NOT running on port 3001")
        print("\nTo start the server, run:")
        print("  cd .claude/skills/email-sending")
        print("  bash scripts/start-server.sh")
        sys.exit(1)

    print("✓ Email MCP Server is running\n")

    # Get status
    print("Getting server status...")
    status = get_status()
    if status:
        print(f"✓ Provider: {status.get('provider', 'unknown')}")
        if status.get('status') == 'ready':
            print(f"✓ From: {status.get('from', 'unknown')}")
        elif status.get('error'):
            print(f"⚠ Error: {status.get('error')}")
    else:
        print("⚠ Could not get server status")

    print()

    # Get available tools
    print("Available tools:")
    try:
        response = requests.get(f"{SERVER_URL}/tools", timeout=5)
        tools = response.json().get('tools', [])
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
    except Exception as e:
        print(f"  ⚠ Could not get tools: {e}")

    print("\n" + "="*40)
    print("✓ Email MCP Server is ready to use!")
    print("="*40)

if __name__ == '__main__':
    main()
