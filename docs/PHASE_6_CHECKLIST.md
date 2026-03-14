# Silver Tier - Phase 6: Approval Workflow Checklist

**Phase**: 6 of 9 (Human-in-Loop)
**Status**: READY TO BUILD
**Time**: ~2-3 hours

## Overview

Phase 6 implements human-in-the-loop approval for sensitive actions. Instead of Claude sending emails directly, Claude creates approval requests that humans review before execution.

## Architecture

```
Claude drafts action
    ↓
Creates /Pending_Approval/ACTION_*.md
    ↓
Human reviews
    ↓
Moves to /Approved/ folder (approval signal)
    ↓
Claude detects approved file
    ↓
Claude executes action via MCP
    ↓
Logs result to /Done/
```

## What to Build

### 1. Approval File Format

Create files with this structure in `/Pending_Approval/`:

```markdown
---
type: email_approval
action_type: send_email
recipient: john@example.com
subject: Quarterly Results
status: pending_approval
created_at: 2026-03-13T22:30:00Z
required_approvals: 1
approvals: []
---

# Approval Required: Send Email

## Action Details
**To**: john@example.com
**Subject**: Quarterly Results

## Draft Content
Please see the attached quarterly results...

## Risks
- Email addresses sensitive financial data
- Consider if recipient needs this information

## Approve or Reject
- Move to /Approved/ to approve
- Delete to reject
```

### 2. Folder Structure

Add to vault:
```
AI_Employee_Vault/
├── Pending_Approval/        # Items awaiting human review
│   └── EMAIL_john_12345.md  # Claude creates these
├── Approved/                # User moves approved items here
│   └── EMAIL_john_12345.md  # Triggers Claude execution
└── Rejected/                # User deletes or moves here
```

### 3. Claude Approval Logic

Implement in Claude (as Agent Skill):

```python
# Check for approved actions in /Approved/
# For each approved file:
#   1. Extract action_type and parameters
#   2. Execute via appropriate MCP (e.g., send_email)
#   3. Log result
#   4. Move to /Done/
```

### 4. Action Types to Support

- `email_approval` - Send email via MCP
- `linkedin_post_approval` - Post to LinkedIn (Phase 8)
- `payment_approval` - Financial transactions (Phase 7)
- `contact_approval` - Add/modify contacts

## Configuration

Add to Company_Handbook.md:

```markdown
## Approval Rules

### Email Approvals Required
- Recipients outside organization
- Bulk emails (>5 recipients)
- Emails with attachments
- Emails referencing sensitive data

### Auto-Approve
- Internal emails to team members
- Routine status updates
- Newsletters and newsletters

### Rejection Criteria
- Grammatical errors (request revision)
- Inappropriate tone
- Missing context
```

## Verification Steps

- [ ] `/Pending_Approval` folder exists
- [ ] `/Approved` folder exists
- [ ] Claude creates approval requests with correct format
- [ ] User can move files to `/Approved/`
- [ ] Claude detects approved files
- [ ] Claude executes approved actions
- [ ] Results logged to `/Done/`
- [ ] Email is actually sent when approved
- [ ] Failed approvals handled gracefully

## Testing

1. **Create approval request manually**:
   ```bash
   # Claude will create this automatically
   touch /Pending_Approval/TEST_APPROVAL.md
   ```

2. **Approve it**:
   ```bash
   mv /Pending_Approval/TEST_APPROVAL.md /Approved/
   ```

3. **Check logs**:
   ```bash
   ls /Done/
   ```

## Next: Phase 7

Phase 7 adds scheduling to run Claude automatically every 30 minutes, making the whole system work 24/7.

---

**Status**: Ready to implement
**Estimated**: 2-3 hours
