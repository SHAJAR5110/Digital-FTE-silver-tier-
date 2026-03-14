# Silver Tier - Phase 5: Email MCP Server Checklist

**Phase**: 5 of 9 (First Action Component)
**Status**: IMPLEMENTATION COMPLETE
**Time**: ~4-5 hours
**Date Started**: 2026-03-13
**Date Completed**: [TBD]

## Overview

Phase 5 builds the **Email MCP Server**, the first "hand" of the Digital FTE. This gives Claude the ability to send emails directly, enabling the complete perception→reasoning→action cycle. The MCP server handles SMTP or Gmail API email sending with proper error handling and logging.

## What Was Built

### ✓ Completed Files

```
Silver Tier/
├── .claude/skills/
│   └── email-sending/
│       ├── SKILL.md                 (✓ NEW - Skill documentation)
│       ├── scripts/
│       │   ├── server.js            (✓ NEW - MCP Server)
│       │   ├── verify.py            (✓ NEW - Verification script)
│       │   ├── start-server.sh      (✓ NEW - Start script)
│       │   └── stop-server.sh       (✓ NEW - Stop script)
│       ├── references/
│       │   └── EMAIL_API.md         (✓ NEW - API documentation)
│       └── skills-lock.json         (✓ NEW - Version lock)
└── PHASE_5_CHECKLIST.md             (✓ This file)
```

### ✓ Email MCP Server Features

- [x] SMTP email sending (Gmail, Outlook, etc.)
- [x] Gmail API integration (alternative to SMTP)
- [x] MCP protocol compliance
- [x] Tool definition for Claude to use
- [x] Email validation (recipient, subject, body)
- [x] Attachment support (files in vault)
- [x] Error handling with detailed messages
- [x] Logging and audit trail
- [x] Configuration via environment variables
- [x] Startup/stop scripts
- [x] Verification script to test functionality

## Setup Instructions

### Step 1: Install Node.js Dependencies

```bash
cd /c/Users/HP/Desktop/H/FTEs/Silver\ Tier/.claude/skills/email-sending

# Check if Node.js is installed
node --version  # Should be v24+

# Install dependencies
npm install
```

### Step 2: Configure Email Provider

Choose either **SMTP** (recommended for Gmail) or **Gmail API**.

#### Option A: SMTP (Gmail with App Password)

```bash
# Update .env:
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password  # NOT your regular password!
SMTP_FROM_NAME=Your Name
```

**How to get Gmail App Password**:
1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification if not done
3. Under "App passwords", select "Mail" and "Windows Computer"
4. Use generated 16-character password in SMTP_PASSWORD

#### Option B: Gmail API

```bash
# Use Gmail credentials from Phase 2
EMAIL_PROVIDER=gmail
EMAIL_GMAIL_CREDENTIALS_PATH=~/.secrets/gmail_credentials.json
EMAIL_GMAIL_USER=your_email@gmail.com
```

### Step 3: Start Email MCP Server

```bash
cd /c/Users/HP/Desktop/H/FTEs/Silver\ Tier/.claude/skills/email-sending

bash scripts/start-server.sh
```

**Expected output**:
```
✓ Email MCP Server started on port 3001
✓ Provider: smtp
✓ Ready to receive requests from Claude Code
```

### Step 4: Verify Server Is Running

```bash
# Check if server is running
python3 scripts/verify.py
```

**Expected output**:
```
✓ Email MCP Server running on port 3001
✓ Provider: smtp
✓ Connected and ready
```

### Step 5: Test Email Sending (Manual)

```bash
# Test with curl
curl -X POST http://localhost:3001/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "to": "your_email@gmail.com",
    "subject": "Test Email",
    "body": "This is a test email from Silver Tier"
  }'
```

**Expected response**:
```json
{
  "success": true,
  "message": "Email sent successfully",
  "messageId": "ABC123..."
}
```

## Verification Checklist

### Prerequisites
- [ ] Node.js v24+ installed: `node --version`
- [ ] npm installed: `npm --version`
- [ ] Email provider configured (SMTP or Gmail API)
- [ ] Gmail App Password created (for SMTP)
- [ ] `.env` file with email credentials
- [ ] Virtual environment activated (Python 3.13+)

