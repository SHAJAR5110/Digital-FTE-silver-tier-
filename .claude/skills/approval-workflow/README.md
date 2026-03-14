# Approval Workflow Skill - Phase 6

**Status**: Phase 6 Implementation
**Purpose**: Human-in-loop approval for sensitive actions
**Integration**: Works with Phase 5 (Email MCP) and Phase 7 (Scheduling)

## What It Does

The Approval Workflow enables Claude to request human approval before taking sensitive actions:

1. **Claude detects** something that needs approval
2. **Creates approval request** in `/Pending_Approval/`
3. **Waits** for user to review
4. **User moves file** to `/Approved/` to signal go-ahead
5. **Claude executes** action via MCP servers
6. **Logs result** to `/Done/`

## Quick Start

### 1. Files You Get

```
approval-workflow/
├── SKILL.md                    # Usage documentation
├── approval_workflow.py        # Main approval processor
├── create_approval.py          # Helper for Claude
├── process_approvals.sh        # Bash wrapper
├── test_approvals.py           # Testing script
└── README.md                   # This file
```

### 2. Setup (2 minutes)

```bash
# Files are already in place, just make script executable
chmod +x process_approvals.sh

# Ensure vault has required folders
mkdir -p AI_Employee_Vault/{Pending_Approval,Approved,Done}
```

### 3. Test It (5 minutes)

```bash
# Test creating and processing an approval
python3 create_approval.py --test

# Check if folders are created
ls -la AI_Employee_Vault/Pending_Approval/
ls -la AI_Employee_Vault/Approved/

# Manually move a file to test
mv AI_Employee_Vault/Pending_Approval/APPROVAL_* \
   AI_Employee_Vault/Approved/

# Process approvals
bash process_approvals.sh
```

## How It Works

### Folder Flow

```
AI_Employee_Vault/
│
├── Pending_Approval/     ← Claude writes approval requests here
│   └── APPROVAL_send_email_2026-03-13_1.md
│
├── Approved/             ← User moves files here to approve
│   └── APPROVAL_send_email_2026-03-13_1.md
│
└── Done/                 ← Claude moves executed files here
    └── APPROVAL_send_email_2026-03-13_1.md
```

### Approval Request Format

```markdown
---
type: action_approval
action_type: send_email
recipient: john@example.com
subject: Project Update
status: pending_approval
created_at: 2026-03-13T22:30:00Z
required_approvals: 1
approvals: []
---

# Approval Required: Send Email to john@example.com

## Action Details
**To**: john@example.com
**Subject**: Project Update

## Email Content
Here is the project status...

## Review Checklist
- [ ] Is this the right recipient?
- [ ] Is the content accurate?

## To Approve
Move this file to `/Approved/` folder

## To Reject
Delete this file
```

## Python API

### For Claude Code

```python
from approval_workflow import ApprovalWorkflow

workflow = ApprovalWorkflow('./AI_Employee_Vault')

# Create email approval request
filepath = workflow.create_approval_request(
    action_type='send_email',
    title='Approval Required: Send Email',
    metadata={
        'recipient': 'john@example.com',
        'subject': 'Project Update'
    },
    content='...'
)

# Check for approved actions
approved = workflow.get_approved_actions()
for approval in approved:
    result = workflow.execute_approved_action(approval)
    print(f"Executed: {result}")
```

### Helper Functions

```python
# Create email approval
from create_approval import create_email_approval

filepath = create_email_approval(
    vault_path='./AI_Employee_Vault',
    recipient='john@example.com',
    subject='Status Update',
    body='Here is the latest status...'
)

# Create LinkedIn post approval
from create_approval import create_linkedin_approval

filepath = create_linkedin_approval(
    vault_path='./AI_Employee_Vault',
    content='Excited to announce...',
    hashtags=['innovation', 'business']
)
```

## Integration with Claude Code

### Step 1: Claude detects something needs approval

```python
# In Claude's reasoning:
if sensitive_action and requires_approval:
    from create_approval import create_email_approval

    approval_file = create_email_approval(
        vault_path='/path/to/vault',
        recipient=email_address,
        subject=subject,
        body=draft_message
    )

    print(f"Created approval request: {approval_file}")
    print("Waiting for user approval...")
```

### Step 2: User reviews and approves

```bash
# User sees the approval request
cat AI_Employee_Vault/Pending_Approval/APPROVAL_*.md

# User approves by moving to /Approved/
mv AI_Employee_Vault/Pending_Approval/APPROVAL_* \
   AI_Employee_Vault/Approved/
```

