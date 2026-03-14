# Silver Tier - Phase 7: Scheduling Checklist

**Phase**: 7 of 9 (Automation)
**Status**: READY TO BUILD
**Time**: ~2-3 hours

## Overview

Phase 7 sets up automated scheduling so Claude Code runs every 30 minutes, processing all pending actions from the vault. This makes the Digital FTE work 24/7 without manual triggers.

## Architecture

```
Scheduled Task (every 30 minutes)
    ↓
Runs: claude code /path/to/vault
    ↓
Claude reads /Needs_Action/
    ↓
Claude analyzes and creates Plans
    ↓
Claude checks /Approved/ for approved actions
    ↓
Claude executes actions via MCP servers
    ↓
Claude logs results to /Done/
    ↓
Wait 30 minutes, repeat
```

## Implementation Options

### Option 1: Windows Task Scheduler (Windows)

**Create scheduled task**:
```powershell
# Run in PowerShell as Administrator
$TaskName = "Digital FTE Claude Runner"
$TaskPath = "\Digital FTE\"
$ScriptPath = "C:\Users\HP\Desktop\H\FTEs\Silver Tier\scripts\run-claude.sh"

# Create trigger for every 30 minutes
New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 30) -Once

# Create action to run script
$Action = New-ScheduledTaskAction -Execute "C:\Program Files\Git\bin\bash.exe" -Argument $ScriptPath

# Create task
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Description "Digital FTE Claude runs every 30 minutes"
```

### Option 2: Cron (Linux/macOS)

**Edit crontab**:
```bash
crontab -e

# Add this line to run every 30 minutes:
*/30 * * * * /c/Users/HP/Desktop/H/FTEs/Silver\ Tier/scripts/run-claude.sh >> ~/.logs/claude_scheduled.log 2>&1
```

### Option 3: Python Scheduler (Any OS)

Create `scripts/scheduler.py`:
```python
import schedule
import time
import subprocess
import os

VAULT_PATH = "/c/Users/HP/Desktop/H/FTEs/Silver Tier/AI_Employee_Vault"

def run_claude():
    subprocess.run(["claude", "code", VAULT_PATH])

schedule.every(30).minutes.do(run_claude)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Configuration

### Update run-claude.sh

```bash
#!/bin/bash
VAULT_PATH="/c/Users/HP/Desktop/H/FTEs/Silver Tier/AI_Employee_Vault"
LOG_FILE="$HOME/.logs/claude_scheduled.log"

echo "[$(date)] Starting Claude run" >> $LOG_FILE
claude code "$VAULT_PATH" >> $LOG_FILE 2>&1
echo "[$(date)] Claude run completed" >> $LOG_FILE
```

### Environment Setup

```bash
# Ensure Claude is in PATH
which claude

# Create log directory
mkdir -p ~/.logs

# Test manual run
bash /c/Users/HP/Desktop/H/FTEs/Silver\ Tier/scripts/run-claude.sh
```

## Verification Steps

- [ ] Scheduled task created (Windows) or cron entry added (Linux/macOS)
- [ ] Claude runs automatically at scheduled time
- [ ] Logs show successful runs: `tail -f ~/.logs/claude_scheduled.log`
- [ ] Vault updates reflect Claude processing
- [ ] Emails are sent when approved
- [ ] No errors in logs
- [ ] All three watchers still running in background
- [ ] Multiple runs don't conflict or duplicate work

## Testing Schedule

1. **Create test item in /Needs_Action**
2. **Wait for next scheduled run** (or trigger manually)
3. **Check /Plans for Claude's response**
4. **Check /Done for completed items**
5. **Verify no duplicates or conflicts**

## Monitoring

**Check if scheduled task is running**:

Windows:
```powershell
Get-ScheduledTaskInfo -TaskName "Digital FTE Claude Runner"
```

Linux/macOS:
```bash
crontab -l | grep "run-claude"
```

**View recent logs**:
```bash
tail -100 ~/.logs/claude_scheduled.log
```

**Manually trigger**:
```bash
bash /c/Users/HP/Desktop/H/FTEs/Silver\ Tier/scripts/run-claude.sh
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Claude command not found" in cron | Add full path to claude in cron entry |
| "Permission denied" on script | Make executable: `chmod +x run-claude.sh` |
| Task runs but does nothing | Check logs, ensure vault path is absolute |
| Duplicate processing | Add timestamp-based deduplication |
| High memory usage | Increase interval to 60 minutes |

## Next: Phase 8

Phase 8 adds LinkedIn posting capability, allowing Claude to auto-post business updates.

---

**Status**: Ready to implement
**Estimated**: 2-3 hours