### MCP Server Implementation
- [ ] `scripts/server.js` exists (Node.js MCP server)
- [ ] Imports @anthropic-ai/sdk correctly
- [ ] Defines email sending tool for Claude
- [ ] SMTP module implemented (for SMTP provider)
- [ ] Gmail module implemented (for Gmail API provider)
- [ ] Error handling for invalid emails
- [ ] Validation of recipients, subject, body
- [ ] Attachment handling (base64 encoding)
- [ ] Logging all sent emails
- [ ] MCP server listens on port 3001

### Startup/Stop Scripts
- [ ] `scripts/start-server.sh` exists and is executable
- [ ] `scripts/stop-server.sh` exists and is executable
- [ ] start-server.sh activates Node environment
- [ ] start-server.sh logs PID to file
- [ ] stop-server.sh kills server cleanly
- [ ] Error handling for missing dependencies

### Verification Script
- [ ] `scripts/verify.py` exists
- [ ] Checks if server is running on port 3001
- [ ] Tests basic email sending capability
- [ ] Shows provider configuration
- [ ] Shows clear success/failure message

### Documentation
- [ ] `SKILL.md` explains how to use the skill
- [ ] `references/EMAIL_API.md` documents API endpoints
- [ ] `skills-lock.json` tracks version
- [ ] Examples provided for common use cases

### Runtime Testing
- [ ] Server starts without errors
- [ ] Port 3001 is listening
- [ ] Verify.py reports server is ready
- [ ] Manual curl test sends email successfully
- [ ] Email arrives in recipient inbox
- [ ] Server logs show email sent with timestamp
- [ ] Multiple emails can be sent in succession
- [ ] Invalid recipients show error message
- [ ] Missing subject shows error message
- [ ] Empty body is handled gracefully

### Claude Integration
- [ ] Claude Code can see email-sending skill
- [ ] Claude can invoke send_email tool
- [ ] Claude gets success/failure response
- [ ] Claude can handle error messages
- [ ] Server stays running across multiple Claude invocations

## How It Works

### MCP (Model Context Protocol) Flow

```
Claude Code (reasoning layer)
    ↓
    "Claude, send an email to john@example.com with subject 'Urgent: Project Update'"
    ↓
MCP Server discovers available tools
    ↓
Claude uses send_email tool with parameters
    ↓
Email MCP Server receives request
    ↓
Validates email (recipient, subject, body)
    ↓
Connects to SMTP or Gmail API
    ↓
Sends email
    ↓
Returns success/failure to Claude
    ↓
Claude updates vault with sent email log
```

### Tool Definition

Claude has access to:

```
Tool: send_email
Parameters:
  - to: Email address of recipient
  - subject: Email subject
  - body: Email body (markdown or plain text)
  - cc: Optional CC recipients (comma-separated)
  - bcc: Optional BCC recipients (comma-separated)
  - attachments: Optional file paths to attach

Returns:
  - success: true/false
  - message: Status message
  - messageId: Email ID (for tracking)
  - error: Error message if failed
```

## Email Providers

### SMTP (Recommended for Gmail)

**Pros**:
- Works with any email provider (Gmail, Outlook, etc.)
- Simple configuration
- No complex OAuth required

**Cons**:
- Requires app-specific passwords
- May be blocked by some corporate networks

**Configuration**:
```env
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM_NAME=Your Name
```

### Gmail API

**Pros**:
- Uses same OAuth token as Gmail Watcher
- More secure (no password in .env)
- Better integration with Gmail

**Cons**:
- More complex setup
- Requires OAuth credentials file

**Configuration**:
```env
EMAIL_PROVIDER=gmail
EMAIL_GMAIL_CREDENTIALS_PATH=~/.secrets/gmail_credentials.json
EMAIL_GMAIL_USER=your_email@gmail.com
```

## Environment Variables

