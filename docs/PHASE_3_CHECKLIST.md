# Silver Tier - Phase 3: WhatsApp Watcher Checklist

**Phase**: 3 of 9 (Watchers)
**Status**: IMPLEMENTATION COMPLETE
**Time**: ~3-4 hours
**Date Started**: 2026-03-13
**Date Completed**: [TBD]

## Overview

Phase 3 builds the **WhatsApp Watcher**, the second automated perception component. The WhatsApp Watcher monitors WhatsApp Web for unread messages and creates `WHATSAPP_*.md` files in `/Needs_Action`, feeding Claude with real-time chat data.

## What Was Built

### ✓ Completed Files

```
Silver Tier/
├── watchers/
│   └── whatsapp_watcher.py          (✓ NEW - Playwright-based monitoring)
└── PHASE_3_CHECKLIST.md             (✓ This file)
```

### ✓ WhatsApp Watcher Features

- [x] Playwright browser automation for WhatsApp Web
- [x] QR code scanning on first run (auto-login)
- [x] Session persistence (no re-login each time)
- [x] Unread message detection
- [x] Keyword filtering (urgent, invoice, payment, etc.)
- [x] Contact name extraction
- [x] Message snippet capture
- [x] Markdown action file generation with YAML front-matter
- [x] Error handling and graceful recovery
- [x] Logging for debugging

## Setup Instructions

### Step 1: Install Playwright Browsers

```bash
cd /c/Users/HP/Desktop/H/FTEs/Silver\ Tier

# Activate virtual environment
source venv/bin/activate

# Install Playwright browsers (required for Chrome automation)
playwright install chromium
```

### Step 2: Configure WhatsApp Watcher

**Update `.env` file**:
```bash
cp .env.example .env
```

**Add/update WhatsApp settings**:
```
WHATSAPP_SESSION_PATH=~/.secrets/whatsapp_session
WHATSAPP_CHECK_INTERVAL=30
WHATSAPP_KEYWORD_FILTERS=urgent,invoice,payment,important,asap
WHATSAPP_TIMEOUT=30000
```

### Step 3: First Run - QR Code Login

```bash
cd /c/Users/HP/Desktop/H/FTEs/Silver\ Tier

python3 watchers/whatsapp_watcher.py
```

**Expected behavior**:
1. Playwright opens Chrome browser
2. WhatsApp Web loads (whatsapp.com/web)
3. QR code displayed in browser
4. Scan with your phone camera
5. Watcher auto-detects login completion
6. Session saved to `~/.secrets/whatsapp_session`
7. Browser closes
8. Watcher starts monitoring

### Step 4: Verify Session

Check if session was saved:
```bash
ls -la ~/.secrets/whatsapp_session/
```

Expected directory with session files (cookies, local storage, etc.)

### Step 5: Test With Real Messages

**Send yourself a test message**:
1. Open WhatsApp on your phone
2. Create a new chat with a contact or group
3. Send message: "test message from silver tier"
4. Keep the watcher running for ~1 minute

**Check for action file**:
```bash
ls -la /c/Users/HP/Desktop/H/FTEs/Silver\ Tier/AI_Employee_Vault/Needs_Action/WHATSAPP_*
```

**Verify action file content**:
```bash
cat /c/Users/HP/Desktop/H/FTEs/Silver\ Tier/AI_Employee_Vault/Needs_Action/WHATSAPP_*.md
```

**Expected file format**:
```markdown
---
type: whatsapp
contact_name: Contact Name
message_snippet: test message from silver tier
keyword_match: none
timestamp: 2026-03-13T...
detected_at: 2026-03-13T...
status: pending
priority: normal
---

# WhatsApp Message: Contact Name

## Message Details
- **From**: Contact Name
- **Timestamp**: ...
- **Message**: test message from silver tier

## Status
- [ ] Review message
- [ ] Determine response needed
- [ ] Create response plan if required
- [ ] Move to Done when processed

## Notes
Add analysis or response draft below.
```

## Verification Checklist

