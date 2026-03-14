# Silver Tier: Functional Assistant (Digital FTE)

Welcome to **Silver Tier** — the functional assistant phase of the Digital FTE project. Silver Tier extends Bronze Tier with multiple watchers, email automation, human-in-the-loop approval workflows, and intelligent scheduling.

## 🎯 What You Get

Silver Tier delivers a **24/7 autonomous assistant** that:

- **Monitors 3 channels** continuously:
  - 📧 Gmail (unread emails)
  - 💬 WhatsApp (unread messages)
  - 🔗 LinkedIn (connection requests, messages, opportunities)

- **Reasons intelligently** about incoming messages via Claude
- **Routes to human approval** before any action
- **Executes approved actions** automatically:
  - Sends emails via SMTP/Gmail API
  - Posts to LinkedIn
  - Logs all activities

- **Runs on schedule** (every 30 minutes) or manually

## ⚡ Quick Start (5 minutes)

### 1. Install Dependencies

```bash
# Python dependencies
pip3 install pyyaml requests google-auth-oauthlib google-auth-httplib2 google-api-python-client playwright python-dotenv

# Install Playwright browsers
playwright install chromium

# Node.js dependencies (for MCP servers)
cd .claude/skills/email-sending && npm install
cd ../linkedin-posting && npm install
cd ../../../
```

### 2. Configure Environment

Create `.env` files in each MCP server directory:

**`.claude/skills/email-sending/.env`:**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_NAME=Your Name
```

**`.claude/skills/linkedin-posting/.env`:**
```
LINKEDIN_ACCESS_TOKEN=your-linkedin-access-token
LINKEDIN_PERSON_ID=your-linkedin-person-id
```

### 3. Initialize Watchers (One-Time Setup)

For Gmail OAuth:
```bash
python3 watchers/gmail_watcher.py
# Browser will open for OAuth approval
```

For WhatsApp QR login:
```bash
python3 watchers/whatsapp_watcher.py
# Scan QR code with your phone
```

For LinkedIn:
```bash
python3 watchers/linkedin_watcher.py
# Logs in with provided credentials
```

### 4. Start the System

**Option A: Manual Trigger**
```bash
bash scripts/run-claude.sh
```

**Option B: Automated Scheduling (Every 30 minutes)**

```bash
# Linux/Mac: Add to crontab
crontab -e
# Add: */30 * * * * /path/to/silver-tier/scripts/run-claude.sh

# Windows: Use Task Scheduler (see PHASE_7_IMPLEMENTATION.md)

