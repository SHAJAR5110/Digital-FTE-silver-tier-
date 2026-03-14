# Approval Workflow MCP Skill

**Capability**: Human-in-loop approval for sensitive actions
**Status**: Ready
**Phase**: Silver Tier - Phase 6

## Overview

This skill enables Claude to request human approval before executing sensitive actions. Instead of sending emails or posting directly, Claude:
1. **Drafts** the action
2. **Creates approval request** in `/Pending_Approval/`
3. **Waits** for human review
4. **Executes** when user moves file to `/Approved/`
5. **Logs** result to `/Done/`

## Quick Start

### 1. Folder Structure

Ensure vault has these folders:
```
AI_Employee_Vault/
├── Pending_Approval/    # Claude creates approval requests here
├── Approved/           # User moves approved items here
└── Done/              # Claude logs results here
```

### 2. Approval File Format

Claude creates files in `/Pending_Approval/`:

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

# Approval Required: Send Email

## Action Details
**To**: john@example.com
**Subject**: Project Update

## Content
Here's the project status update...

## Risks
- Recipient is external
- Includes project timeline

## Review Checklist
- [ ] Is this the right recipient?
- [ ] Is the content appropriate?
- [ ] Should attachments be included?

## To Approve
Move this file to `/Approved/`

## To Reject
Delete this file or move to `/Rejected/`
```

### 3. How It Works

```
User runs Claude
    ↓
Claude reads /Needs_Action/
    ↓
Claude analyzes and recognizes sensitive action
    ↓
Claude creates approval request in /Pending_Approval/
    ↓
Claude waits for user action
    ↓
User reviews approval file
    ↓
User moves to /Approved/ (approval signal)
    ↓
Next Claude run detects approval
    ↓
Claude executes action via MCP
    ↓
Claude logs result
    ↓
Claude moves to /Done/
```

## Implementation

### Python Approval Detector

```python
from pathlib import Path

class ApprovalWorkflow:
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.pending = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'

    def get_pending_approvals(self):
        """Get all pending approval requests"""
        if not self.pending.exists():
            return []
        return list(self.pending.glob('*.md'))

    def get_approved_actions(self):
        """Get all approved actions ready for execution"""
        if not self.approved.exists():
            return []
        return list(self.approved.glob('*.md'))

    def create_approval_request(self, action_type, content):
        """Create approval request for Claude"""
        filename = f"APPROVAL_{action_type}_{datetime.now().isoformat()[:10]}.md"
        filepath = self.pending / filename
        filepath.write_text(content)
        return filepath

    def execute_approved_action(self, approval_file):
        """Execute approved action via MCP and log result"""
        # Parse approval file
        metadata = self.parse_yaml(approval_file)
        action_type = metadata.get('action_type')

        # Execute based on action type
        if action_type == 'send_email':
            result = self.execute_email(metadata)
        elif action_type == 'linkedin_post':
            result = self.execute_linkedin_post(metadata)

        # Log result
        self.log_execution(approval_file, result)

        # Move to Done
        done_file = self.done / approval_file.name
        approval_file.rename(done_file)

    def parse_yaml(self, filepath):
        """Extract YAML metadata from approval file"""
        import yaml
        with open(filepath) as f:
            content = f.read()
            yaml_str = content.split('---')[1]
            return yaml.safe_load(yaml_str)
```

## Approval Types

### Email Approval

```markdown
---
type: action_approval
action_type: send_email
recipient: email@example.com
subject: Email Subject
status: pending_approval
---

# Approval Required: Send Email
...
```

**Fields**:
- `recipient`: Email address
- `subject`: Email subject
- `body`: Email content (in markdown section)

**Auto-Approve Rules** (no approval needed):
- Internal emails (same domain)
- Routine status updates
- To known contacts

**Require Approval**:
- External recipients
- Sensitive content
- Bulk emails (>5 recipients)

### LinkedIn Post Approval

```markdown
---
type: action_approval
action_type: linkedin_post
target_audience: connections
status: pending_approval
---

# Approval Required: LinkedIn Post
...
```

**Fields**:
- `target_audience`: connections, followers, public
- `hashtags`: list of hashtags
- `media`: list of media files to attach

### Other Action Types (Future)

- `payment_approval` - Financial transactions
- `contact_approval` - Add/modify contacts
- `calendar_approval` - Schedule meetings

## Configuration

Add to `Company_Handbook.md`:

```markdown
## Approval Policies