```env
# Email Provider Selection
EMAIL_PROVIDER=smtp  # Options: smtp, gmail

# SMTP Configuration (if using SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password  # App password, not regular password
SMTP_FROM_NAME=Your Name

# Gmail API Configuration (if using Gmail API)
EMAIL_GMAIL_CREDENTIALS_PATH=~/.secrets/gmail_credentials.json
EMAIL_GMAIL_USER=your_email@gmail.com

# MCP Server Configuration
MCP_PORT=3001
LOG_FILE=~/.logs/email_mcp.log
LOG_LEVEL=info

# Email Configuration
MAX_EMAIL_SIZE=25000000  # 25MB
ALLOWED_RECIPIENTS_DOMAIN=*  # * = any, or specific domain
REQUIRE_APPROVAL=false  # If true, Claude must get approval first
```

## Known Issues & Limitations

### SMTP
- Gmail app passwords are 16 characters (no spaces)
- Some corporate networks block SMTP port 587
- TLS required for security
- Rate limiting: ~300 emails/hour from Gmail

### Gmail API
- Requires OAuth token setup
- Token refresh handled automatically
- Session file location must be accessible
- Rate limiting: ~1000 requests/second per user

### MCP Server
- Runs as separate process (not embedded in Claude)
- Must be started before Claude uses email tool
- Single instance can handle many requests
- No built-in clustering/load balancing

### Email Content
- Max file size per email: 25MB
- No HTML email support (plain text or markdown)
- Attachments must be in vault or accessible path
- BCC may be limited by provider

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "npm ERR!" on install | Check Node.js version: `node --version` (need v24+) |
| "SMTP authentication failed" | Verify app password (not regular password) in .env |
| "Gmail credentials not found" | Check EMAIL_GMAIL_CREDENTIALS_PATH in .env |
| "Port 3001 already in use" | Kill existing process: `pkill -f email-sending` |
| "Email not received" | Check spam folder, verify recipient email |
| "Claude can't see tool" | Restart MCP server: `bash scripts/stop-server.sh && bash scripts/start-server.sh` |
| "Verify.py fails" | Ensure server is running: `bash scripts/start-server.sh` |
| "Too many emails sent" | Implement approval workflow (Phase 6) |
| "TLS connection failed" | Check firewall allows port 587 |

## Commands Reference

### Start Email MCP Server
```bash
cd /c/Users/HP/Desktop/H/FTEs/Silver\ Tier/.claude/skills/email-sending
bash scripts/start-server.sh
```

### Stop Email MCP Server
```bash
bash scripts/stop-server.sh
```

### Verify Server
```bash
python3 scripts/verify.py
```

### View Logs
```bash
tail -f ~/.logs/email_mcp.log
```

### Test Email Sending (curl)
```bash
curl -X POST http://localhost:3001/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "to": "test@example.com",
    "subject": "Test",
    "body": "Test email"
  }'
```

### Check Server Running
```bash
ps aux | grep email-sending
# or
netstat -an | grep 3001
```

## Integration with Claude Code

### Example: Claude sends email after approval

```
User: "Send an email to john@example.com about the project status"

Claude: "I can send that email. Let me draft it for approval first."

[Claude creates /Pending_Approval/EMAIL_john_project.md with draft]

User approves by moving file to /Approved/EMAIL_john_project.md

Claude: "Sending email..."
[Claude uses send_email tool via MCP Server]

[Email MCP Server connects to SMTP and sends]

Claude: "Email sent successfully! Moving to /Done."
```

## Phase 5 Completion Criteria

Phase 5 is **COMPLETE** when:

- [x] Files created: server.js, verify.py, start-server.sh, stop-server.sh, SKILL.md
- [x] Node.js dependencies installed
- [x] Email provider configured (SMTP or Gmail API)
- [ ] MCP server starts without errors
- [ ] Verify.py confirms server is running
- [ ] Manual curl test sends email successfully
- [ ] Email arrives in recipient inbox
- [ ] Server logs show email transaction
- [ ] Claude Code can use send_email tool
- [ ] Multiple emails can be sent
- [ ] Error handling works (invalid email, etc.)
- [ ] Server can be stopped cleanly

## Ready for Phase 6?

Once this checklist is complete, proceed to:

**Phase 6: Approval Workflow** (`PHASE_6_CHECKLIST.md`)

This will implement human-in-the-loop approval for sensitive actions.

---

**Created**: 2026-03-13
**Next Review**: After Phase 5 verification complete