### Prerequisites
- [ ] Playwright installed: `pip install playwright`
- [ ] Chromium browser installed: `playwright install chromium`
- [ ] Virtual environment activated
- [ ] `.env` file configured with WHATSAPP_SESSION_PATH
- [ ] `~/.secrets/` directory created with proper permissions

### WhatsApp Watcher Implementation
- [ ] `watchers/whatsapp_watcher.py` exists
- [ ] WhatsAppWatcher extends BaseWatcher
- [ ] Constructor initializes Playwright and vault path
- [ ] `_authenticate_whatsapp()` method handles QR code login
- [ ] Session persistence working (no re-login after first run)
- [ ] `check_for_updates()` scans for unread messages
- [ ] `_extract_unread_messages()` properly detects unread badges
- [ ] `_get_message_snippet()` captures message content
- [ ] `_get_contact_name()` extracts sender/contact name
- [ ] `_filter_by_keywords()` correctly filters important messages
- [ ] `create_action_file()` generates proper markdown
- [ ] Filename sanitization prevents special characters
- [ ] Logging shows authentication and message detection

### First Run Tests
- [ ] Browser opens (Chromium via Playwright)
- [ ] WhatsApp Web loads (whatsapp.com/web)
- [ ] QR code displayed
- [ ] Phone scan logs into WhatsApp
- [ ] Session saved to `~/.secrets/whatsapp_session/`
- [ ] Browser closes after login confirmation
- [ ] No session files if login fails (proper cleanup)

### Runtime Tests
- [ ] Second run doesn't require QR code (uses cached session)
- [ ] Test message detected within 30 seconds
- [ ] WHATSAPP_*.md file created in /Needs_Action
- [ ] Action file contains contact name
- [ ] Action file contains message snippet
- [ ] Action file has YAML front-matter
- [ ] Action file has status checkboxes
- [ ] Keyword filtering works (filters on: urgent, invoice, payment, etc.)
- [ ] Multiple unread messages all detected
- [ ] Timeout handling prevents browser hang

### Error Handling
- [ ] Missing Playwright handled gracefully
- [ ] Browser launch failure logged
- [ ] QR code timeout shows helpful message
- [ ] Network errors don't crash watcher
- [ ] Invalid vault path handled gracefully
- [ ] Duplicate messages not re-created

### Integration with Vault
- [ ] AI_Employee_Vault/Needs_Action exists
- [ ] Action files readable by Claude Code
- [ ] Manual `claude code AI_Employee_Vault` shows WHATSAPP_*.md files

## Known Issues & Limitations

### Browser Automation
- First run slower (browser startup ~5-10 seconds)
- Requires visual login (QR code scan)
- Chromium ~100MB disk space
- Cannot run headless on all systems (some require display)

### WhatsApp Web Limitations
- WhatsApp Web shows only last 100 messages per chat
- Archived chats not automatically monitored
- Must manually open chat to see message previews
- Session expires if not accessed for ~1-2 weeks

### Message Detection
- Only monitors chats currently visible in chat list
- Muted chats still checked but won't highlight as unread
- Group messages harder to filter than 1:1 chats
- Cannot access media files (images, documents) in messages

### Keywords
- Filtering is case-insensitive
- Partial matching (e.g., "pay" matches "payment")
- Custom keywords can be set in .env file

### Performance
- Check interval: 30 seconds (customizable)
- Slows down if many unread messages
- Browser memory: ~100MB per instance

## Known Workarounds

### Session Expires
```bash
# Clear old session
rm -rf ~/.secrets/whatsapp_session/

# Re-run watcher to re-login
python3 watchers/whatsapp_watcher.py
```

### Messages Not Detected
- Open WhatsApp Web in browser to refresh
- Ensure messages are truly unread (not just archived)
- Check chat list is visible (watcher might have hidden it)

### Browser Won't Close
```bash
# Force kill hanging Chromium processes
pkill -f chromium
# Or on Windows:
taskkill /IM chrome.exe /F
```

