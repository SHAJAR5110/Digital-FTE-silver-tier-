# Phase 6: Approval Workflow - Implementation Guide

**Status**: COMPLETE & READY TO TEST
**Time**: ~2-3 hours
**Date**: 2026-03-13

---

## 🎯 What Phase 6 Delivers

Phase 6 implements **human-in-the-loop approval** for sensitive actions:

```
Claude decides to take action
    ↓
Creates approval request in /Pending_Approval/
    ↓
User reviews: "Should Claude send this email?"
    ↓
User approves by moving file to /Approved/
    ↓
Next Claude run executes the action
    ↓
Result logged to /Done/
```

**Result**: No sensitive action happens without human approval ✅

---

## 📁 Files Created

```
Silver Tier/
├── .claude/skills/approval-workflow/           ✅ NEW SKILL
│   ├── SKILL.md                                (Usage guide)
│   ├── README.md                               (Implementation)
│   ├── approval_workflow.py                    (Main processor)
│   ├── create_approval.py                      (Helper for Claude)
│   └── process_approvals.sh                    (Executable wrapper)
│
└── scripts/
    └── run-claude.sh                           ✅ UPDATED
        (Now includes approval processing)
```

---

## ✅ Immediate Setup (5 minutes)

### Step 1: Verify Folder Structure

```bash
cd /c/Users/HP/Desktop/H/FTEs/Silver\ Tier

# Verify approval folders exist
ls -la AI_Employee_Vault/Pending_Approval/
ls -la AI_Employee_Vault/Approved/
ls -la AI_Employee_Vault/Done/

# If not, create them:
mkdir -p AI_Employee_Vault/{Pending_Approval,Approved,Done}
```

### Step 2: Test Approval Creation

```bash
# Create a test approval
cd .claude/skills/approval-workflow
python3 create_approval.py --test
```

**Expected output**:
```
Creating test email approval...
✓ Created: /c/Users/HP/Desktop/H/FTEs/Silver Tier/AI_Employee_Vault/Pending_Approval/APPROVAL_send_email_2026-03-13_0.md

Creating test LinkedIn approval...
✓ Created: /c/Users/HP/Desktop/H/FTEs/Silver Tier/AI_Employee_Vault/Pending_Approval/APPROVAL_linkedin_post_2026-03-13_1.md

Test complete!
Check /c/Users/HP/Desktop/H/FTEs/Silver Tier/AI_Employee_Vault/Pending_Approval/ for files
```

### Step 3: Review Approval File

```bash
# Look at what was created
cat AI_Employee_Vault/Pending_Approval/APPROVAL_send_email_*.md
```

**Should see**:
```markdown
---
type: action_approval
action_type: send_email
recipient: john@example.com
...
---

# Approval Required: Send Email to john@example.com

## Action Details
**To**: john@example.com
**Subject**: Project Update

## Email Content
Here is the latest project status...

## Review Checklist
- [ ] Is this the right recipient?
- [ ] Is the content accurate?

## To Approve
Move this file to `/Approved/` folder
```

---

## 🧪 Test Approval Workflow (10 minutes)

### Test 1: Manual Approval (No MCP)

```bash
# 1. Check pending approvals
ls -la AI_Employee_Vault/Pending_Approval/

# 2. Review one
cat AI_Employee_Vault/Pending_Approval/APPROVAL_send_email_*.md

# 3. Approve it (move to /Approved/)
mv AI_Employee_Vault/Pending_Approval/APPROVAL_send_email_* \
   AI_Employee_Vault/Approved/

# 4. Process approvals
cd .claude/skills/approval-workflow
bash process_approvals.sh
```

**Expected output**:
```
Processing approved actions from: /c/Users/HP/Desktop/H/FTEs/Silver Tier/AI_Employee_Vault

📋 Executing approval: APPROVAL_send_email_2026-03-13_0.md
   Action type: send_email

✗ Email MCP server not running on port 3001
✗ Error sending email: Email MCP server not available

📝 Result:
   Success: False
   Message: Email MCP server not available

✓ Moved to /Done/APPROVAL_send_email_2026-03-13_0.md
```

**Note**: Email not sent because MCP server isn't running, but the approval workflow processed correctly ✅

### Test 2: Real Email Approval (With MCP)

#### Part A: Start Email MCP Server

```bash
# In a separate terminal:
cd .claude/skills/email-sending
bash scripts/start-server.sh

# Verify it's running:
python3 scripts/verify.py
```