# Or use Python scheduler
python3 scripts/scheduler.py
```

## 📁 Project Structure

```
Silver Tier/
├── README.md (this file)
├── CLAUDE.md (tier-specific guidance)
├── .gitignore (secrets protection)
├── AI_Employee_Vault/
│   ├── Needs_Action/          # Incoming tasks from watchers
│   ├── Plans/                 # Claude's analysis & plans
│   ├── Pending_Approval/      # Actions awaiting human approval
│   ├── Approved/              # Approved actions ready to execute
│   ├── Done/                  # Completed actions
│   ├── Dashboard.md           # Real-time status
│   └── Company_Handbook.md    # Rules of engagement
│
├── watchers/                  # Perception layer (monitoring)
│   ├── base_watcher.py        # Abstract base class
│   ├── gmail_watcher.py       # Gmail monitoring
│   ├── whatsapp_watcher.py    # WhatsApp monitoring
│   └── linkedin_watcher.py    # LinkedIn monitoring
│
├── .claude/skills/            # AI Functionality (Agent Skills)
│   ├── email-sending/         # Email MCP server (port 3001)
│   │   ├── server.js
│   │   ├── package.json
│   │   ├── SKILL.md
│   │   ├── .env.example
│   │   └── scripts/
│   │       ├── start-server.sh
│   │       ├── stop-server.sh
│   │       └── verify.py
│   │
│   ├── linkedin-posting/      # LinkedIn MCP server (port 3002)
│   │   ├── server.js
│   │   ├── package.json
│   │   ├── SETUP.md
│   │   ├── .env
│   │   └── scripts/
│   │       ├── start-server.sh
│   │       ├── stop-server.sh
│   │       └── verify.py
│   │
│   └── approval-workflow/     # Approval processing
│       ├── approval_workflow.py
│       ├── create_approval.py
│       └── process_approvals.sh
│
├── scripts/
│   ├── start-watchers.sh      # Start all watchers
│   ├── run-claude.sh          # Run Claude reasoning + approval processing
│   ├── scheduler.py           # Python scheduler (30-min intervals)
│   └── verify-setup.sh        # Verify all components
│
├── documentation/             # Detailed guides
│   ├── PHASE_2_CHECKLIST.md   # Gmail Watcher setup
│   ├── PHASE_3_CHECKLIST.md   # WhatsApp Watcher setup
│   ├── PHASE_4_CHECKLIST.md   # LinkedIn Watcher setup
│   ├── PHASE_5_SETUP.md       # Email MCP server
│   ├── PHASE_6_IMPLEMENTATION.md   # Approval workflow
│   ├── PHASE_7_IMPLEMENTATION.md   # Scheduling setup
│   ├── PHASE_8_IMPLEMENTATION.md   # LinkedIn posting
│   └── PHASE_9_FINAL_IMPLEMENTATION.md  # Testing & deployment
│
└── STATUS.md                  # Project progress tracker
```

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER (24/7)                  │
│  Gmail Watcher (2m) │ WhatsApp (30s) │ LinkedIn Watcher (5m) │
└──────────────┬──────────────────────────────────────────────┘
               │
        Creates *.md files
               │
┌──────────────▼──────────────────────────────────────────────┐
│                  /Needs_Action Folder                        │
│    EMAIL_*.md │ WHATSAPP_*.md │ LINKEDIN_*.md               │
└──────────────┬──────────────────────────────────────────────┘
               │
        Every 30 minutes
               │
┌──────────────▼──────────────────────────────────────────────┐
│                   REASONING LAYER (Claude)                  │
│  Reads /Needs_Action/ → Analyzes → Creates Plans           │
└──────────────┬──────────────────────────────────────────────┘
               │
        Creates APPROVAL_*.md
               │
┌──────────────▼──────────────────────────────────────────────┐
│              APPROVAL LAYER (Human Review)                   │
│   /Pending_Approval/ ← User reviews → /Approved/            │
└──────────────┬──────────────────────────────────────────────┘
               │
        Next scheduled run
               │
┌──────────────▼──────────────────────────────────────────────┐
│                    ACTION LAYER (MCP)                        │
│  Email MCP (3001) │ LinkedIn MCP (3002) │ Results → /Done/  │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 How It Works

### Approval Workflow (Core Safety Feature)

**NO ACTION happens without human approval:**

1. **Watcher detects change** → Creates markdown file in `/Needs_Action/`
2. **Claude processes** → Reads file, creates approval request
3. **Creates APPROVAL_*.md** → Places in `/Pending_Approval/` with:
   - What action is being proposed
   - Who it affects
   - Full content to send/post
   - Timestamp and context
4. **Human reviews** → Opens `/Pending_Approval/APPROVAL_*.md`
5. **Human approves** → Moves file to `/Approved/`
6. **MCP executes** → Email sent or LinkedIn post published
7. **Logs result** → Records in `/Done/` with timestamp and status

### Approval File Format

```yaml
---
type: action_request
action_type: email  # or linkedin_post
recipient: john@example.com
subject: Project Update
status: pending
created_at: 2026-03-14T10:30:00Z
---

# Approval Request: Send Email

## Action
Send email to john@example.com

## Preview
Subject: Project Update

Body:
Hi John,

Thanks for reaching out about the project...

## Review Checklist
- [ ] Recipient is correct
- [ ] Message is professional
- [ ] No sensitive information exposed
- [ ] Tone matches company handbook

