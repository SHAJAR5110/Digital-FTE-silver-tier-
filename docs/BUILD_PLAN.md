# Silver Tier - Build Plan

**Status**: Ready to Build
**Prerequisites**: Bronze Tier Complete ✅
**Estimated Time**: 20-30 hours
**Build Path**: Sequential phases following CLAUDE.md

---

## Silver Tier Overview

Silver Tier upgrades Bronze with:
- ✅ Multiple Watchers (Gmail, WhatsApp, LinkedIn)
- ✅ First MCP Server (Email Sending)
- ✅ Approval Workflow (Human-in-the-loop)
- ✅ Scheduling (Automated Claude triggers)
- ✅ LinkedIn Auto-posting

**Result**: Functional AI Assistant with multi-domain input processing

---

## Build Phases (From CLAUDE.md)

### Phase 1: Foundation Setup (1-2 hours)
- [ ] Copy Bronze vault structure to Silver
- [ ] Expand Company_Handbook with Silver rules
- [ ] Create /Pending_Approval and /Approved folders
- [ ] Expand /Accounting folder structure

### Phase 2: Gmail Watcher (3-4 hours)
- [ ] Set up Google OAuth2 credentials
- [ ] Implement GmailWatcher class
- [ ] Monitor important/unread emails
- [ ] Create action files with metadata
- [ ] Test with sample emails

### Phase 3: WhatsApp Watcher (3-4 hours)
- [ ] Implement WhatsAppWatcher (Playwright-based)
- [ ] Monitor web WhatsApp
- [ ] Detect keywords (urgent, invoice, payment)
- [ ] Create action files
- [ ] Test with sample messages

### Phase 4: LinkedIn Watcher (2-3 hours)
- [ ] Implement LinkedInWatcher
- [ ] Monitor messages and notifications
- [ ] Detect opportunities (collaboration, job, business)
- [ ] Create action files
- [ ] Test with sample data

### Phase 5: Email MCP Server (4-5 hours)
- [ ] Build MCP server for sending emails
- [ ] Support SMTP or Gmail API
- [ ] Implement approval gate
- [ ] Integrate with Claude Code
- [ ] Test email sending workflow

### Phase 6: Approval Workflow (2-3 hours)
- [ ] Create approval file format
- [ ] Implement move-to-approve pattern
- [ ] Document in Company_Handbook
- [ ] Test workflow end-to-end

### Phase 7: Scheduling (2-3 hours)
- [ ] Set up cron job (Linux/macOS) OR Task Scheduler (Windows)
- [ ] Schedule Claude to run every 30 minutes
- [ ] Set up watcher continuous monitoring
- [ ] Test automation

### Phase 8: LinkedIn Auto-posting (2-3 hours)
- [ ] Implement LinkedIn MCP server
- [ ] Support post creation
- [ ] Approval workflow for posts
- [ ] Test posting

### Phase 9: Testing & Documentation (2-3 hours)
- [ ] End-to-end testing
- [ ] Create README.md
- [ ] Document all watchers
- [ ] Create troubleshooting guide

---

## What Needs to Be Created

### Documentation
- [ ] USE.md - Daily operations guide
- [ ] README.md - Comprehensive documentation
- [ ] QUICKSTART.md - Quick start guide
- [ ] TROUBLESHOOTING.md - Common issues & fixes

### Vault Structure
- [ ] Copy from Bronze
- [ ] Add /Pending_Approval
- [ ] Add /Approved
- [ ] Expand Company_Handbook.md

### Watcher Scripts
- [ ] gmail_watcher.py
- [ ] whatsapp_watcher.py
- [ ] linkedin_watcher.py
- [ ] Update base_watcher.py if needed

### MCP Servers
- [ ] email-sending/ skill
- [ ] linkedin-posting/ skill (Phase 8)

### Configuration
- [ ] .env.example (credentials template)
- [ ] requirements.txt (Python deps)
- [ ] test_setup.py (verification)

