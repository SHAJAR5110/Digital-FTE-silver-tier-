# CLAUDE.md - Silver Tier

This file provides guidance to Claude Code when working on the Silver Tier of the Digital FTE project.

## Silver Tier Overview

**Estimated Time**: 20-30 hours
**Status**: READY FOR BUILD
**Prerequisites**: Complete Bronze Tier first
**Goal**: Build a functional AI assistant with multiple watchers, email sending, and approval workflows

## Silver Tier Deliverables

- [ ] Copy Bronze Tier vault as foundation
- [ ] Gmail Watcher script (monitors inbox for new emails)
- [ ] WhatsApp Watcher script (via browser automation)
- [ ] LinkedIn Watcher script (monitors messages/notifications)
- [ ] First MCP Server: Email Sending capability
- [ ] Human-in-the-loop approval workflow (APPROVAL_REQUIRED files)
- [ ] Basic scheduling (cron or Task Scheduler for automatic watcher triggers)
- [ ] Claude reasoning loop creating detailed Plan.md files
- [ ] LinkedIn auto-posting for business generation
- [ ] All AI functionality as Agent Skills in `.claude/skills/`

## Architecture for Silver Tier

```
Silver Tier = Automated Perception → Claude Reasoning → Approval-Based Action

Multiple Watcher Scripts (Python)
    ├── Gmail Watcher
    │   ├── Monitors: Gmail inbox
    │   └── Triggers: On new unread emails
    ├── WhatsApp Watcher
    │   ├── Monitors: Web-based WhatsApp
    │   └── Triggers: On new unread messages
    └── LinkedIn Watcher
        ├── Monitors: LinkedIn notifications
        └── Triggers: On new messages/job posts

        ↓ (All write to /Needs_Action)

Claude Code (Scheduled Trigger)
    ├── Reads: /Needs_Action folder
    ├── Thinks: Plans responses with multiple options
    ├── Creates: /Plans/Task_*.md with checklists
    └── Creates: /Pending_Approval/*.md for sensitive actions

        ↓ (Human reviews)

Human Approval + MCP Servers
    ├── Reviews APPROVAL_REQUIRED files
    ├── Approves or rejects actions
    ├── MCP Servers execute (Email, LinkedIn Post)
    └── Updates vault with results
```

## Key Differences from Bronze

### Watchers (Multiple)
- **Bronze**: 1 FileSystem watcher (manual)
- **Silver**: 3+ watchers (Gmail, WhatsApp, LinkedIn) - continuous

### MCP Servers (First Integration)
- **Bronze**: None (manual actions)
- **Silver**: Email sending MCP server (first "hand")

### Approval Workflow
- **Bronze**: Manual review of Plans
- **Silver**: Formal APPROVAL_REQUIRED files for sensitive actions

### Scheduling
- **Bronze**: Manual trigger (`claude code vault`)
- **Silver**: Automated scheduling (cron/Task Scheduler runs Claude periodically)

### LinkedIn Integration
- **Bronze**: None
- **Silver**: Auto-posting for business lead generation

## Silver Tier: Build Path

### Phase 1: Setup Foundation (1-2 hours)
1. Copy Bronze Tier vault to Silver Tier
2. Expand Company_Handbook with new rules (email responses, LinkedIn guidelines)
3. Create `/Pending_Approval` folder for approval workflow
4. Create `/Accounting` folder (prepare for Gold Tier)

### Phase 2: Gmail Watcher (3-4 hours)
1. Set up Google OAuth2 credentials
2. Implement GmailWatcher class (extends BaseWatcher)
3. Monitor "is:unread is:important" emails
4. Create action files with email metadata
5. Test with sample emails

### Phase 3: WhatsApp Watcher (3-4 hours)
1. Implement WhatsAppWatcher (Playwright-based)
2. Monitor web-based WhatsApp
3. Detect unread messages with keywords (urgent, invoice, payment)
4. Create action files with message content
5. Test with sample conversations

### Phase 4: LinkedIn Watcher (2-3 hours)
1. Implement LinkedInWatcher (Playwright-based)
2. Monitor messages and notifications
3. Detect important keywords (opportunity, collaboration, job)
4. Create action files with opportunity summary
5. Test with sample messages

### Phase 5: Email MCP Server (4-5 hours)
1. Build MCP server for sending emails via SMTP or Gmail API
2. Support: recipient, subject, body, attachments
3. Integrate with Claude Code for sending approved emails
4. Test email sending workflow

### Phase 6: Approval Workflow (2-3 hours)
1. Create approval file format: `APPROVAL_REQUIRED_<action>.md`
2. Implement move-to-approve pattern: `/Pending_Approval/<action>.md`
3. Claude creates approval requests for sensitive actions
4. Human moves file to `/Approved` to trigger action
5. Test with sample approval requests

