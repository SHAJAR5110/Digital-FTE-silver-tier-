# Silver Tier - Phase 4: LinkedIn Watcher Checklist

**Phase**: 4 of 9 (Watchers)
**Status**: IMPLEMENTATION COMPLETE
**Time**: ~2-3 hours
**Date Started**: 2026-03-13
**Date Completed**: [TBD]

## Overview

Phase 4 builds the **LinkedIn Watcher**, the third automated perception component. The LinkedIn Watcher monitors LinkedIn for messages and notifications to detect business opportunities and creates `LINKEDIN_*.md` files in `/Needs_Action`.

## What Was Built

### ✓ Completed Files

```
Silver Tier/
├── watchers/
│   └── linkedin_watcher.py          (✓ NEW - Playwright-based monitoring)
└── PHASE_4_CHECKLIST.md             (✓ This file)
```

### ✓ LinkedIn Watcher Features

- [x] Playwright browser automation for LinkedIn.com
- [x] Email/password authentication (first run)
- [x] Session persistence (no re-login each time)
- [x] Message inbox monitoring
- [x] Notification detection
- [x] Keyword filtering (opportunity, collaboration, job, client, contract, etc.)
- [x] Sender name and message snippet extraction
- [x] Markdown action file generation with YAML front-matter
- [x] Priority assignment (high for opportunities, normal for others)
- [x] Error handling and graceful recovery
- [x] Logging for debugging

## Setup Instructions

### Step 1: Install/Verify Playwright

```bash
cd /c/Users/HP/Desktop/H/FTEs/Silver\ Tier

# Activate virtual environment
source venv/bin/activate

# Verify Playwright is installed (should be from Phase 3)
python3 -c "from playwright.sync_api import sync_playwright; print('✓ Playwright OK')"

# If not installed:
pip install playwright
playwright install chromium
```

### Step 2: Configure .env

**Update these settings**:
```bash
# LinkedIn Session
LINKEDIN_SESSION_PATH=~/.secrets/linkedin_session
LINKEDIN_CHECK_INTERVAL=300  # Check every 5 minutes (slower than WhatsApp)

# LinkedIn Credentials (first login)
LINKEDIN_EMAIL=your_email@linkedin.com
LINKEDIN_PASSWORD=your_password

# Keywords to look for
LINKEDIN_KEYWORD_FILTERS=opportunity,collaboration,job,client,contract,project,partnership,consulting
LINKEDIN_TIMEOUT=60000  # 60 second timeout for page loads
```

**Important Security Notes**:
- Never commit `.env` to git
- Use a dedicated LinkedIn account or ensure 2FA is disabled for automation
- LinkedIn may block automated logins - have backup manual access ready

### Step 3: First Run - Email/Password Login

```bash
cd /c/Users/HP/Desktop/H/FTEs/Silver\ Tier

python3 watchers/linkedin_watcher.py
```

**Expected behavior**:
1. Browser opens (Chromium)
2. LinkedIn login page loads
3. Enters your email (from .env)
4. Enters your password (from .env)
5. Handles 2FA if enabled (you may need to approve)
6. Navigates to messaging/notifications
7. Session saved to `~/.secrets/linkedin_session/`
8. Browser closes
9. Watcher starts monitoring

**Possible Issues**:
- LinkedIn may require "Unusual login activity" approval on phone
- Some accounts require CAPTCHA (manual intervention needed)
- 2FA codes may expire before watcher can use them

### Step 4: Verify Session

Check if session was saved:
```bash
ls -la ~/.secrets/linkedin_session/
```

Expected: Directory with state.json and browser data

### Step 5: Test With Real Connection

**Send yourself a message** (use LinkedIn on phone/web):
1. Search for a connection on LinkedIn
2. Send them a message with keyword like "**opportunity**"
3. Keep watcher running for ~5 minutes (LinkedIn Watcher checks every 300s)

**Check for action file**:
```bash
ls -la /c/Users/HP/Desktop/H/FTEs/Silver\ Tier/AI_Employee_Vault/Needs_Action/LINKEDIN_*
```

**Verify content**:
```bash
cat /c/Users/HP/Desktop/H/FTEs/Silver\ Tier/AI_Employee_Vault/Needs_Action/LINKEDIN_*.md
```

**Expected file format**:
```markdown
---
type: linkedin
sender_name: Jane Smith
message_snippet: I have an opportunity for you
keyword_match: opportunity
timestamp: 2026-03-13T...
detected_at: 2026-03-13T...
status: pending
priority: high
---

# LinkedIn Message: Jane Smith

## Message Details
- **From**: Jane Smith
- **Timestamp**: ...
- **Priority**: 🔴 HIGH
**Keyword Match**: opportunity

## Message Content
I have an opportunity for you...

## Action Items
- [ ] Read full message on LinkedIn
- [ ] Assess opportunity
- [ ] Draft response if interested
- [ ] Move to Done when processed

## Notes
Add analysis below...
```

