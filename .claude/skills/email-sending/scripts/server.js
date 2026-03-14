#!/usr/bin/env node

/**
 * Email MCP Server
 * Provides email sending capability to Claude Code via Model Context Protocol
 * Supports SMTP (Gmail, Outlook, etc.) and Gmail API
 */

const { Server } = require('@anthropic-ai/sdk/lib/resources/messages/mcp.js');
const nodemailer = require('nodemailer');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const PORT = process.env.MCP_PORT || 3001;
const PROVIDER = process.env.EMAIL_PROVIDER || 'smtp';

// Initialize transporter based on provider
let transporter = null;
let initError = null;

async function initializeTransporter() {
  try {
    if (PROVIDER === 'smtp') {
      transporter = nodemailer.createTransport({
        host: process.env.SMTP_HOST || 'smtp.gmail.com',
        port: parseInt(process.env.SMTP_PORT || '587'),
        secure: process.env.SMTP_USE_TLS === 'false' ? false : true,
        auth: {
          user: process.env.SMTP_EMAIL,
          pass: process.env.SMTP_PASSWORD,
        },
      });

      // Verify connection
      await transporter.verify();
      console.log(`✓ SMTP transporter initialized: ${process.env.SMTP_EMAIL}`);
    } else if (PROVIDER === 'gmail') {
      // TODO: Implement Gmail API support
      throw new Error('Gmail API provider not yet implemented');
    } else {
      throw new Error(`Unknown email provider: ${PROVIDER}`);
    }
  } catch (error) {
    console.error(`✗ Failed to initialize transporter: ${error.message}`);
    initError = error;
  }
}

/**
 * Send an email
 */
async function sendEmail(params) {
  if (initError) {
    return {
      success: false,
      error: `Email service not initialized: ${initError.message}`,
    };
  }

  // Validate required parameters
  if (!params.to) {
    return {
      success: false,
      error: 'Missing required parameter: to',
    };
  }

  if (!params.subject) {
    return {
      success: false,
      error: 'Missing required parameter: subject',
    };
  }

  if (!params.body) {
    return {
      success: false,
      error: 'Missing required parameter: body',
    };
  }

  // Validate email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const recipients = params.to.split(',').map(e => e.trim());
  for (const recipient of recipients) {
    if (!emailRegex.test(recipient)) {
      return {
        success: false,
        error: `Invalid email address: ${recipient}`,
      };
    }
  }

  try {
    // Prepare email
    const mailOptions = {
      from: `${process.env.SMTP_FROM_NAME || 'Digital FTE'} <${process.env.SMTP_EMAIL}>`,
      to: params.to,
      subject: params.subject,
      text: params.body,
      html: params.body.replace(/\n/g, '<br>'),
    };

    // Add optional fields
    if (params.cc) {
      mailOptions.cc = params.cc;
    }
    if (params.bcc) {
      mailOptions.bcc = params.bcc;
    }

    // Handle attachments if provided
    if (params.attachments && Array.isArray(params.attachments)) {
      mailOptions.attachments = [];
      for (const filePath of params.attachments) {
        if (fs.existsSync(filePath)) {
          mailOptions.attachments.push({
            filename: path.basename(filePath),
            path: filePath,
          });
        } else {
          console.warn(`Attachment not found: ${filePath}`);
        }
      }
    }

    // Send email
    const info = await transporter.sendMail(mailOptions);

    console.log(`✓ Email sent: ${params.to} - "${params.subject}"`);
    console.log(`  Message ID: ${info.messageId}`);

    return {
      success: true,
      message: 'Email sent successfully',
      messageId: info.messageId,
      recipients: recipients,
      timestamp: new Date().toISOString(),
    };
  } catch (error) {
    console.error(`✗ Email send failed: ${error.message}`);
    return {
      success: false,
      error: `Failed to send email: ${error.message}`,
    };
  }
}

/**
 * Get email sending status
 */
async function getStatus() {
  if (initError) {
    return {
      status: 'error',
      provider: PROVIDER,
      error: initError.message,
    };
  }

  try {
    if (PROVIDER === 'smtp') {
      return {
        status: 'ready',
        provider: 'smtp',
        host: process.env.SMTP_HOST,
        from: process.env.SMTP_EMAIL,
      };
    }
  } catch (error) {
    return {
      status: 'error',
      provider: PROVIDER,
      error: error.message,
    };
  }
}

/**
 * Main Server Setup (Express-based for simplicity)
 */
const express = require('express');
const app = express();

app.use(express.json());

// Health check endpoint
app.get('/', (req, res) => {
  res.json({
    status: 'running',
    service: 'Email MCP Server',
    provider: PROVIDER,
    port: PORT,
  });
});

// Status endpoint
app.get('/status', async (req, res) => {
  const status = await getStatus();
  res.json(status);
});

// Send email endpoint (MCP-compatible)
app.post('/send-email', express.json(), async (req, res) => {
  const result = await sendEmail(req.body);
  if (result.success) {
    res.status(200).json(result);
  } else {
    res.status(400).json(result);
  }
});

// MCP Tool Definition endpoint
app.get('/tools', (req, res) => {
  res.json({
    tools: [
      {
        name: 'send_email',
        description: 'Send an email using SMTP or Gmail API',
        inputSchema: {
          type: 'object',
          properties: {
            to: {
              type: 'string',
              description: 'Email recipient (or comma-separated list)',
            },
            subject: {
              type: 'string',
              description: 'Email subject',
            },
            body: {
              type: 'string',
              description: 'Email body (plain text or markdown)',
            },
            cc: {
              type: 'string',
              description: 'CC recipients (optional, comma-separated)',
            },
            bcc: {
              type: 'string',
              description: 'BCC recipients (optional, comma-separated)',
            },
            attachments: {
              type: 'array',
              description: 'File paths to attach (optional)',
              items: {
                type: 'string',
              },
            },
          },
          required: ['to', 'subject', 'body'],
        },
      },
    ],
  });
});

// Error handling
app.use((err, req, res, next) => {
  console.error(`✗ Error: ${err.message}`);
  res.status(500).json({
    success: false,
    error: err.message,
  });
});

// Start server
async function start() {
  await initializeTransporter();

  app.listen(PORT, () => {
    console.log(`✓ Email MCP Server started on port ${PORT}`);
    console.log(`✓ Provider: ${PROVIDER}`);
    console.log(`✓ Ready to receive requests from Claude Code`);

    if (initError) {
      console.error(`⚠ Warning: Email service not ready: ${initError.message}`);
    }
  });
}

start();

// Handle graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully...');
  process.exit(0);
});