### Phase 7: Scheduling (2-3 hours)
1. **Windows**: Create Task Scheduler job running Claude every 30 minutes
2. **macOS/Linux**: Create cron job running Claude every 30 minutes
3. Ensure watcher scripts run continuously
4. Set up logging for automated runs
5. Test scheduling with sample tasks

### Phase 8: LinkedIn Auto-Posting (2-3 hours)
1. Implement LinkedIn posting MCP server
2. Claude creates post drafts in Plans
3. Human approves via APPROVAL_REQUIRED file
4. MCP server posts to LinkedIn
5. Log posted content

### Phase 9: Testing & Documentation (2-3 hours)
1. End-to-end testing: Email → Watcher → Claude → Approval → MCP Server
2. Test all watchers simultaneously
3. Verify scheduling works reliably
4. Update vault with lessons learned
5. Create tier-specific documentation

## Silver Tier: Folder Structure

```
Silver Tier/
├── CLAUDE.md                    # This file
├── README.md                    # Full documentation (after completion)
├── requirements.txt             # Python + Node.js dependencies
├── AI_Employee_Vault/           # (Copy from Bronze)
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── Inbox/
│   ├── Needs_Action/
│   ├── Plans/
│   ├── Done/
│   ├── Pending_Approval/        # NEW: Approval workflow
│   ├── Approved/                # NEW: Approved actions
│   ├── Accounting/              # NEW: Prepare for Gold
│   └── References/
├── watchers/                    # Python watcher scripts
│   ├── base_watcher.py
│   ├── filesystem_watcher.py    # From Bronze
│   ├── gmail_watcher.py         # NEW
│   ├── whatsapp_watcher.py      # NEW
│   └── linkedin_watcher.py      # NEW
├── .claude/skills/              # Agent Skills
│   ├── browsing-with-playwright/  # From Bronze
│   ├── email-sending/           # NEW: MCP for email
│   └── linkedin-posting/        # NEW: MCP for LinkedIn
└── scripts/
    ├── start-watchers.sh        # Start all watchers
    ├── run-claude.sh            # Run Claude on vault
    └── schedule-claude.sh       # Setup scheduling
```

## Silver Tier: Common Commands

### Start All Watchers
```bash
bash scripts/start-watchers.sh
```

This runs:
- `python3 watchers/filesystem_watcher.py &`
- `python3 watchers/gmail_watcher.py &`
- `python3 watchers/whatsapp_watcher.py &`
- `python3 watchers/linkedin_watcher.py &`

### Trigger Claude Manually
```bash
claude code AI_Employee_Vault
```

### Schedule Claude (Linux/macOS)
```bash
# Add to crontab
crontab -e

# Add line:
*/30 * * * * cd /path/to/silver/tier && claude code AI_Employee_Vault
```

### Schedule Claude (Windows)
```bash
# Create Task Scheduler task
# Trigger: Every 30 minutes
# Action: Run `claude code AI_Employee_Vault`
# See: scripts/schedule-claude.sh for details
```

### Send Test Email via MCP
```bash
bash .claude/skills/email-sending/scripts/start-server.sh
python3 .claude/skills/email-sending/scripts/test-send-email.py
bash .claude/skills/email-sending/scripts/stop-server.sh
```

### Test All Components
```bash
python3 test_setup.py
# Should verify all watchers and MCP servers
```

## Silver Tier: MCP Servers

### Email Sending MCP Server
**Purpose**: Send emails via Claude Code
**Tools**:
- `send_email`: Send immediate email
- `draft_email`: Create draft for approval
- `schedule_email`: Schedule for later

**Workflow**:
```
Claude creates email draft
    ↓
Creates APPROVAL_REQUIRED_Email_*.md
    ↓
Human moves to /Approved/
    ↓
MCP server sends email
    ↓
Claude logs to /Done/
```

### LinkedIn Posting MCP Server (if implemented)
**Purpose**: Post to LinkedIn for business generation
**Tools**:
- `post_to_linkedin`: Immediate post
- `draft_post`: Create draft
- `schedule_post`: Schedule post

**Workflow**: Same as Email (Draft → Approval → Post → Log)

## Silver Tier: Approval Workflow

### Creating Approval Requests

Claude creates file in `/Pending_Approval/`:
```markdown
---
type: approval_required
action: send_email
recipient: client@example.com
priority: high
created: 2026-03-12T10:00:00
---

# Approval Required: Send Email to Client

**Action**: Send email
**To**: client@example.com
**Subject**: Project Update

**Email Body**:
Thank you for your inquiry...

---

**To Approve**: Move this file to `/Approved/`
**To Reject**: Delete this file or move to `/Rejected/`
```

