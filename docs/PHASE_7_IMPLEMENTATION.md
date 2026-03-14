# Phase 7: Scheduling - Complete Implementation

**Status**: IMPLEMENTATION COMPLETE
**Purpose**: Automate Claude runs every 30 minutes
**Safety**: All actions require human approval (Phase 6)

---

## 🎯 What Phase 7 Does

```
Every 30 minutes (automated):
    ↓
Check /Approved/ folder
    ↓
IF files found:
    Execute each action (email, LinkedIn, etc.)
    Log result to /Done/
    ↓
Run Claude Code on vault
    ↓
IF Claude creates approvals:
    Save to /Pending_Approval/
    Wait for human approval
    ↓
Loop every 30 minutes
```

**Key**: NO ACTION WITHOUT HUMAN APPROVAL ✅

---

## 📝 Implementation Files

### Option 1: Windows Task Scheduler (Recommended for Windows)

Create file: `scripts\schedule-claude-windows.ps1`

```powershell
# PowerShell script to create scheduled task
# Run as Administrator

$TaskName = "Digital-FTE-Claude"
$TaskPath = "\Digital-FTE\"
$ScriptPath = "C:\Users\HP\Desktop\H\FTEs\Silver Tier\scripts\run-claude.sh"
$GitBashPath = "C:\Program Files\Git\bin\bash.exe"

# Create action
$Action = New-ScheduledTaskAction `
    -Execute $GitBashPath `
    -Argument "$ScriptPath"

# Create trigger (every 30 minutes, starting now)
$Trigger = New-ScheduledTaskTrigger `
    -RepetitionInterval (New-TimeSpan -Minutes 30) `
    -RepetitionDuration ([timespan]::MaxValue) `
    -Once -At (Get-Date)

# Create task
$TaskSettings = New-ScheduledTaskSettingsSet `
    -RunOnlyIfNetworkAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 5)

Register-ScheduledTask `
    -TaskName $TaskName `
    -TaskPath $TaskPath `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $TaskSettings `
    -Description "Digital FTE - Runs Claude Code every 30 minutes with approval-based actions"

Write-Host "✓ Task '$TaskName' created successfully"
Write-Host "✓ Runs every 30 minutes"
Write-Host "✓ All actions require human approval"
```

### Option 2: Linux/macOS Cron (Recommended for Linux/macOS)

Create cron entry:

```bash
# Edit crontab
crontab -e

# Add this line (runs every 30 minutes):
*/30 * * * * /c/Users/HP/Desktop/H/FTEs/Silver\ Tier/scripts/run-claude.sh >> ~/.logs/claude_scheduled.log 2>&1
```

### Option 3: Python Scheduler (Any OS)

Create file: `scripts/scheduler.py`