### Scripts
- [ ] start-watchers.sh (launch all watchers)
- [ ] run-claude.sh (trigger Claude)

---

## Dependencies & Prerequisites

### Python Libraries Needed
```
google-auth-oauthlib>=1.0.0  # Gmail OAuth
google-api-python-client>=2.100.0  # Gmail API
playwright>=1.40.0  # WhatsApp/LinkedIn browser automation
python-dotenv>=1.0.0  # Credentials management
```

### External Accounts Needed
- [ ] Google (Gmail API access)
- [ ] WhatsApp Business Account (or Web access)
- [ ] LinkedIn API credentials
- [ ] SMTP credentials (for email sending)

### System Setup
- [ ] Port availability (for MCP servers)
- [ ] Cron/Task Scheduler access
- [ ] API token storage (.env file)

---

## Timeline Estimate

| Phase | Hours | Cumulative |
|-------|-------|-----------|
| 1: Foundation | 1-2h | 1-2h |
| 2: Gmail Watcher | 3-4h | 4-6h |
| 3: WhatsApp Watcher | 3-4h | 7-10h |
| 4: LinkedIn Watcher | 2-3h | 9-13h |
| 5: Email MCP | 4-5h | 13-18h |
| 6: Approval Workflow | 2-3h | 15-21h |
| 7: Scheduling | 2-3h | 17-24h |
| 8: LinkedIn Posting | 2-3h | 19-27h |
| 9: Testing & Docs | 2-3h | 21-30h |

**Total**: 20-30 hours

---

## Success Criteria

### By End of Phase 1
- [ ] Vault copied from Bronze
- [ ] Company_Handbook expanded
- [ ] New folders created

### By End of Phase 4
- [ ] All 3 watchers working
- [ ] Action files being created
- [ ] Multiple input sources monitored

### By End of Phase 7
- [ ] MCP servers operational
- [ ] Approval workflow tested
- [ ] Scheduling automated
- [ ] Claude running every 30 minutes

### By End of Phase 9
- [ ] All systems integrated
- [ ] Documentation complete
- [ ] Ready for daily use
- [ ] All tests passing

---

## Order of Operations

1. **Start with Phase 1** - Foundation (fastest, enables others)
2. **Do Gmail Watcher first** - Most valuable input source
3. **Then WhatsApp** - Real-time communication
4. **Then LinkedIn** - Business generation
5. **Build Email MCP** - First "hands" for agent
6. **Add Approval Workflow** - Safety gate for actions
7. **Automate with Scheduling** - Hands-free operation
8. **Add LinkedIn Posting** - Business automation
9. **Complete with Testing** - Verify everything works

---

## Key Files to Reference

- **CLAUDE.md** - Full Silver Tier architecture (9 phases detailed)
- **Root CLAUDE.md** - Project-wide patterns and commands
- **Bronze Tier/CLAUDE.md** - Base patterns to extend
- **Bronze Tier/README.md** - Example documentation quality

---

## Getting Started

### Immediate Actions
1. ✅ Read this BUILD_PLAN.md
2. ✅ Read Silver Tier/CLAUDE.md completely
3. ✅ Review Bronze Tier working system
4. ✅ Plan Phase 1 (1-2 hours)

### First Session
- **Duration**: 1-2 hours
- **Focus**: Phase 1 (Foundation Setup)
- **Deliverable**: Vault copied, folders created, Company_Handbook expanded

### Next Steps
- Complete Phase 1, then move to Phase 2 (Gmail Watcher)
- Build sequentially, testing each phase
- Create documentation as you go

---

## Notes

- **Don't Skip Phases** - Each builds on previous
- **Test Constantly** - Each phase has checkpoints
- **Document As You Go** - Makes final docs easier
- **Use Bronze as Reference** - Patterns are similar, just more complex
- **Store Credentials Safely** - Use .env files, never commit to git

---

**Ready to start Silver Tier Build!**
**→ Begin with Phase 1: Foundation Setup**
