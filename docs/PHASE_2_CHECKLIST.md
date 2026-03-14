# Silver Tier - Phase 2: Gmail Watcher Checklist

**Phase**: 2 of 5 (Watchers)
**Status**: IMPLEMENTATION COMPLETE
**Time**: ~3-4 hours
**Date Started**: 2026-03-13
**Date Completed**: [TBD]

## Overview

Phase 2 builds the **Gmail Watcher**, the first automated perception component for Silver Tier. The Gmail Watcher monitors your Gmail inbox for unread emails and creates `EMAIL_*.md` files in `/Needs_Action`, feeding Claude's reasoning loop with real email data.

## What Was Built

### ✓ Completed Files

```
Silver Tier/
├── watchers/
│   ├── base_watcher.py              (✓ Copied from Bronze)
│   └── gmail_watcher.py             (✓ NEW - Gmail OAuth2 implementation)
├── scripts/
│   ├── start-watchers.sh            (✓ NEW - Background startup)
│   └── run-claude.sh                (✓ NEW - Manual trigger)
└── PHASE_2_CHECKLIST.md             (✓ This file)
```

### ✓ Gmail Watcher Features

- [x] OAuth2 authentication with automatic token management
- [x] Monitors Gmail inbox for unread emails
- [x] Creates markdown action files with email metadata
- [x] Deduplicates processed emails by message ID
- [x] Sanitizes filenames from email subjects
- [x] Full YAML front-matter with email metadata
- [x] Markdown template with status checkboxes
- [x] Error handling and logging

## Setup Instructions

### Step 1: Install Dependencies

```bash
cd /c/Users/HP/Desktop/H/FTEs/Silver\ Tier

# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install requirements
pip install -r requirements.txt
```

### Step 2: Set Up Gmail OAuth2 Credentials

1. **Go to Google Cloud Console**: https://console.cloud.google.com/

2. **Create a new project**:
   - Click "Select a Project" → "New Project"
   - Name it "Digital FTE" (or similar)
   - Click "Create"

3. **Enable Gmail API**:
   - Search for "Gmail API"
   - Click "Gmail API" → "Enable"

4. **Create OAuth2 credentials**:
   - Go to "Credentials" (left sidebar)
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Desktop application"
   - Click "Create"

5. **Download credentials**:
   - Click the download icon (⬇️) next to your credentials
   - This downloads `client_secret_*.json`

6. **Save credentials locally**:
   ```bash
   mkdir -p ~/.secrets
   mv ~/Downloads/client_secret_*.json ~/.secrets/gmail_credentials.json
   ```

7. **Create .env file**:
   ```bash
   cp Silver\ Tier/.env.example Silver\ Tier/.env
   ```

8. **Edit .env**:
   ```bash
   VAULT_PATH=/c/Users/HP/Desktop/H/FTEs/Silver\ Tier/AI_Employee_Vault
   GMAIL_CREDENTIALS_PATH=~/.secrets/gmail_credentials.json
   GMAIL_CHECK_INTERVAL=120
   ```

### Step 3: Test Gmail Watcher

```bash
cd /c/Users/HP/Desktop/H/FTEs/Silver\ Tier

# Activate venv
source venv/bin/activate

# Run watcher (will open browser for OAuth on first run)
python3 watchers/gmail_watcher.py
```

**Expected behavior**:
1. Browser opens with Google login page
2. You grant "Gmail read access" permission
3. Watcher starts monitoring
4. Terminal shows: "Gmail Watcher initialized successfully"

### Step 4: Verify With Test Email

1. **Send yourself a test email** with subject "Test Email from Silver Tier"
2. **Keep the watcher running** (let it check for ~2 minutes)
3. **Check for new action file**:
   ```bash
   ls -la /c/Users/HP/Desktop/H/FTEs/Silver\ Tier/AI_Employee_Vault/Needs_Action/
   ```
4. **Verify the email file was created**:
   ```bash
   cat /c/Users/HP/Desktop/H/FTEs/Silver\ Tier/AI_Employee_Vault/Needs_Action/EMAIL_*.md
   ```

**Expected file content**:
```markdown
---
type: email
message_id: <gmail_id>
sender: <your_email@gmail.com>
subject: Test Email from Silver Tier
date: <RFC2822 date>
detected_at: 2026-03-13T...
status: pending
priority: normal
---

# Email: Test Email from Silver Tier
...
```

## Verification Checklist

### Prerequisites
- [ ] Python 3.13+ installed
- [ ] Virtual environment created and activated
- [ ] All requirements.txt dependencies installed
- [ ] Gmail credentials downloaded and saved to `~/.secrets/gmail_credentials.json`
- [ ] `.env` file created and configured with correct paths

### Gmail Watcher Implementation
- [ ] `watchers/base_watcher.py` exists (copied from Bronze)
- [ ] `watchers/gmail_watcher.py` exists and has GmailWatcher class
- [ ] GmailWatcher has `_authenticate()` method (OAuth2 flow)
- [ ] GmailWatcher has `check_for_updates()` method (Gmail API query)
- [ ] GmailWatcher has `create_action_file()` method (markdown creation)
- [ ] `_sanitize_filename()` static method handles special characters
- [ ] `_get_header()` static method extracts email headers
- [ ] Deduplication works (processed_ids set prevents duplicates)
- [ ] Error handling for missing credentials
- [ ] Logging shows authentication and file creation