### High CPU Usage
- Reduce CHECK_INTERVAL from 30 to 60+ seconds
- Disable keyword filtering (check all messages)
- Close other browser windows to reduce competition

## Next Steps (Phase 4)

After Phase 3 is verified:

1. **Build LinkedIn Watcher** (watchers/linkedin_watcher.py)
   - Uses Playwright for LinkedIn.com
   - Monitors messages and notifications
   - Detects opportunities (job posts, collaboration requests)

2. **Integrate Multiple Watchers**
   - Modify start-watchers.sh to run Gmail + WhatsApp + LinkedIn
   - Each watcher runs independently in background

3. **CloudFlare/JavaScript Challenges**
   - Some sites may have anti-bot detection
   - Add random delays and user-agent rotation if needed

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Playwright not installed" | Run: `pip install playwright` |
| "chromium not found" | Run: `playwright install chromium` |
| Browser won't open | Check if DISPLAY set (on Linux/macOS) |
| QR code doesn't appear | WhatsApp Web might be loading, wait 10s |
| QR code timeout (>30s) | Check internet connection, increase timeout in .env |
| No session saved | Check ~/.secrets/ permissions (should be 700) |
| "Session expired" error | Delete session folder and re-login |
| No messages detected | Send yourself message with "urgent" keyword |
| Browser hangs | Kill with: `pkill -f chromium` or `taskkill /IM chrome.exe` |
| High memory usage | Increase CHECK_INTERVAL to 60+ seconds |
| Multiple WHATSAPP_*.md for same message | Increase dedup timeout or check for duplicate logins |

## Commands Reference

### Start WhatsApp Watcher
```bash
cd /c/Users/HP/Desktop/H/FTEs/Silver\ Tier
source venv/bin/activate
python3 watchers/whatsapp_watcher.py
```

### View Watcher Logs
```bash
# If running in background
tail -f ~/.logs/whatsapp_watcher.log
```

### Check Created Action Files
```bash
ls -la /c/Users/HP/Desktop/H/FTEs/Silver\ Tier/AI_Employee_Vault/Needs_Action/WHATSAPP_*
```

### Clear Session and Re-login
```bash
rm -rf ~/.secrets/whatsapp_session/
python3 watchers/whatsapp_watcher.py  # Will prompt for QR scan again
```

### Test Message Detection
```bash
# Send message with keyword
whatsapp_send "test urgent message"

# Check vault
ls /c/Users/HP/Desktop/H/FTEs/Silver\ Tier/AI_Employee_Vault/Needs_Action/WHATSAPP_*
```

## Environment Variables

```env
# WhatsApp Watcher Configuration
WHATSAPP_SESSION_PATH=~/.secrets/whatsapp_session
WHATSAPP_CHECK_INTERVAL=30          # Seconds
WHATSAPP_TIMEOUT=30000              # Milliseconds
WHATSAPP_HEADLESS=false             # Show browser (true = hidden, but may fail)
WHATSAPP_KEYWORD_FILTERS=urgent,invoice,payment,important,asap
WHATSAPP_MESSAGE_LIMIT=50           # Max messages to check per run
```

## Phase 3 Completion Criteria

Phase 3 is **COMPLETE** when:

- [x] File created: whatsapp_watcher.py
- [x] Code extends BaseWatcher properly
- [x] Playwright and Chromium installed
- [ ] First run: QR code appears and login works
- [ ] Session persists: second run doesn't require QR
- [ ] Test message detected and WHATSAPP_*.md created
- [ ] Action file has correct format
- [ ] Keyword filtering works
- [ ] Browser properly closes after login
- [ ] Logs show no errors
- [ ] Claude Code can read /Needs_Action folder
- [ ] Multiple unread messages all detected

## Ready for Phase 4?

Once this checklist is complete, proceed to:

**Phase 4: LinkedIn Watcher** (`PHASE_4_CHECKLIST.md`)

---

**Created**: 2026-03-13
**Next Review**: After Phase 3 verification complete