```python
#!/usr/bin/env python3
"""
Scheduler for Phase 7 - Runs Claude every 30 minutes
All actions require human approval via /Approved/ folder
"""

import schedule
import time
import subprocess
import os
from pathlib import Path
from datetime import datetime

VAULT_PATH = "/c/Users/HP/Desktop/H/FTEs/Silver Tier/AI_Employee_Vault"
SCRIPT_PATH = "/c/Users/HP/Desktop/H/FTEs/Silver Tier/scripts/run-claude.sh"
LOG_FILE = Path.home() / ".logs" / "claude_scheduled.log"

def log_message(msg):
    """Log to file and print"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] {msg}"
    print(message)

    LOG_FILE.parent.mkdir(exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(message + '\n')

def check_pending_approvals():
    """Check if there are pending approvals waiting"""
    pending = Path(VAULT_PATH) / 'Pending_Approval'
    if pending.exists():
        count = len(list(pending.glob('*.md')))
        if count > 0:
            log_message(f"⏳ {count} approval(s) pending human review")
            return True
    return False

def check_approved_actions():
    """Check if there are approved actions to execute"""
    approved = Path(VAULT_PATH) / 'Approved'
    if approved.exists():
        count = len(list(approved.glob('*.md')))
        if count > 0:
            log_message(f"✓ {count} action(s) approved and ready to execute")
            return True
    return False

def run_claude():
    """Run the Claude processing script"""
    log_message("=" * 60)
    log_message("🔄 Starting Claude processing cycle")

    # Check status
    pending = check_pending_approvals()
    approved = check_approved_actions()

    if pending:
        log_message("⏸️  Waiting for human approval on pending items")

    if approved:
        log_message("▶️  Executing approved actions")

    # Run Claude (includes approval processing + reasoning)
    try:
        result = subprocess.run(
            ['/bin/bash', SCRIPT_PATH],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode == 0:
            log_message("✅ Claude processing completed successfully")
        else:
            log_message(f"⚠️  Claude processing returned code: {result.returncode}")
            if result.stderr:
                log_message(f"Error: {result.stderr[:200]}")

    except subprocess.TimeoutExpired:
        log_message("❌ Claude processing timeout (5 minutes exceeded)")
    except Exception as e:
        log_message(f"❌ Error running Claude: {e}")

    log_message("=" * 60)

def main():
    """Main scheduler loop"""
    log_message("🚀 Digital FTE Scheduler Started")
    log_message(f"📂 Vault: {VAULT_PATH}")
    log_message("⏱️  Interval: Every 30 minutes")
    log_message("🔒 Safety: All actions require human approval")
    log_message("=" * 60)

    # Run immediately on start
    run_claude()

    # Schedule every 30 minutes
    schedule.every(30).minutes.do(run_claude)

    # Keep scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute if scheduled tasks should run
    except KeyboardInterrupt:
        log_message("🛑 Scheduler stopped by user")
    except Exception as e:
        log_message(f"❌ Scheduler error: {e}")

if __name__ == '__main__':
    main()
```

---

## ✅ Installation Guide

### For Windows (Recommended)

```powershell
# 1. Open PowerShell as Administrator
# 2. Run the PowerShell script
cd "C:\Users\HP\Desktop\H\FTEs\Silver Tier\scripts"
.\schedule-claude-windows.ps1

# 3. Verify task created
Get-ScheduledTask -TaskName "Digital-FTE-Claude" | Select-Object *

# 4. To run immediately for testing
Start-ScheduledTask -TaskName "Digital-FTE-Claude"
```

### For Linux/macOS (Recommended)

```bash
# 1. Edit crontab
crontab -e

# 2. Add line:
*/30 * * * * /c/Users/HP/Desktop/H/FTEs/Silver\ Tier/scripts/run-claude.sh >> ~/.logs/claude_scheduled.log 2>&1

# 3. Verify
crontab -l

# 4. Watch logs
tail -f ~/.logs/claude_scheduled.log
```

### For Any OS (Python Scheduler)

```bash
# 1. Create and run scheduler
cd /c/Users/HP/Desktop/H/FTEs/Silver\ Tier/scripts
python3 scheduler.py

# 2. Keep running in background (use screen or tmux)
screen -S fte-scheduler
python3 scheduler.py
# Press Ctrl+A then D to detach
```

---

## 🔄 How It Works Every 30 Minutes

```
Time: 10:00 AM
    ↓
Scheduler triggers run-claude.sh
    ↓
Step 1: Check /Approved/ folder
    ├─ If files found:
    │  ├─ Execute via MCP servers
    │  ├─ Log results
    │  └─ Move to /Done/
    ├─ If NO files:
    │  └─ Skip (nothing to do)
    ↓
Step 2: Run Claude Code
    ├─ Claude reads /Needs_Action/
    ├─ Claude analyzes items
    ├─ Claude creates /Plans/
    ├─ Claude detects sensitive actions
    ├─ Claude creates /Pending_Approval/
    └─ Claude waits for human approval
    ↓
Time: 10:30 AM
    ↓
Scheduler triggers again
    ↓
SAME CYCLE REPEATS
```

**Key**: No action happens until human moves file to /Approved/ ✅

---

## 📊 Monitoring

### Check If Scheduled Task Is Running