**To approve:** Move this file to `/Approved/` folder
```

## 🛠️ Key Components

### Phase 2: Gmail Watcher
- **File**: `watchers/gmail_watcher.py`
- **Frequency**: Every 2 minutes
- **Output**: Creates `EMAIL_*.md` in `/Needs_Action/`
- **Features**: OAuth2 authentication, deduplication, YAML metadata

### Phase 3: WhatsApp Watcher
- **File**: `watchers/whatsapp_watcher.py`
- **Frequency**: Every 30 seconds
- **Output**: Creates `WHATSAPP_*.md` with priority levels
- **Features**: Playwright automation, QR code login, keyword filtering (urgent, invoice, payment)

### Phase 4: LinkedIn Watcher
- **File**: `watchers/linkedin_watcher.py`
- **Frequency**: Every 5 minutes
- **Output**: Creates `LINKEDIN_*.md` with opportunity classification
- **Features**: Email/password auth, opportunity detection, connection request tracking

### Phase 5: Email MCP Server
- **Port**: 3001
- **File**: `.claude/skills/email-sending/server.js`
- **Capabilities**: Send emails via SMTP or Gmail API
- **Startup**: `bash .claude/skills/email-sending/scripts/start-server.sh`

### Phase 6: Approval Workflow
- **File**: `.claude/skills/approval-workflow/approval_workflow.py`
- **Capabilities**: Create approval requests, process approvals, execute actions
- **Core Logic**: ApprovalWorkflow class with human-gating

### Phase 7: Scheduling
- **Options**: Windows Task Scheduler, Linux cron, Python scheduler
- **Interval**: Every 30 minutes (configurable)
- **Logs**: `~/.logs/claude_scheduled.log`

### Phase 8: LinkedIn Posting MCP Server
- **Port**: 3002
- **File**: `.claude/skills/linkedin-posting/server.js`
- **Capabilities**: Post content to LinkedIn with hashtags
- **Startup**: `bash .claude/skills/linkedin-posting/scripts/start-server.sh`

### Phase 9: Monitoring & Alerts
- **Status**: Check `AI_Employee_Vault/Dashboard.md`
- **Logs**: All actions logged to `/Done/` with timestamps
- **Errors**: Tracked in watcher logs for debugging

## ✅ Verification & Testing

### 1. Verify Watchers Are Running
```bash
# Check if processes are active
ps aux | grep watcher

# Check /Needs_Action for new files
ls -la AI_Employee_Vault/Needs_Action/
```

### 2. Test Email Workflow
```bash
# 1. Send test email to your account
# 2. Wait 2 minutes for Gmail watcher
# 3. Run Claude manually
bash scripts/run-claude.sh
# 4. Check /Pending_Approval for approval request
# 5. Approve by moving to /Approved
# 6. Run Claude again - email should send
# 7. Check /Done for logged action
```

### 3. Test WhatsApp Workflow
```bash
# 1. Send yourself a WhatsApp message
# 2. Wait 30 seconds for watcher
# 3. Verify WHATSAPP_*.md appears in /Needs_Action
# 4. Run Claude and approve workflow
```

### 4. Test LinkedIn Workflow
```bash
# 1. Get a LinkedIn message or connection request
# 2. Wait 5 minutes for watcher
# 3. Verify LINKEDIN_*.md appears
# 4. Approve posting through workflow
```

### 5. Verify MCP Servers
```bash
# Email server
python3 .claude/skills/email-sending/scripts/verify.py

# LinkedIn server
python3 .claude/skills/linkedin-posting/scripts/verify.py
```

## 🚀 Deployment Checklist

- [ ] All dependencies installed (`pip3 install ...`)
- [ ] Playwright browsers installed (`playwright install chromium`)
- [ ] OAuth tokens created for Gmail, LinkedIn, WhatsApp
- [ ] .env files configured for MCP servers
- [ ] Watchers tested manually
- [ ] Claude Code can read/write vault
- [ ] Approval workflow tested end-to-end
- [ ] Scheduler configured and running
- [ ] MCP servers verified on ports 3001 and 3002
- [ ] Dashboard.md displays current status
- [ ] Logs are being generated

## 📊 Monitoring Commands

```bash
# Check all watcher processes
ps aux | grep watcher

