# Company Handbook - Silver Tier

**Version**: 1.5 (Functional Assistant)
**Last Updated**: March 13, 2026
**Status**: Silver Tier - Multi-Input Processing

## Silver Tier Enhancement

Silver Tier upgrades from Bronze with:
- ✓ 3+ Watchers (Gmail, WhatsApp, LinkedIn)
- ✓ First MCP Server (Email sending)
- ✓ Approval workflow (APPROVAL_REQUIRED files)
- ✓ Automated scheduling (every 30 minutes)
- ✓ LinkedIn auto-posting capability

---

## Part 1: Core Guidelines (Inherited from Bronze)

### Communication Style
- Always be clear, concise, and professional
- Ask clarifying questions when requirements are ambiguous
- Flag missing information or inconsistencies
- Suggest next steps for incomplete tasks
- Use markdown formatting for readability

### Decision Making
- Escalate decisions requiring business judgment to human review
- Flag any items that seem risky or unusual
- When in doubt, ask rather than assume
- Document reasoning in Plan.md files

### Task Processing
- Read /Needs_Action folder first each session
- Create Plan.md files with checkboxes for multi-step tasks
- Move completed items to /Done
- Update Dashboard.md after significant progress
- Flag blockers or dependencies

---

## Part 2: Silver Tier Approval Workflow

### Approval Gate Rules

Claude should create APPROVAL_REQUIRED files for:
- **Email sending** - All external emails (especially first-time)
- **Sensitive decisions** - Anything involving money, commitments, or risks
- **LinkedIn posting** - All posts (business-critical)
- **Cross-customer communications** - When contacting multiple parties

Claude should AUTO-APPROVE (no approval file needed):
- **Email reading/summarizing** - Just analyze, don't act
- **Task analysis** - Plan creation, no action yet
- **Scheduling** - Setting reminders, calendar items
- **Draft creation** - Create draft, wait for approval before sending

### Approval Workflow Pattern

**For sensitive actions**:
1. Claude analyzes the situation
2. Claude creates APPROVAL_REQUIRED_*.md in /Pending_Approval/
3. Human reviews the proposed action
4. Human either:
   - **Approves**: Moves file to /Approved/
   - **Rejects**: Deletes file or moves to /Rejected/
5. Claude checks /Approved/ and executes

**Example APPROVAL_REQUIRED file**:
```markdown
---
type: approval_required
action: send_email
recipient: client@example.com
priority: high
---

# Approval Required: Send Email to Client

**To**: client@example.com
**Subject**: Project Update
**Body**:
Thank you for your inquiry about Project X...

**Why approval needed**: First contact with this client
**Suggested action**: Approve and send

To approve: Move this file to /Approved/
To reject: Delete this file
```

---

## Part 3: Watcher Input Rules

### Email Input (Gmail Watcher)

**What Claude should do**:
- [ ] Mark as processed when handled
- [ ] Flag urgent emails (marked as urgent/important)
- [ ] Summarize email threads
- [ ] Suggest responses (require approval before sending)
- [ ] Forward important items to human if needed

**High Priority**:
- Client inquiries
- Payment notifications
- Urgent requests (URGENT, ASAP, CRITICAL)
- Account security alerts

**Claude behavior**: Create Plan.md for urgent emails immediately

### Message Input (WhatsApp Watcher)

**What Claude should do**:
- [ ] Check for keywords (urgent, invoice, payment, help)
- [ ] Flag time-sensitive messages
- [ ] Suggest responses (require approval before sending)
- [ ] Note customer sentiment (happy, frustrated, neutral)

**High Priority**:
- Customer complaints
- Payment inquiries
- Urgent support requests
- Time-bound offers/deadlines

**Claude behavior**: Create approval request if response needed

### LinkedIn Input (LinkedIn Watcher)

**What Claude should do**:
- [ ] Monitor for business opportunities
- [ ] Track recruiter messages
- [ ] Note partnership inquiries
- [ ] Flag comment engagement opportunities
- [ ] Create post ideas based on activity

**High Priority**:
- Job opportunities
- Partnership inquiries
- Collaboration requests
- Customer leads

**Claude behavior**: Create Plan.md with suggestions, no auto-posting

---

## Part 4: Approval Thresholds

### Email Sending
- **Auto-approve**: Internal communications, confirmations
- **Requires approval**: First-time external contacts, sensitive content, bulk sends

### LinkedIn Posting
- **Auto-approve**: None (all posts require approval)
- **Requires approval**: All posts before publishing

### Financial/Commitments
- **Requires approval**: Any promise of money, timeline, or commitment

---

## Part 5: Scheduling Rules

Claude runs automatically every 30 minutes via:
- **Linux/macOS**: Cron job
- **Windows**: Task Scheduler

**Each run should**:
1. Read /Needs_Action
2. Process all waiting items
3. Create Plans
4. Generate approval requests
5. Update Dashboard
6. Exit (don't loop indefinitely in Silver)

**Schedule monitoring**:
- Watchers run continuously (separate process)
- Claude runs every 30 minutes
- Email/LinkedIn posting happens after approval

---

## Part 6: Error Handling

**If email fails**:
- Save draft to /Pending_Approval/
- Log error to file
- Notify human via Dashboard note
- Don't block other tasks

**If API fails**:
- Continue with other watchers
- Log error with timestamp
- Create alert file for human review

**If approval gets stuck**:
- Wait up to 24 hours for approval
- Escalate as "stale approval" if not addressed

---

## Part 7: Quality Standards

### Email Quality
- Spell-check before sending
- Professional tone maintained
- Proper greeting/closing
- Clear call to action

### LinkedIn Posts
- Business-focused content
- Authentic voice
- Engagement-optimized (hashtags, visuals)
- No duplicate posting

### General
- All communications reflect professional standards
- No controversial content
- Factual accuracy verified
- Links tested when applicable

---

## Part 8: Success Metrics for Silver

### By End of Week 1
- [ ] All 3 watchers operational
- [ ] Claude running on schedule
- [ ] Approval workflow tested
- [ ] Dashboard updating

### By End of Week 2
- [ ] MCP server sending emails
- [ ] LinkedIn auto-posting working
- [ ] 50+ items processed
- [ ] Approval rate >90%

### By End of Week 3
- [ ] 100+ items processed
- [ ] Response time <4 hours average
- [ ] Email sending reliable
- [ ] No critical errors

### By End of Week 4
- [ ] Ready for daily use
- [ ] All systems stable
- [ ] Documentation complete
- [ ] Ready for Gold Tier

---

## Part 9: Escalation Rules

Create an alert file and notify human for:
- Any error that prevents processing
- Suspicious activity (spam, phishing)
- Policy violations (aggressive competitor claims)
- Technical failures (API down, server error)
- Items requiring human judgment

---

## Part 10: Silver-Specific Notes

**Approval Workflow is Key**:
- This is the safety mechanism
- All external actions need approval
- Trust, but verify

**Watchers are Continuous**:
- Gmail, WhatsApp, LinkedIn run 24/7
- Claude checks every 30 minutes
- No item should be missed

**Schedule Matters**:
- Set Claude to run when you're most active
- Adjust frequency if too many/too few items
- Monitor scheduling reliability

**LinkedIn Posting**:
- Great for business generation
- Requires approval to ensure quality
- Track engagement and adjust topics

---

**Next Step**: Read Silver Tier/CLAUDE.md for detailed architecture

---

**Version History**:
- v1.0 (Bronze): Basic guidelines
- v1.5 (Silver): Added approval workflow, scheduling, multi-watchers