#### Part B: Create Real Approval

```bash
# Go back to approval-workflow
cd .claude/skills/approval-workflow

# Create approval request for real email
python3 -c "
from create_approval import create_email_approval
import os

vault = os.getenv('VAULT_PATH', './AI_Employee_Vault')
f = create_email_approval(
    vault_path=vault,
    recipient='your_email@gmail.com',
    subject='Test from Approval Workflow',
    body='This is a real test email from the approval workflow system.'
)
print(f'✓ Created: {f}')
"
```

#### Part C: Approve and Execute

```bash
# List pending approvals
ls -la AI_Employee_Vault/Pending_Approval/

# Approve (move to /Approved/)
mv AI_Employee_Vault/Pending_Approval/APPROVAL_send_email_* \
   AI_Employee_Vault/Approved/

# Execute
bash process_approvals.sh
```

**Expected output**:
```
📋 Executing approval: APPROVAL_send_email_2026-03-13_0.md
   Action type: send_email
✓ Email sent to your_email@gmail.com
✓ Moved to /Done/
```

**Then check your email**: You should receive the test email! ✅

---

## 🔄 Integration with Claude Code

### How Claude Uses Approvals

In Claude's reasoning, when it detects something sensitive:

```python
# In Claude Code prompt/thinking:
"This email should be reviewed before sending. Let me create an approval request."

from create_approval import create_email_approval
import os

approval_file = create_email_approval(
    vault_path=os.getenv('VAULT_PATH'),
    recipient='john@example.com',
    subject='Project Status Update',
    body='Here is the latest project status...'
)
```

Claude creates approval → User approves → Next run executes.

### Full Workflow Example

**Scenario**: Claude detects important email and wants to respond

```
1. Watcher detects: "Partnership opportunity - can we discuss?"
   → EMAIL_partnership_inquiry.md in /Needs_Action/

2. Claude reads email
   → "This is a business opportunity, needs human review"
   → Creates APPROVAL_respond_to_partnership.md

3. Approval file shows:
   To: john@example.com
   Subject: RE: Partnership opportunity
   Body: [Claude's drafted response]

4. User reviews:
   - "Looks good, let's send it"
   - Moves to /Approved/

5. Next Claude run or manual trigger:
   → Detects approved file
   → Sends email via Email MCP Server
   → Logs success

6. Result:
   → Email sent ✅
   → Logged in /Done/ ✅
```

---

## 📝 Configuration: Update Company Handbook

Add to `AI_Employee_Vault/Company_Handbook.md`:

```markdown
## Approval Policy

### Actions Requiring Approval
- [ ] Send email to external recipient
- [ ] Email with sensitive/confidential data
- [ ] Bulk emails (>5 recipients)
- [ ] Post to LinkedIn
- [ ] Any custom action (default: approve)

### Auto-Approved (No approval needed)
- [ ] Internal team emails
- [ ] Routine status updates
- [ ] To known/trusted contacts (TBD: build whitelist)
- [ ] Automated alerts/notifications

### How to Approve
1. Check `/Pending_Approval/` folder
2. Review the approval file (human-readable markdown)
3. Read: recipient, content, risks, checklist
4. Decide: approve or reject
5. **To approve**: Move file to `/Approved/`
6. **To reject**: Delete the file
7. Next Claude run will execute approved actions

### Response Times
- Standard: within 1 hour
- Urgent (marked in file): within 15 minutes
- Critical: within 5 minutes

### Audit Trail
All approvals logged in `/Done/` with:
- Timestamp
- What was approved
- Execution result
- Any errors or issues
```

---

## 🧬 How It Works (Technical Details)

### Approval Workflow Class

```python
workflow = ApprovalWorkflow('./AI_Employee_Vault')

# Create approval
workflow.create_approval_request(
    action_type='send_email',
    title='Approval Required: Email to Client',
    metadata={'recipient': 'john@example.com', 'subject': 'Update'},
    content='Email body...'
)

# Get approved actions
approved = workflow.get_approved_actions()

# Execute each
for approval in approved:
    result = workflow.execute_approved_action(approval)
    print(f"Executed: {result['message']}")
```

### File States

**Pending Approval** (`/Pending_Approval/`):
```
APPROVAL_send_email_2026-03-13_0.md
├── Created by: Claude
├── Status: Waiting for user
└── Action: None yet
```