### Emails Requiring Approval
- [ ] External recipients (outside organization)
- [ ] Bulk emails (>5 recipients)
- [ ] Attachments included
- [ ] Sensitive/confidential content
- [ ] Financial information

### Emails Auto-Approved
- [ ] Internal team members
- [ ] Routine status updates
- [ ] Known contacts (whitelist)
- [ ] Scheduled/automated messages

### LinkedIn Posts Requiring Approval
- [ ] Business offers/services
- [ ] Job postings
- [ ] Company announcements
- [ ] Any posted content (policy: always approve)

### Response Time
- Standard approvals: within 1 hour
- Urgent: within 15 minutes
- Critical: within 5 minutes
```

## Workflow in Action

### Example: Email Workflow

```
1. Watcher detects email from potential client
   ↓
2. EMAIL_inquiry_12345.md in /Needs_Action/
   ↓
3. Claude reads email, recognizes business opportunity
   ↓
4. Claude creates response draft
   ↓
5. Claude creates APPROVAL_email_response.md in /Pending_Approval/
   ↓
6. User reviews approval file
   ↓
7. User reads: "To: john@example.com, Subject: RE: Partnership..."
   ↓
8. User approves by moving to /Approved/
   ↓
9. Next Claude run detects approval
   ↓
10. Claude calls send_email MCP tool
    ↓
11. Email MCP sends response
    ↓
12. Claude logs: "Email sent to john@example.com"
    ↓
13. Files moved to /Done/
```

## Testing

### Test 1: Manual Approval Request

```bash
# 1. Create test approval file
cat > AI_Employee_Vault/Pending_Approval/TEST_APPROVAL.md << 'EOF'
---
type: action_approval
action_type: send_email
recipient: test@example.com
subject: Test Email
status: pending_approval
---

# Approval Required: Test Email

Test content...
EOF

# 2. Verify it appears
ls AI_Employee_Vault/Pending_Approval/

# 3. Move to Approved
mv AI_Employee_Vault/Pending_Approval/TEST_APPROVAL.md \
   AI_Employee_Vault/Approved/

# 4. Claude should process it
claude code AI_Employee_Vault

# 5. Check Done folder
ls AI_Employee_Vault/Done/
```

### Test 2: Claude Creates Approval

```bash
# Set up scenario where Claude detects something that needs approval
# Then manually trigger Claude processing

claude code AI_Employee_Vault

# Check what Claude created:
ls AI_Employee_Vault/Pending_Approval/
cat AI_Employee_Vault/Pending_Approval/APPROVAL_*.md
```

## Integration with Phase 5

When user approves action in `/Approved/`, Claude:
1. Reads approval file
2. Extracts action details (recipient, subject, body)
3. Calls appropriate MCP server (email-sending, linkedin-posting)
4. Logs result
5. Moves to `/Done/`

## Integration with Phase 7

Scheduled Claude runs will:
1. Check `/Approved/` for new items
2. Execute each approved action
3. Log results
4. Clean up folders
5. Process next batch

## Dashboard Updates

Add to `Dashboard.md`:

```markdown
## Approval Status

- Pending Approvals: {{ count /Pending_Approval/ }}
- Approved & Ready: {{ count /Approved/ }}
- Executed Today: {{ count /Done/ with today's date }}
- Rejection Rate: {{ count rejected / total }}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Claude creates approval, user can't find it | Check `/Pending_Approval/` folder |
| Approved file not detected | Ensure file moved (not copied) to `/Approved/` |
| Action not executed | Check logs, verify MCP server running |
| Wrong action executed | Verify `action_type` field in metadata |

## Security Considerations

- ✅ No action without explicit approval
- ✅ Audit trail in `/Done/`
- ✅ Easy to reject (just delete)
- ✅ Human always has final say
- ⚠️ Requires oversight (review approvals regularly)

## Next Steps

- **Phase 7**: Automate approval detection with scheduled runs
- **Phase 8**: Extend to LinkedIn posting approvals
- **Gold Tier**: Advanced approval workflows, delegation

---

**Created**: 2026-03-13
**Status**: Ready for implementation
**Integration**: Works with Phase 5 (Email MCP) and Phase 7 (Scheduling)
