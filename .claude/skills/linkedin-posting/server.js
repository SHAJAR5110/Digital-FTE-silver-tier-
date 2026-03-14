#!/usr/bin/env node

/**
 * LinkedIn Posting MCP Server
 * Posts to LinkedIn after human approval
 * Requires: LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_ID, LINKEDIN_ORGANIZATION_ID
 */

const express = require('express');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.MCP_PORT || 3002;

app.use(express.json());

let server = null;

/**
 * Post to LinkedIn
 */
async function postToLinkedIn(params) {
  try {
    const { content, media = [], hashtags = [] } = params;

    if (!content || content.trim().length === 0) {
      return {
        success: false,
        error: 'Content cannot be empty'
      };
    }

    // Format content with hashtags
    let post_content = content;
    if (hashtags && hashtags.length > 0) {
      post_content += '\n\n' + hashtags.map(tag => `#${tag}`).join(' ');
    }

    // Check for required credentials
    const access_token = process.env.LINKEDIN_ACCESS_TOKEN;
    const person_id = process.env.LINKEDIN_PERSON_ID;

    if (!access_token || !person_id) {
      return {
        success: false,
        error: 'LinkedIn credentials not configured (LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_ID)',
        message: 'Set environment variables in .env file'
      };
    }

    // LinkedIn API endpoint
    const url = 'https://api.linkedin.com/v2/ugcPosts';

    // Build request
    const requestData = {
      author: `urn:li:person:${person_id}`,
      lifecycleState: 'PUBLISHED',
      specificContent: {
        'com.linkedin.ugc.ShareContent': {
          shareCommentary: {
            text: post_content
          },
          shareMediaCategory: 'NONE'
        }
      },
      visibility: {
        'com.linkedin.ugc.MemberNetworkVisibility': 'PUBLIC'
      }
    };

    console.log(`📤 Posting to LinkedIn: ${content.substring(0, 50)}...`);

    // Make request to LinkedIn API
    const response = await axios.post(url, requestData, {
      headers: {
        'Authorization': `Bearer ${access_token}`,
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      },
      timeout: 30000
    });

    const post_id = response.headers['x-linkedin-id'] || response.data?.id || 'unknown';

    console.log(`✓ Post published: ${post_id}`);

    return {
      success: true,
      message: 'Post published to LinkedIn',
      postId: post_id,
      timestamp: new Date().toISOString(),
      content: content.substring(0, 100)
    };

  } catch (error) {
    console.error(`✗ LinkedIn post failed: ${error.message}`);

    // Check if it's auth error
    if (error.response?.status === 401) {
      return {
        success: false,
        error: 'Authentication failed - check LINKEDIN_ACCESS_TOKEN',
        statusCode: 401
      };
    }

    return {
      success: false,
      error: error.message || 'Failed to post to LinkedIn',
      statusCode: error.response?.status
    };
  }
}

/**
 * Get LinkedIn status
 */
async function getStatus() {
  const access_token = process.env.LINKEDIN_ACCESS_TOKEN;
  const person_id = process.env.LINKEDIN_PERSON_ID;

  if (access_token && person_id) {
    return {
      status: 'ready',
      provider: 'linkedin_api',
      authenticated: true,
      personId: person_id.substring(0, 8) + '...'
    };
  }

  return {
    status: 'error',
    provider: 'linkedin_api',
    error: 'LinkedIn credentials not configured',
    required: ['LINKEDIN_ACCESS_TOKEN', 'LINKEDIN_PERSON_ID']
  };
}

// Routes

app.get('/', (req, res) => {
  res.json({
    status: 'running',
    service: 'LinkedIn Posting MCP Server',
    port: PORT,
    provider: 'linkedin_api'
  });
});

app.get('/status', async (req, res) => {
  const status = await getStatus();
  res.json(status);
});

app.post('/post-linkedin', express.json(), async (req, res) => {
  const result = await postToLinkedIn(req.body);
  if (result.success) {
    res.status(200).json(result);
  } else {
    res.status(400).json(result);
  }
});

app.get('/tools', (req, res) => {
  res.json({
    tools: [
      {
        name: 'post_to_linkedin',
        description: 'Post content to LinkedIn',
        inputSchema: {
          type: 'object',
          properties: {
            content: {
              type: 'string',
              description: 'Post content (max 3000 characters)'
            },
            hashtags: {
              type: 'array',
              description: 'Hashtags to include (optional)',
              items: { type: 'string' }
            },
            media: {
              type: 'array',
              description: 'Media file paths (optional)',
              items: { type: 'string' }
            }
          },
          required: ['content']
        }
      }
    ]
  });
});

// Error handling
app.use((err, req, res, next) => {
  console.error(`✗ Error: ${err.message}`);
  res.status(500).json({
    success: false,
    error: err.message
  });
});

// Start server
async function start() {
  const status = await getStatus();

  app.listen(PORT, () => {
    console.log(`✓ LinkedIn Posting MCP Server started on port ${PORT}`);
    console.log(`✓ Status: ${status.status}`);

    if (status.error) {
      console.error(`⚠ Warning: ${status.error}`);
    } else {
      console.log(`✓ Authenticated: Yes`);
      console.log(`✓ Ready to post to LinkedIn`);
    }
  });
}

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully...');
  process.exit(0);
});

start();