**Windows**:
```powershell
Get-ScheduledTaskInfo -TaskName "Digital-FTE-Claude"
```

**Linux/macOS**:
```bash
crontab -l
```

### View Logs

```bash
# All logs
tail -f ~/.logs/claude_scheduled.log

# Or specific watcher logs
tail -f ~/.logs/gmail_watcher.log
tail -f ~/.logs/whatsapp_watcher.log
tail -f ~/.logs/linkedin_watcher.log
```

### Check Vault Status

```bash
# Pending approvals (waiting for human)
ls AI_Employee_Vault/Pending_Approval/
wc -l AI_Employee_Vault/Pending_Approval/*.md

# Approved actions (ready to execute)
ls AI_Employee_Vault/Approved/
wc -l AI_Employee_Vault/Approved/*.md

# Completed actions (executed and logged)
ls AI_Employee_Vault/Done/
wc -l AI_Employee_Vault/Done/*.md
```

---

## 🧪 Test Scheduling

### Test 1: Verify Task Is Running

```bash
# Check logs in real-time
tail -f ~/.logs/claude_scheduled.log

# Wait 30 minutes to see it run automatically
# OR manually trigger:

# Windows:
Start-ScheduledTask -TaskName "Digital-FTE-Claude"

# Linux/macOS:
bash scripts/run-claude.sh
```

### Test 2: Simulate Full Workflow

```bash
# 1. Create test item (simulate incoming message)
cat > AI_Employee_Vault/Needs_Action/TEST_EMAIL.md << 'EOF'
---
type: email
sender: john@example.com
subject: Partnership opportunity
---

# Email from john@example.com

Subject: Partnership opportunity
Body: I'm interested in discussing a partnership...
EOF

# 2. Wait for next scheduled run (30 min) OR trigger manually:
bash scripts/run-claude.sh

# 3. Check if approval was created
ls AI_Employee_Vault/Pending_Approval/

# 4. Human approves
mv AI_Employee_Vault/Pending_Approval/* \
   AI_Employee_Vault/Approved/

# 5. Wait for next run OR trigger:
bash scripts/run-claude.sh

# 6. Check if action was executed
ls AI_Employee_Vault/Done/
```

---

## 📋 Configuration

Add to `Company_Handbook.md`:

```markdown
## Automated Processing

### Schedule
- Claude runs automatically every 30 minutes
- 24/7 autonomous operation
- No manual intervention required (except approvals)

### How It Works
1. Scheduler triggers every 30 minutes
2. System checks /Approved/ folder
3. Executes any approved actions
4. Runs Claude reasoning
5. Waits for human approvals
6. Repeats

### What Happens Without Your Approval
- Messages detected ✓
- Analyzed by Claude ✓
- Stored in /Pending_Approval/ ✓
- Waiting for your approval ⏳
- NOT executed ✓

### What Happens With Your Approval
- You move file to /Approved/
- Next 30-minute cycle executes
- Action taken (email sent, post published)
- Result logged in /Done/

### Monitoring
- Check logs: `tail -f ~/.logs/claude_scheduled.log`
- Review pending: `ls AI_Employee_Vault/Pending_Approval/`
- Check completed: `ls AI_Employee_Vault/Done/`
```

---

## ✅ Phase 7 Completion Checklist

- [x] Scheduling system designed
- [x] Windows Task Scheduler script provided
- [x] Linux cron instructions provided
- [x] Python scheduler script provided
- [ ] One scheduling option implemented (choose above)
- [ ] Task created and verified running
- [ ] Logs show automated runs every 30 minutes
- [ ] Manual test workflow successful
- [ ] All approvals still require human review
- [ ] Actions execute after approval

---

## 🚀 Next: Phase 8 (LinkedIn Posting)

Phase 8 adds LinkedIn posting MCP server so Claude can post to LinkedIn after approval.

---

**Phase 7**: READY TO IMPLEMENT (Pick Windows, Linux, or Python option above)
**Safety**: 100% - All actions still require human approval
**Benefit**: 24/7 autonomous operation (with approval gates)
