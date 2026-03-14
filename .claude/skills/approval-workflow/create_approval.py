#!/usr/bin/env python3

"""
Helper script for Claude to create approval requests
"""

import os
import sys
from pathlib import Path
from approval_workflow import ApprovalWorkflow

def create_email_approval(
    vault_path: str,
    recipient: str,
    subject: str,
    body: str,
    cc: str = None,
    bcc: str = None
) -> str:
    """
    Create an email approval request for Claude to use.

    Args:
        vault_path: Path to vault
        recipient: Email recipient
        subject: Email subject
        body: Email body
        cc: Optional CC recipients
        bcc: Optional BCC recipients

    Returns:
        Path to created approval file
    """
    workflow = ApprovalWorkflow(vault_path)

    metadata = {
        'recipient': recipient,
        'subject': subject,
    }
    if cc:
        metadata['cc'] = cc
    if bcc:
        metadata['bcc'] = bcc

    content = f"""## Action Details
**To**: {recipient}
**Subject**: {subject}
{f'**CC**: {cc}' if cc else ''}
{f'**BCC**: {bcc}' if bcc else ''}

## Email Content
{body}

## Review Checklist
- [ ] Is this the right recipient?
- [ ] Is the content accurate?
- [ ] Should this be sent?
- [ ] Any attachments needed?

## Approval Instructions
**To approve**: Move this file to `/Approved/` folder
**To reject**: Delete this file

## Status
**Type**: Email approval
**Created**: {str(Path(vault_path).parent / 'Pending_Approval')}
"""

    filepath = workflow.create_approval_request(
        action_type='send_email',
        title=f'Approval Required: Send Email to {recipient}',
        metadata=metadata,
        content=content
    )

    return str(filepath)


def create_linkedin_approval(
    vault_path: str,
    content: str,
    hashtags: list = None,
    media: list = None
) -> str:
    """
    Create a LinkedIn post approval request for Claude to use.

    Args:
        vault_path: Path to vault
        content: Post content
        hashtags: Optional hashtags
        media: Optional media files

    Returns:
        Path to created approval file
    """
    workflow = ApprovalWorkflow(vault_path)

    metadata = {
        'target_audience': 'connections',
    }
    if hashtags:
        metadata['hashtags'] = hashtags
    if media:
        metadata['media'] = media

    hashtag_str = '\n'.join([f'- {tag}' for tag in (hashtags or [])])

    content_section = f"""## Post Content
{content}

## Hashtags
{hashtag_str if hashtag_str else 'None'}

## Media
{content if media else 'None'}

## Review Checklist
- [ ] Is the content appropriate?
- [ ] Are hashtags relevant?
- [ ] Is this the right audience?
- [ ] Ready to post?

## Approval Instructions
**To approve**: Move this file to `/Approved/` folder
**To reject**: Delete this file

## Status
**Type**: LinkedIn post approval
**Target Audience**: Connections
"""

    filepath = workflow.create_approval_request(
        action_type='linkedin_post',
        title=f'Approval Required: Post to LinkedIn',
        metadata=metadata,
        content=content_section
    )

    return str(filepath)


def main():
    """Test approval creation"""
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')

    # Test email approval
    print("Creating test email approval...")
    email_file = create_email_approval(
        vault_path=vault_path,
        recipient='john@example.com',
        subject='Project Update',
        body='Here is the latest project status...'
    )
    print(f"✓ Created: {email_file}")

    # Test LinkedIn approval
    print("\nCreating test LinkedIn approval...")
    linkedin_file = create_linkedin_approval(
        vault_path=vault_path,
        content='Excited to announce our new feature launch! 🚀',
        hashtags=['innovation', 'business'],
        media=['screenshot.png']
    )
    print(f"✓ Created: {linkedin_file}")

    print("\nTest complete!")
    print(f"Check {vault_path}/Pending_Approval/ for files")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            main()
    else:
        main()
