# Email Sending MCP Skill

**Capability**: Send emails via SMTP or Gmail API
**Status**: Ready
**Phase**: Silver Tier - Phase 5

## Overview

This MCP (Model Context Protocol) server enables Claude Code to send emails directly. It acts as the first "hand" of the Digital FTE - the ability to take action in the real world.

## Quick Start

### 1. Configure Email Provider

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your email provider
# SMTP (Gmail recommended):
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
SMTP_FROM_NAME=Your Name
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Start Server

```bash
bash scripts/start-server.sh
```

### 4. Verify Server

```bash
python3 scripts/verify.py
```

## Usage in Claude Code

Once the server is running, Claude Code can send emails automatically:

```
User: "Send an email to john@example.com about the quarterly results"

Claude: "I'll draft an email and send it."

[Claude uses the send_email tool]

Claude: "Email sent successfully to john@example.com"
```

## Tool Definition

Claude has access to the `send_email` tool with these parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `to` | string | Yes | Recipient email (comma-separated for multiple) |
| `subject` | string | Yes | Email subject |
| `body` | string | Yes | Email body (plain text or markdown) |
| `cc` | string | No | CC recipients (comma-separated) |
| `bcc` | string | No | BCC recipients (comma-separated) |
| `attachments` | array | No | File paths to attach |

## Email Providers

### SMTP (Recommended)

Works with Gmail, Outlook, or any SMTP server.

**Gmail Setup**:
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification" if not done
3. Create "App password" for "Mail" and "Windows Computer"
4. Use the 16-character password in .env

```env
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
SMTP_FROM_NAME=Your Name
```

### Gmail API

Uses the same OAuth credentials as Gmail Watcher (Phase 2).

```env
EMAIL_PROVIDER=gmail
EMAIL_GMAIL_CREDENTIALS_PATH=~/.secrets/gmail_credentials.json
EMAIL_GMAIL_USER=your_email@gmail.com
```

## API Endpoints

### POST /send-email

Send an email.

**Request**:
```json
{
  "to": "recipient@example.com",
  "subject": "Email Subject",
  "body": "Email body text",
  "cc": "cc@example.com",
  "bcc": "bcc@example.com",
  "attachments": ["/path/to/file.pdf"]
}
```

**Response (Success)**:
```json
{
  "success": true,
  "message": "Email sent successfully",
  "messageId": "ABC123...",
  "recipients": ["recipient@example.com"],
  "timestamp": "2026-03-13T22:30:00.000Z"
}
```

**Response (Error)**:
```json
{
  "success": false,
  "error": "Invalid email address: bad@email"
}
```

### GET /status

Get current server status and configuration.

**Response**:
```json
{
  "status": "ready",
  "provider": "smtp",
  "host": "smtp.gmail.com",
  "from": "your_email@gmail.com"
}
```

### GET /tools

Get available MCP tools.

## Testing

### Test with curl

```bash
curl -X POST http://localhost:3001/send-email \
  -H "Content-Type: application/json" \
  -d '{
    "to": "test@example.com",
    "subject": "Test Email",
    "body": "This is a test email"
  }'
```

### Test with verification script

```bash
python3 scripts/verify.py
```

### Check logs

```bash
tail -f ~/.logs/email_mcp.log
```

## Common Use Cases

### 1. Send Simple Email

```python
# Claude would do this automatically
send_email(
  to="client@example.com",
  subject="Project Update",
  body="The project is on track. See attached report."
)
```

### 2. Send Email with Attachments

```python
send_email(
  to="team@example.com",
  subject="Weekly Report",
  body="Please find attached the weekly report.",
  attachments=["/vault/Reports/weekly.pdf"]
)
```

### 3. Send to Multiple Recipients

```python
send_email(
  to="john@example.com,jane@example.com",
  cc="manager@example.com",
  subject="Team Meeting Notes",
  body="Here are the meeting notes..."
)
```

## Integration with Approval Workflow

In Phase 6, email sending will be gated by approval:

```
1. Claude drafts email → Creates /Pending_Approval/EMAIL_*.md
2. User reviews and approves → Moves to /Approved/
3. Claude sends email → Uses send_email tool
4. Log written → Moves to /Done/
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "smtp.gmail.com: connect ECONNREFUSED" | Network error or firewall blocking port 587 |
| "Invalid login: application-specific password required" | Use app password, not regular password |
| "Email not received" | Check spam folder, verify recipient email address |
| "Port 3001 already in use" | Kill existing process: `pkill -f email-sending` |
| "npm ERR! code ERESOLVE" | Try: `npm install --legacy-peer-deps` |
| "Node.js command not found" | Install Node.js v24+: https://nodejs.org/ |

## Configuration Reference

```env
# Email Provider
EMAIL_PROVIDER=smtp              # smtp or gmail

# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
SMTP_FROM_NAME=Digital FTE

# Gmail API Configuration (alternative)
EMAIL_GMAIL_CREDENTIALS_PATH=~/.secrets/gmail_credentials.json
EMAIL_GMAIL_USER=your_email@gmail.com

# MCP Server
MCP_PORT=3001
LOG_FILE=~/.logs/email_mcp.log
LOG_LEVEL=info

# Email Settings
MAX_EMAIL_SIZE=25000000          # 25MB max email size
ALLOWED_RECIPIENTS_DOMAIN=*      # * for any, or specific domain
REQUIRE_APPROVAL=false           # If true, manual approval required
```

## Files

```
email-sending/
├── SKILL.md                      (this file)
├── .env                          (configuration - DO NOT COMMIT)
├── .env.example                  (example configuration)
├── package.json                  (Node.js dependencies)
├── scripts/
│   ├── server.js                 (MCP server implementation)
│   ├── start-server.sh           (start server)
│   ├── stop-server.sh            (stop server)
│   └── verify.py                 (verification script)
├── references/
│   └── EMAIL_API.md              (detailed API documentation)
└── skills-lock.json              (version lock)
```

## Support

For issues:
1. Check logs: `tail -f ~/.logs/email_mcp.log`
2. Run verification: `python3 scripts/verify.py`
3. Test with curl: See "Testing" section above
4. Check configuration: `cat .env`

## Next Steps

- **Phase 6**: Implement approval workflow for sensitive emails
- **Phase 7**: Add scheduling for automated emails
- **Phase 8**: Integration with LinkedIn posting

---

**Created**: 2026-03-13
**Version**: 1.0.0
**Status**: Ready for use