### Human Approval Process
1. Review file in `/Pending_Approval/`
2. Check content, recipient, timing
3. To approve: `mv Pending_Approval/APPROVAL_*.md Approved/`
4. To reject: Delete or move to `/Rejected/`
5. Claude monitors `/Approved/` and executes

## Silver Tier: Scheduling Setup

### macOS/Linux (Cron)
```bash
# Edit crontab
crontab -e

# Run Claude every 30 minutes
*/30 * * * * cd /path/to/Silver\ Tier && \
  /usr/local/bin/claude code AI_Employee_Vault >> logs/claude-run.log 2>&1

# Also keep watchers running (in separate terminal or systemd service)
@reboot bash /path/to/Silver\ Tier/scripts/start-watchers.sh &
```

### Windows (Task Scheduler)
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Repeat task every 30 minutes
4. Action: Run program
   - Program: `claude`
   - Arguments: `code C:\path\to\Silver\Tier\AI_Employee_Vault`
   - Working directory: `C:\path\to\Silver\Tier`

See `scripts/schedule-claude.sh` for PowerShell automation.

## Silver Tier: Testing & Verification

### Test 1: All Watchers Running
```bash
bash scripts/start-watchers.sh
ps aux | grep watcher
# Should show 3+ watcher processes
```

### Test 2: Gmail Watcher
```bash
# Send test email to your account
# Check /Needs_Action for EMAIL_*.md file within 2 minutes
ls AI_Employee_Vault/Needs_Action/EMAIL_*
```

### Test 3: Claude Processes Emails
```bash
claude code AI_Employee_Vault
# Prompt: "Read /Needs_Action and create a plan for responding to emails"
# Should create /Plans/Plan_Email_Responses.md
```

### Test 4: Approval Workflow
```bash
# Check /Pending_Approval folder
ls AI_Employee_Vault/Pending_Approval/
# Should have APPROVAL_REQUIRED_*.md files
```

### Test 5: Email MCP Server
```bash
bash .claude/skills/email-sending/scripts/start-server.sh
python3 .claude/skills/email-sending/scripts/test-send-email.py
bash .claude/skills/email-sending/scripts/stop-server.sh
```

### Test 6: End-to-End
```
1. Receive email → Gmail Watcher creates task
2. Claude processes → Creates Plan + Approval request
3. Human approves → Moves file to /Approved/
4. MCP Server executes → Sends email
5. Claude logs → Moves to /Done/
```

## Silver Tier: Common Issues

| Issue | Solution |
|-------|----------|
| Gmail Watcher not detecting emails | Check OAuth2 credentials, filter syntax |
| WhatsApp Watcher can't detect messages | Ensure browser automation working, check selectors |
| LinkedIn Watcher missing messages | Verify session valid, check for CAPTCHA |
| MCP Server not sending | Check SMTP credentials, network connectivity |
| Claude not triggered by scheduling | Verify cron/Task Scheduler configured correctly |
| Approval workflow not working | Check folder paths, file moved correctly |

## Silver Tier: Completion Checklist

- [ ] Bronze Tier copied as foundation
- [ ] Company_Handbook.md expanded with Silver rules
- [ ] `/Pending_Approval` and `/Approved` folders created
- [ ] Gmail Watcher implemented and tested
- [ ] WhatsApp Watcher implemented and tested
- [ ] LinkedIn Watcher implemented and tested
- [ ] Email MCP server implemented and tested
- [ ] Approval workflow tested end-to-end
- [ ] Scheduling configured (cron or Task Scheduler)
- [ ] Claude reasoning loop creating detailed Plans
- [ ] LinkedIn auto-posting working
- [ ] All watchers running reliably
- [ ] Documentation complete (README.md)

## Next Steps: Gold Tier

When Silver Tier is stable, move to **Gold Tier** which adds:
- Full cross-domain integration
- Odoo Community accounting system
- Facebook, Instagram, Twitter/X integration
- Weekly CEO Briefing generation
- Ralph Wiggum loop for multi-step autonomy
- Comprehensive error recovery and audit logging

Gold Tier estimated time: 40+ hours

## Key Concepts for Silver

**Scheduled Automation**: Watchers run continuously, Claude runs on schedule
**Human-in-the-Loop**: Approval required for sensitive actions
**MCP Servers**: First "hands" - able to send emails, post to social media
**Multi-Domain**: Gmail, WhatsApp, LinkedIn all feeding into single vault
**Scaling**: One approval workflow handles all action types

## Resources

- Root CLAUDE.md: `../CLAUDE.md`
- Bronze CLAUDE.md: `../Bronze Tier/CLAUDE.md`
- Hackathon Guide: `../Personal AI Employee Hackathon 0_...md`
- Playwright docs: https://playwright.dev/python/
- Google OAuth2: https://developers.google.com/identity/protocols/oauth2
- MCP Spec: https://modelcontextprotocol.io/