**Approved** (`/Approved/`):
```
APPROVAL_send_email_2026-03-13_0.md
├── Moved by: User
├── Status: Ready to execute
└── Action: Execute on next run
```

**Done** (`/Done/`):
```
APPROVAL_send_email_2026-03-13_0.md
├── Moved by: Approval workflow
├── Status: Executed
└── Result: Success/Failure logged
```

---

## ✅ Verification Checklist

After implementing Phase 6, verify:

- [ ] Approval folders exist:
  - `/Pending_Approval/` ✓
  - `/Approved/` ✓
  - `/Done/` ✓

- [ ] Scripts work:
  - `bash process_approvals.sh` runs without error
  - `python3 create_approval.py --test` creates files
  - Files appear in `/Pending_Approval/`

- [ ] Manual workflow works:
  - Move file to `/Approved/`
  - Run `bash process_approvals.sh`
  - File moves to `/Done/`

- [ ] Email integration works:
  - Email MCP server running
  - `bash process_approvals.sh` sends email
  - Email received ✅

- [ ] Claude integration ready:
  - `bash scripts/run-claude.sh` includes approval processing
  - Can create approvals from Claude Code
  - Can execute approvals automatically

- [ ] Documentation updated:
  - `Company_Handbook.md` has approval policies
  - Team knows how to approve/reject
  - Audit trail accessible

---

## 🎯 Next Steps (Phase 7)

Once Phase 6 is verified:

### Phase 7: Scheduling
- Automate approval detection
- Run every 30 minutes
- No manual triggers needed
- 24/7 operation

**Preview**:
```bash
# Phase 7 will set up:
Task Scheduler (Windows) or cron (Linux)
  ↓
Runs: bash scripts/run-claude.sh
  ↓
Every 30 minutes
  ↓
Automatically:
  - Processes approved actions
  - Runs Claude reasoning
  - Executes new approvals
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Folder not found" | `mkdir -p AI_Employee_Vault/Pending_Approval` |
| "No approvals created" | Run: `python3 create_approval.py --test` |
| "File not moving" | Check permissions: `ls -la AI_Employee_Vault/Approved/` |
| "Process fails" | Check: `python3 approval_workflow.py` directly |
| "Email not sent" | Ensure Email MCP server running: `bash .claude/skills/email-sending/scripts/start-server.sh` |

---

## 📊 Success Criteria

Phase 6 is **COMPLETE** when:

- ✅ Approval workflow skill created
- ✅ `approval_workflow.py` runs without errors
- ✅ Approvals can be created manually
- ✅ Approvals can be executed manually
- ✅ Email sending works with approvals
- ✅ Claude can integrate approvals
- ✅ `scripts/run-claude.sh` includes approval processing
- ✅ Company Handbook updated with policies
- ✅ Team understands approval workflow
- ✅ Audit trail in `/Done/`

---

## 🚀 Ready?

**Option A: Quick Test** (10 min)
```bash
cd .claude/skills/approval-workflow
python3 create_approval.py --test
mv AI_Employee_Vault/Pending_Approval/* AI_Employee_Vault/Approved/
bash process_approvals.sh
```

**Option B: Full Integration Test** (20 min)
```bash
# Start Email MCP server
bash .claude/skills/email-sending/scripts/start-server.sh

# Create and approve real email
cd .claude/skills/approval-workflow
python3 create_approval.py --test
mv AI_Employee_Vault/Pending_Approval/APPROVAL_send_email* \
   AI_Employee_Vault/Approved/
bash process_approvals.sh

# Check email received
```

**Option C: Full Pipeline Test** (30 min)
```bash
# 1. Start all services
bash .claude/skills/email-sending/scripts/start-server.sh

# 2. Run Claude with approval processing
bash scripts/run-claude.sh

# 3. Create test items in /Needs_Action/

# 4. Approve them

# 5. Verify execution
```

---

## 📞 Questions?

Check:
1. `.claude/skills/approval-workflow/SKILL.md` - Usage guide
2. `.claude/skills/approval-workflow/README.md` - Full documentation
3. `PHASE_6_CHECKLIST.md` - Original requirements
4. Logs: `tail -f ~/.logs/*.log`

---

**Phase 6**: ✅ COMPLETE
**Next Phase**: Phase 7 (Scheduling)
**Estimated Time**: 2-3 hours

**Status**: Ready to move forward! 🚀