### Step 3: Claude executes

```python
# Next Claude run or manual trigger:
from approval_workflow import ApprovalWorkflow

workflow = ApprovalWorkflow('./AI_Employee_Vault')
approved = workflow.get_approved_actions()

for approval in approved:
    result = workflow.execute_approved_action(approval)
    print(f"Executed: {result['message']}")
```

## Configuration

Add approval policies to `Company_Handbook.md`:

```markdown
## Approval Requirements

### Emails Requiring Approval
- External recipients
- Bulk emails (>5 recipients)
- Sensitive content
- With attachments

### Auto-Approve (No approval needed)
- Internal team emails
- Routine status updates
- Known contacts

### LinkedIn Posts
- Always require approval
- Check for professional tone
- Verify no sensitive data
- Confirm hashtags

### Response Time
- Standard: within 1 hour
- Urgent: within 15 minutes
- Critical: within 5 minutes
```

## Testing

### Test 1: Create Email Approval

```bash
python3 -c "
from create_approval import create_email_approval
import os

vault = os.getenv('VAULT_PATH', './AI_Employee_Vault')
f = create_email_approval(vault, 'test@example.com', 'Test', 'Test body')
print(f'Created: {f}')
"
```

### Test 2: Execute Approval

```bash
# 1. Create approval
python3 create_approval.py --test

# 2. Approve it
mv AI_Employee_Vault/Pending_Approval/* \
   AI_Employee_Vault/Approved/

# 3. Execute
bash process_approvals.sh

# 4. Check result
ls AI_Employee_Vault/Done/
```

### Test 3: Full Integration

```bash
# Make sure Email MCP server is running
bash .claude/skills/email-sending/scripts/start-server.sh

# Create and execute approval with real email sending
python3 create_approval.py --test
mv AI_Employee_Vault/Pending_Approval/* \
   AI_Employee_Vault/Approved/
bash process_approvals.sh

# Check email was sent
tail -f ~/.logs/email_mcp.log
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Folder not found" | Ensure `/Pending_Approval` exists: `mkdir -p AI_Employee_Vault/Pending_Approval` |
| "No approved actions" | Check if files moved (not copied) to `/Approved/` |
| "Email MCP not available" | Start email server: `bash .claude/skills/email-sending/scripts/start-server.sh` |
| "Permission denied" | Make script executable: `chmod +x process_approvals.sh` |

## Next Steps

### Immediately (Phase 6)
- ✅ Approval workflow ready
- ✅ Manual approval testing
- ✅ Integration with email sending

### Phase 7 (Scheduling)
- Automate approval detection
- Run every 30 minutes
- Process batches of approvals

### Phase 8 (LinkedIn)
- Extend to LinkedIn post approvals
- Same workflow, different action type
- Integrated with linkedin-posting MCP

## Files Overview

### approval_workflow.py
Main approval processor. Handles:
- Creating approval requests
- Parsing approval files
- Executing approved actions
- Logging results

### create_approval.py
Helper functions for Claude to create approvals:
- `create_email_approval()` - Email approvals
- `create_linkedin_approval()` - LinkedIn post approvals
- Easy to extend for other action types

### process_approvals.sh
Bash wrapper to run approval processor from scripts or cron

### SKILL.md
Complete documentation of approval workflow usage and integration

## Security & Best Practices

✅ **Secure**:
- No action without explicit approval
- Human always has final say
- Audit trail in `/Done/`
- Easy to reject (just delete)

⚠️ **Monitor**:
- Review pending approvals regularly
- Check logs for failed actions
- Audit rejected items
- Keep `/Done/` for history

## Integration Diagram

```
Claude Code (Reasoning)
    ↓
    Detects sensitive action
    ↓
    Creates approval request
    ↓
    /Pending_Approval/APPROVAL_*.md
    ↓
User Reviews Approval File
    ↓
    Moves to /Approved/
    ↓
Next Claude Run (or Phase 7 scheduling)
    ↓
    Detects approved action
    ↓
    Calls MCP Server (Email, LinkedIn, etc.)
    ↓
    Receives result
    ↓
    Logs to /Done/
    ↓
    Complete
```

## Phase 6 Completion

Phase 6 is complete when:
- ✅ Approval workflow files created
- ✅ Folders exist in vault
- ✅ Manual approval testing works
- ✅ Integration with Email MCP tested
- ⏳ Phase 7: Automate with scheduling

---

**Status**: COMPLETE & READY
**Next**: Phase 7 (Scheduling)
**Time**: ~2-3 hours