# View recent approvals
cat AI_Employee_Vault/Pending_Approval/*.md

# View completed actions
cat AI_Employee_Vault/Done/*.md

# Check scheduler logs
tail -f ~/.logs/claude_scheduled.log

# Manual Claude run
bash scripts/run-claude.sh

# Start MCP servers
bash .claude/skills/email-sending/scripts/start-server.sh
bash .claude/skills/linkedin-posting/scripts/start-server.sh
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| Watcher not detecting changes | Check OAuth tokens, verify browser login (WhatsApp) |
| Approval not creating | Verify Claude Code can read vault, check permissions |
| Email not sending | Verify SMTP credentials, check port 3001 server status |
| LinkedIn post fails | Verify access token, check person ID format |
| Scheduler not running | Check cron (Linux) or Task Scheduler (Windows) |
| Duplicate approvals | Clear /Needs_Action and re-run watchers |

## 📚 Documentation

For detailed setup instructions, see:
- **Phase 2**: `documentation/PHASE_2_CHECKLIST.md` (Gmail)
- **Phase 3**: `documentation/PHASE_3_CHECKLIST.md` (WhatsApp)
- **Phase 4**: `documentation/PHASE_4_CHECKLIST.md` (LinkedIn)
- **Phase 5**: `documentation/PHASE_5_SETUP.md` (Email MCP)
- **Phase 6**: `documentation/PHASE_6_IMPLEMENTATION.md` (Approval Workflow)
- **Phase 7**: `documentation/PHASE_7_IMPLEMENTATION.md` (Scheduling)
- **Phase 8**: `documentation/PHASE_8_IMPLEMENTATION.md` (LinkedIn MCP)
- **Phase 9**: `documentation/PHASE_9_FINAL_IMPLEMENTATION.md` (Testing & Deployment)

## 🔐 Security

- **All actions require human approval** before execution
- **Secrets stored locally** — never committed to git
- **OAuth tokens** — refreshed automatically
- **Session data** — encrypted and not synced
- **Logs** — sanitized (no passwords, tokens, or sensitive data)

## 🎯 Next Steps

After Silver Tier is stable:

1. **Test for 24 hours** — Monitor `/Done` folder for proper logging
2. **Refine approval templates** — Customize based on actual messages
3. **Adjust watcher intervals** — Tune timing to your workflow
4. **Move to Gold Tier** — Add Odoo accounting, social media, and advanced autonomy

## 📖 Architecture Guide

For complete architecture, patterns, and tier specifications, see:
- `../CLAUDE.md` — Root project guidance
- `../Personal AI Employee Hackathon 0_...md` — Complete specification
- `CLAUDE.md` — Silver Tier specific guidance

## 💡 Tips & Tricks

1. **Debug approval creation**: Check `AI_Employee_Vault/Plans/` for Claude's reasoning
2. **Monitor vault health**: Run `bash scripts/verify-setup.sh` regularly
3. **Custom rules**: Edit `AI_Employee_Vault/Company_Handbook.md` to guide Claude
4. **Email templates**: Store in `AI_Employee_Vault/References/` for reuse
5. **Test before deploying**: Always run `bash scripts/run-claude.sh` manually first

## 🤝 Support

- **Questions about implementation**: See tier-specific PHASE_*.md files
- **Architecture questions**: See `CLAUDE.md`
- **MCP server issues**: Check respective SKILL.md and SETUP.md files
- **General debugging**: Check vault logs in `/Done/` and scheduler logs

---

**Status**: ✅ Silver Tier Complete — Ready for Production
**Build Time**: 20-30 hours (this implementation: ~2000 lines of code)
**Safety Model**: 100% approval-gated — No automated actions without human review

**Ready to move to Gold Tier?** See `../Gold Tier/CLAUDE.md` for Odoo integration, social media automation, and autonomous intelligence.
