# Silver Tier - Phase 8: LinkedIn Auto-Posting Checklist

**Phase**: 8 of 9 (Social Media)
**Status**: READY TO BUILD
**Time**: ~2-3 hours

## Overview

Phase 8 adds LinkedIn posting capability. Claude can draft posts, get approval, and post directly to LinkedIn for business lead generation.

## Architecture

```
Claude detects business opportunity
    ↓
Creates post draft in /Plans/LINKEDIN_POST_*.md
    ↓
Creates approval in /Pending_Approval/
    ↓
User approves (moves to /Approved/)
    ↓
Claude uses linkedin-posting MCP server
    ↓
Post published to LinkedIn
    ↓
Logged to /Done/
```

## What to Build

### 1. LinkedIn Posting MCP Server

Create in `.claude/skills/linkedin-posting/`:

```javascript
// scripts/server.js

// Tool: post_to_linkedin
// Parameters:
//   - content: Post text (max 3000 chars)
//   - media: Optional image/video paths
//   - link: Optional link to include
//   - hashtags: Optional hashtags

// Returns:
//   - success: true/false
//   - postId: LinkedIn post ID
//   - url: Link to posted content
```

### 2. LinkedIn Posting Integration

Use LinkedIn API or web automation:

**Option A: LinkedIn API** (Official)
```env
LINKEDIN_ORGANIZATION_ID=12345
LINKEDIN_ACCESS_TOKEN=your_token
```

**Option B: Web Automation** (Playwright)
```javascript
// Use existing LinkedIn session from LinkedIn Watcher
// Automate post creation via web.linkedin.com
```

### 3. Post Templates

Create in Company_Handbook:

```markdown
## LinkedIn Posting Guidelines

### Post Types
- **Industry Updates**: Share news, trends
- **Company Milestones**: New projects, achievements
- **Thought Leadership**: Industry insights
- **Business Development**: Services, offers

### Auto-Post Triggers
- Project completion
- Major client announcement
- Industry opportunity
- Knowledge sharing

### Do Not Post
- Confidential information
- Client data without permission
- Political or controversial content
- Competitors' information
```

## Configuration

### .env Setup

```env
# LinkedIn Posting
LINKEDIN_POSTING_PROVIDER=api  # or: web (Playwright)
LINKEDIN_ORGANIZATION_ID=12345
LINKEDIN_ACCESS_TOKEN=your_access_token

# Post Settings
MAX_POST_LENGTH=3000
REQUIRE_APPROVAL=true
AUTO_HASHTAG_GENERATION=true
```

### Post Draft Format

Claude creates drafts in `/Plans/LINKEDIN_POST_*.md`:

```markdown
---
type: linkedin_post
target_audience: connections
hashtags: [industry, business, innovation]
media: ["/vault/images/screenshot.png"]
linked_url: https://example.com/blog
requires_approval: true
status: draft
---

# LinkedIn Post Draft

## Content
Your innovative company just launched a game-changing product...

## Media
- screenshot.png: Demo screenshot

## Linked Content
Blog post about the product launch

## Engagement Strategy
- Post timing: Tuesday 10am
- Expected engagement: 20-30 reactions
- Follow-up: Link to company page
```

## Verification Steps

- [ ] LinkedIn Posting MCP server created
- [ ] Node.js dependencies installed
- [ ] LinkedIn credentials configured
- [ ] Test post created manually
- [ ] Claude can draft posts
- [ ] Approval workflow works
- [ ] Post successfully published to LinkedIn
- [ ] Post appears on timeline
- [ ] Logging shows post details
- [ ] Multiple posts can be published

## Testing

1. **Manually test LinkedIn API**:
   ```bash
   curl -X POST http://localhost:3002/post-linkedin \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"content": "Test post from Digital FTE"}'
   ```

2. **Have Claude draft a post**:
   ```
   Claude: "Create a LinkedIn post about our latest feature"
   ```

3. **Approve the draft**:
   ```bash
   mv /Plans/LINKEDIN_POST_*.md /Approved/
   ```

4. **Verify post published**:
   - Check LinkedIn timeline
   - Verify post ID in `/Done/`

## Integration with Watcher

LinkedIn Watcher (Phase 4) monitors for opportunities. Claude can:
- Detect job posting opportunity
- Create post offering services
- Get approval
- Post to LinkedIn
- Track engagement

## Rate Limiting

LinkedIn limits:
- 1 post per 12 hours per user
- 100 posts per month
- Avoid spam/duplicate content

**Implementation**:
```python
# Check /Done/ for recent posts
# Enforce cooldown: max 1 post per 12 hours
# Track monthly count
```

## Next: Phase 9

Phase 9 completes Silver Tier with comprehensive testing and documentation.

---

**Status**: Ready to implement
**Estimated**: 2-3 hours

**Note**: LinkedIn API access requires approval from LinkedIn. Alternatively, use Playwright web automation with existing LinkedIn session.