## Verification Checklist

### Prerequisites
- [ ] Playwright installed: `pip install playwright`
- [ ] Chromium browser installed: `playwright install chromium`
- [ ] Virtual environment activated
- [ ] `.env` file configured with LINKEDIN_EMAIL, LINKEDIN_PASSWORD
- [ ] `~/.secrets/` directory created with proper permissions (700)
- [ ] LinkedIn account has automation enabled or 2FA disabled
- [ ] Valid LinkedIn credentials (will be used in plaintext in .env)

### LinkedIn Watcher Implementation
- [ ] `watchers/linkedin_watcher.py` exists
- [ ] LinkedInWatcher extends BaseWatcher
- [ ] Constructor initializes Playwright and vault path
- [ ] `_authenticate_linkedin()` handles email/password login
- [ ] Session persistence working (no re-login after first run)
- [ ] `check_for_updates()` scans for unread messages
- [ ] Message extraction gets sender and content
- [ ] `_filter_by_keywords()` correctly filters opportunities
- [ ] `create_action_file()` generates proper markdown
- [ ] Filename sanitization prevents special characters
- [ ] Priority assignment: high for opportunities, normal for others
- [ ] Logging shows authentication and message detection

### First Run Tests
- [ ] Browser opens (Chromium)
- [ ] LinkedIn login page loads
- [ ] Email/password credentials auto-filled from .env
- [ ] Login completes successfully
- [ ] Session saved to `~/.secrets/linkedin_session/`
- [ ] Browser closes after successful login
- [ ] No session files if login fails (proper cleanup)
- [ ] Error handling for 2FA (shows message to user)

### Runtime Tests
- [ ] Second run doesn't require login (uses cached session)
- [ ] Test message detected within 5-10 minutes
- [ ] LINKEDIN_*.md file created in /Needs_Action
- [ ] Action file contains sender name
- [ ] Action file contains message snippet
- [ ] Action file has YAML front-matter
- [ ] Action file has priority tags (🔴 HIGH or 🟢 NORMAL)
- [ ] Keyword filtering works (opportunity, collaboration, job, etc.)
- [ ] Multiple messages all detected
- [ ] Check interval properly respects LINKEDIN_CHECK_INTERVAL

### Error Handling
- [ ] Missing Playwright handled gracefully
- [ ] Browser launch failure logged
- [ ] Login timeout shows helpful message
- [ ] Network errors don't crash watcher
- [ ] Invalid vault path handled gracefully
- [ ] Duplicate messages not re-created
- [ ] 2FA errors show clear instructions

### Integration with Vault
- [ ] AI_Employee_Vault/Needs_Action exists
- [ ] Action files readable by Claude Code
- [ ] Manual `claude code AI_Employee_Vault` shows LINKEDIN_*.md files

## Known Issues & Limitations

### Authentication
- LinkedIn may block automated logins (requires phone approval)
- 2FA greatly complicates automation (may require manual approval each time)
- Best practice: disable 2FA on automation account or use dedicated account
- Session expires after ~1 week without use

### Message Detection
- Cannot access notifications reliably (LinkedIn changes HTML structure frequently)
- Message preview may be truncated or missing
- Requires LinkedIn to have message inbox visible
- Cannot filter by message type reliably

### Rate Limiting
- LinkedIn throttles repeated page loads (slow down check interval)
- Too many logins in short time can trigger account block
- Recommended: check interval of 300s or more (5+ minutes)

### Browser Automation
- Slower than WhatsApp (LinkedIn is JS-heavy)
- First load takes 10-20 seconds
- Session file larger (~50MB with cached data)
- Requires more memory (~150MB) due to LinkedIn's complexity

### Keyword Filtering
- Case-insensitive partial matching
- Custom keywords can be set in .env
- Some legitimate messages may be missed
- False positives possible with generic keywords

## Known Workarounds

### Session Expires
```bash
# Clear old session
rm -rf ~/.secrets/linkedin_session/

# Re-run watcher to re-login
python3 watchers/linkedin_watcher.py
```

### Account Locked (Too Many Logins)
- Wait 24 hours before attempting again
- Use phone to approve "Unusual login activity" notification
- Consider dedicated automation account

### Messages Not Detected
- Ensure messages are truly unread
- Check notification settings in LinkedIn (may have muted conversations)
- Increase check interval (LinkedIn may block rapid requests)
- Manually open LinkedIn.com to refresh session