### Startup Scripts
- [ ] `scripts/start-watchers.sh` exists and is executable
- [ ] `scripts/run-claude.sh` exists and is executable
- [ ] start-watchers.sh activates venv
- [ ] start-watchers.sh starts gmail_watcher.py in background
- [ ] start-watchers.sh logs to `~/.logs/gmail_watcher.log`
- [ ] run-claude.sh points to correct vault path

### Runtime Testing
- [ ] First OAuth2 run opens browser successfully
- [ ] Gmail token saved to `~/.secrets/gmail_token.pickle`
- [ ] Second run uses cached token (no browser)
- [ ] Test email detected within 2 minutes
- [ ] EMAIL_*.md file created in /Needs_Action
- [ ] Action file contains all email metadata (sender, subject, date, snippet)
- [ ] Action file has YAML front-matter
- [ ] Action file has status checkboxes
- [ ] Duplicate emails are not re-created
- [ ] Logs show activity (no errors)

### Integration with Vault
- [ ] AI_Employee_Vault/Needs_Action folder exists
- [ ] AI_Employee_Vault folder structure intact
- [ ] Action files are readable by Claude Code
- [ ] Manual `claude code AI_Employee_Vault` can see EMAIL_*.md files

### Error Handling
- [ ] Missing credentials.json shows helpful error message
- [ ] Network errors logged but don't crash watcher
- [ ] Invalid vault path handled gracefully
- [ ] Duplicate filenames handled with `_1`, `_2` suffix

## Known Issues & Limitations

### OAuth2 Scope
- Current scope: `gmail.readonly` (email reading only)
- Cannot send emails directly from watcher
- Email sending delegated to MCP servers (Phase 3+)

### Unread Email Query
- Monitors `is:unread` emails only
- Ignored: archived, deleted, spam emails
- To change query: edit `q='is:unread'` in `check_for_updates()`

### Token Refresh
- Token expires after 7 days of non-use
- Watcher auto-refreshes on first check after expiry
- If expired >7 days: delete `~/.secrets/gmail_token.pickle` and re-run

### Rate Limiting
- Gmail API: 1000 requests/second per user
- Current setup: 1 request per 120 seconds (safe)
- Can increase check_interval to reduce load

## Next Steps (Phase 3)

After Phase 2 is verified:

1. **Build WhatsApp Watcher** (watchers/whatsapp_watcher.py)
   - Uses Playwright browser automation
   - Monitors web.whatsapp.com for unread messages

2. **Build LinkedIn Watcher** (watchers/linkedin_watcher.py)
   - Monitors LinkedIn for messages/notifications
   - Uses Playwright or unofficial API

3. **Integrate Multiple Watchers**
   - Modify start-watchers.sh to run Gmail + WhatsApp + LinkedIn
   - Each writes to /Needs_Action with domain prefix (EMAIL_, WHATSAPP_, LINKEDIN_)

4. **First MCP Server**
   - Build Email Sending capability
   - Integrate with Claude approval workflow

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Gmail credentials not found" | Verify path in .env matches actual file location |
| OAuth browser doesn't open | Ensure port 0 is available, check firewall |
| "Permission denied" reading token | Check `~/.secrets/` folder permissions |
| Gmail not returning emails | Ensure you have unread emails, check query in code |
| "Invalid grant" error | Delete token.pickle and re-authenticate |
| Watcher exits silently | Check logs: `tail -f ~/.logs/gmail_watcher.log` |
| Duplicate EMAIL_*.md files | Check if watcher is running twice |
| ACTION file not in Needs_Action | Verify vault path is correct absolute path |

## Commands Reference

### Start Gmail Watcher (Background)
```bash
cd /c/Users/HP/Desktop/H/FTEs/Silver\ Tier
bash scripts/start-watchers.sh
```

### Stop Watcher
```bash
kill $(cat ~/.logs/silver_watchers.pid)
```

### View Watcher Logs
```bash
tail -f ~/.logs/gmail_watcher.log
```

### Manual Claude Trigger
```bash
cd /c/Users/HP/Desktop/H/FTEs/Silver\ Tier
bash scripts/run-claude.sh
```

### Check Vault Status
```bash
ls -la /c/Users/HP/Desktop/H/FTEs/Silver\ Tier/AI_Employee_Vault/Needs_Action/
cat /c/Users/HP/Desktop/H/FTEs/Silver\ Tier/AI_Employee_Vault/Needs_Action/EMAIL_*.md
```

### Verify Installation
```bash
python3 -c "from watchers.gmail_watcher import GmailWatcher; print('✓ GmailWatcher imports OK')"
python3 -c "import google.auth; print('✓ Google Auth OK')"
```

## Phase 2 Completion Criteria

Phase 2 is **COMPLETE** when:

- [x] Files created: base_watcher.py, gmail_watcher.py, start-watchers.sh, run-claude.sh
- [x] OAuth2 authentication works (first run opens browser)
- [x] Gmail token saved and reused (no browser on subsequent runs)
- [ ] Test email detected and EMAIL_*.md created in /Needs_Action
- [ ] Action file has correct format (YAML + markdown)
- [ ] Deduplication prevents duplicate files
- [ ] Scripts are executable and tested
- [ ] Logs show no errors
- [ ] Claude Code can read /Needs_Action folder

## Ready for Phase 3?

Once this checklist is complete, proceed to:

**Phase 3: WhatsApp Watcher** (`PHASE_3_CHECKLIST.md`)

---

**Created**: 2026-03-13
**Next Review**: After Phase 2 verification complete
