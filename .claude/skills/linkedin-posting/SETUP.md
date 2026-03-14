# LinkedIn Posting MCP - Phase 8 Setup

**Status**: Phase 8 Implementation
**Purpose**: Post to LinkedIn after human approval
**Safety**: All posts require approval in /Approved/ folder

---

## How It Works

```
Claude detects business opportunity
    ↓
Creates APPROVAL_linkedin_post_*.md in /Pending_Approval/
    ↓
Shows post content for review
    ↓
User approves: Move to /Approved/
    ↓
Next automated run (Phase 7)
    ↓
Executes: Calls LinkedIn MCP server
    ↓
Posts to LinkedIn
    ↓
Logged in /Done/
```

---

## Setup Instructions

### Step 1: Get LinkedIn API Credentials

1. Go to: https://www.linkedin.com/developers/apps
2. Create new app
3. Get: **Access Token**
4. Get: **Person ID** (your LinkedIn profile ID)

**To find your Person ID**:
```bash
# Visit your LinkedIn profile, URL like:
https://www.linkedin.com/in/yourprofile/

# API Person ID is different - get from LinkedIn developers console
```

### Step 2: Configure .env

```bash
cd .claude/skills/linkedin-posting

# Create .env file with:
LINKEDIN_ACCESS_TOKEN=your_access_token_here
LINKEDIN_PERSON_ID=your_person_id_here
MCP_PORT=3002
```

### Step 3: Install Dependencies

```bash
npm install
```

### Step 4: Start Server

```bash
bash start-server.sh
# Or: node server.js
```

### Step 5: Verify

```bash
# Check if running
curl http://localhost:3002/status

# Should show:
# { "status": "ready", "authenticated": true }
```

---

## Integration with Approval Workflow

When human approves LinkedIn post:

1. **File in /Approved/**:
```
APPROVAL_linkedin_post_2026-03-13_0.md
├── action_type: linkedin_post
├── content: "Excited to announce..."
└── hashtags: [innovation, business]
```

2. **Claude detects approval** (Phase 7 scheduler)

3. **Calls LinkedIn MCP** on port 3002

4. **Result logged** in /Done/

---

## Example Flow

### User Creates Test Post

```bash
# Manually create approval for testing
cat > AI_Employee_Vault/Pending_Approval/APPROVAL_linkedin_test.md << 'EOF'
---
type: action_approval
action_type: linkedin_post
status: pending_approval
---

# LinkedIn Post Approval

## Content
Excited to launch our new AI-powered features! This will transform how businesses operate. #innovation #technology
EOF
```

### User Approves

```bash
mv AI_Employee_Vault/Pending_Approval/APPROVAL_linkedin_test.md \
   AI_Employee_Vault/Approved/
```

### Automated Execution (Phase 7)

Next 30-minute cycle runs:
```bash
bash scripts/run-claude.sh
```

### Server Executes

LinkedIn MCP server:
1. Reads approval file
2. Extracts content and hashtags
3. Calls LinkedIn API
4. Posts to timeline
5. Logs success

---

## Testing

### Manual Test

```bash
# 1. Start LinkedIn server
npm start

# 2. Test endpoint
curl -X POST http://localhost:3002/post-linkedin \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Test post from Digital FTE",
    "hashtags": ["test", "automation"]
  }'
```

### Full Workflow Test

```bash
# 1. Start all services
bash .claude/skills/email-sending/scripts/start-server.sh
bash .claude/skills/linkedin-posting/start-server.sh

# 2. Trigger Claude
bash scripts/run-claude.sh

# 3. Create test approval
cat > AI_Employee_Vault/Pending_Approval/test_post.md << 'EOF'
---
type: action_approval
action_type: linkedin_post
---

# LinkedIn Post

Test post content here
EOF

# 4. Approve
mv AI_Employee_Vault/Pending_Approval/test_post.md \
   AI_Employee_Vault/Approved/

# 5. Execute
bash .claude/skills/approval-workflow/process_approvals.sh

# 6. Check logs
tail -f ~/.logs/*
```

---

## Environment Variables

```env
# Required for LinkedIn posting
LINKEDIN_ACCESS_TOKEN=your_token
LINKEDIN_PERSON_ID=your_person_id

# Server configuration
MCP_PORT=3002

# Logging
LOG_FILE=~/.logs/linkedin_mcp.log
LOG_LEVEL=info
```

---

## Start/Stop Scripts

### start-server.sh
```bash
#!/bin/bash
cd $(dirname $0)
npm install 2>/dev/null
node server.js &
echo $! > ~/.logs/linkedin_mcp.pid
```

### stop-server.sh
```bash
#!/bin/bash
kill $(cat ~/.logs/linkedin_mcp.pid)
rm ~/.logs/linkedin_mcp.pid
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Cannot find module" | Run: `npm install` |
| "401 Unauthorized" | Check LINKEDIN_ACCESS_TOKEN in .env |
| "Port 3002 already in use" | Kill existing: `pkill -f "node.*server.js"` |
| "Post not appearing" | Check LinkedIn profile, post might be pending moderation |
| "LINKEDIN_PERSON_ID not found" | Get from LinkedIn Developers console |

---

## Complete LinkedIn Workflow

```
Message received
    ↓ (Gmail/WhatsApp/LinkedIn Watcher)
Opportunity detected
    ↓
Claude analyzes
    ↓
Claude creates approval: "Should I post this?"
    ↓ /Pending_Approval/
User reviews post content
    ↓
User approves: Move to /Approved/
    ↓
Phase 7 scheduler triggers (every 30 min)
    ↓
Approval executor detects approval
    ↓
Calls LinkedIn MCP server
    ↓
Post published to LinkedIn
    ↓
Logged in /Done/
    ↓
✅ Complete with human approval
```

---

**Phase 8**: READY TO USE
**Next**: Phase 9 (Testing & Documentation)