### 2FA Blocking Automation
```env
# Option 1: Disable 2FA (not recommended for main account)
# Option 2: Use dedicated account with 2FA disabled
# Option 3: Increase timeout to allow manual approval:
LINKEDIN_TIMEOUT=300000  # 5 minutes
```

## Performance Considerations

### Check Interval
- **Current default**: 300 seconds (5 minutes)
- **Why**: LinkedIn's heavy JavaScript makes 2-3 minute intervals risky
- **Slower connections**: Increase to 600s (10 minutes)
- **Less activity**: Increase to 900s (15 minutes)

### Memory Usage
- Expect ~150-200MB per browser instance
- Can run 2-3 instances on 4GB RAM
- Higher intervals = lower memory impact

### Rate Limiting
- If checking too frequently, LinkedIn may show CAPTCHA or block access
- 1 check per 5 minutes = ~288 checks/day (safe)
- 1 check per 2 minutes = ~720 checks/day (risky)

## Next Steps (Phase 5)

After Phase 4 is verified:

1. **Update start-watchers.sh** (already done)
   - Gmail, WhatsApp, and LinkedIn all run together

2. **Build Email MCP Server** (Phase 5)
   - Capability to send emails
   - Integrates with Claude approval workflow

3. **Test Multiple Watchers**
   - Run all 3 watchers simultaneously
   - Verify no conflicts or performance issues
   - Check vault updates from all sources

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Playwright not installed" | Run: `pip install playwright && playwright install chromium` |
| Browser won't open | Check if Chrome/Chromium available on system |
| Login fails | Verify email/password in .env, check if account locked |
| "Unusual login activity" blocking | Approve on LinkedIn phone app or use different account |
| 2FA prevents login | Disable 2FA, use dedicated account, or increase timeout |
| No messages detected | Send test message with "opportunity" keyword |
| "Session expired" error | Delete session folder and re-login |
| Browser hangs | Kill with: `pkill -f chromium` or `taskkill /IM chrome.exe` |
| High memory usage | Increase CHECK_INTERVAL to 600+ seconds |
| LinkedIn showing CAPTCHA | Too many logins, wait and retry with longer interval |
| Messages appearing but not detected | Check keyword filters in .env |

## Commands Reference

### Start LinkedIn Watcher
```bash
cd /c/Users/HP/Desktop/H/FTEs/Silver\ Tier
source venv/bin/activate
python3 watchers/linkedin_watcher.py
```

### View Logs
```bash
tail -f ~/.logs/linkedin_watcher.log
```

### Check Action Files
```bash
ls -la /c/Users/HP/Desktop/H/FTEs/Silver\ Tier/AI_Employee_Vault/Needs_Action/LINKEDIN_*
```

### Clear Session and Re-login
```bash
rm -rf ~/.secrets/linkedin_session/
python3 watchers/linkedin_watcher.py
```

### Start All 3 Watchers
```bash
bash scripts/start-watchers.sh
```

### Verify Watcher Running
```bash
ps aux | grep watcher
```

## Environment Variables

```env
# LinkedIn Watcher Configuration
LINKEDIN_EMAIL=your_email@linkedin.com           # Login email
LINKEDIN_PASSWORD=your_password                  # Login password
LINKEDIN_SESSION_PATH=~/.secrets/linkedin_session  # Session storage
LINKEDIN_CHECK_INTERVAL=300                      # 5 minutes (safer)
LINKEDIN_TIMEOUT=60000                           # 60 second page load
LINKEDIN_KEYWORD_FILTERS=opportunity,collaboration,job,client,contract,project,partnership,consulting
```

## Phase 4 Completion Criteria

Phase 4 is **COMPLETE** when:

- [x] File created: linkedin_watcher.py
- [x] Code extends BaseWatcher properly
- [x] Playwright and Chromium verified
- [ ] First run: Login works and session saves
- [ ] Second run: Uses cached session (no login)
- [ ] Test message detected and LINKEDIN_*.md created
- [ ] Action file has correct format with priority
- [ ] Keyword filtering works
- [ ] Multiple messages all detected
- [ ] Logs show no errors
- [ ] Claude Code can read /Needs_Action folder
- [ ] start-watchers.sh includes LinkedIn Watcher

## Ready for Phase 5?

Once this checklist is complete, proceed to:

**Phase 5: Email MCP Server** (`PHASE_5_CHECKLIST.md`)

This will build the first "hand" - the ability to send emails.

---

**Created**: 2026-03-13
**Next Review**: After Phase 4 verification complete
