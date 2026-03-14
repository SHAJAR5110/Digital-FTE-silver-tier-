#!/usr/bin/env python3

"""
Approval Workflow Manager
Handles human-in-loop approval for sensitive actions
"""

import yaml
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class ApprovalWorkflow:
    """Manages approval workflow for actions"""

    def __init__(self, vault_path: str):
        """
        Initialize approval workflow.

        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'

        # Create folders if needed
        self.pending_approval.mkdir(exist_ok=True)
        self.approved.mkdir(exist_ok=True)
        self.done.mkdir(exist_ok=True)

    def get_pending_approvals(self) -> List[Path]:
        """Get all files pending approval"""
        return list(self.pending_approval.glob('*.md'))

    def get_approved_actions(self) -> List[Path]:
        """Get all approved actions ready for execution"""
        return list(self.approved.glob('*.md'))

    def create_approval_request(
        self,
        action_type: str,
        title: str,
        metadata: Dict,
        content: str
    ) -> Path:
        """
        Create an approval request file.

        Args:
            action_type: Type of action (send_email, linkedin_post, etc.)
            title: Title of the approval request
            metadata: YAML metadata to include
            content: Markdown content of the request

        Returns:
            Path to created approval file
        """
        # Build filename
        timestamp = datetime.now().isoformat().split('T')[0]
        filename = f"APPROVAL_{action_type}_{timestamp}_{len(self.get_pending_approvals())}.md"
        filepath = self.pending_approval / filename

        # Build metadata
        meta = {
            'type': 'action_approval',
            'action_type': action_type,
            'status': 'pending_approval',
            'created_at': datetime.now().isoformat(),
            'required_approvals': 1,
            'approvals': [],
        }
        meta.update(metadata)

        # Build YAML header
        yaml_header = '---\n'
        for key, value in meta.items():
            if isinstance(value, list):
                yaml_header += f'{key}: []\n'
            elif isinstance(value, str):
                yaml_header += f'{key}: {value}\n'
            else:
                yaml_header += f'{key}: {value}\n'
        yaml_header += '---\n\n'

        # Write file
        filepath.write_text(yaml_header + f"# {title}\n\n" + content)
        return filepath

    def parse_approval_file(self, filepath: Path) -> Dict:
        """
        Parse an approval file to extract metadata and content.

        Args:
            filepath: Path to approval file

        Returns:
            Dictionary with 'metadata' and 'content' keys
        """
        content = filepath.read_text()

        # Split YAML and content
        parts = content.split('---')
        if len(parts) < 3:
            return {'metadata': {}, 'content': content}

        yaml_str = parts[1].strip()
        markdown_content = '---'.join(parts[2:]).strip()

        # Parse YAML
        try:
            metadata = yaml.safe_load(yaml_str)
        except Exception as e:
            print(f"Error parsing YAML: {e}")
            metadata = {}

        return {
            'metadata': metadata,
            'content': markdown_content,
            'filepath': filepath
        }

    def execute_approved_action(self, approval_file: Path) -> Dict:
        """
        Execute an approved action via MCP.

        Args:
            approval_file: Path to approved action file

        Returns:
            Result dictionary with success status and message
        """
        approval = self.parse_approval_file(approval_file)
        metadata = approval.get('metadata', {})
        action_type = metadata.get('action_type')

        print(f"\n📋 Executing approval: {approval_file.name}")
        print(f"   Action type: {action_type}")

        result = {'success': False, 'error': 'Unknown action type'}

        # Execute based on action type
        if action_type == 'send_email':
            result = self._execute_email(metadata, approval)
        elif action_type == 'linkedin_post':
            result = self._execute_linkedin_post(metadata, approval)
        else:
            result = {'success': False, 'error': f'Unknown action type: {action_type}'}

        # Log result
        self._log_execution(approval_file, action_type, result)

        # Move to Done
        if approval_file.exists():
            done_file = self.done / approval_file.name
            approval_file.rename(done_file)
            print(f"✓ Moved to /Done/{approval_file.name}")

        return result

    def _execute_email(self, metadata: Dict, approval: Dict) -> Dict:
        """Execute email sending via MCP server"""
        try:
            recipient = metadata.get('recipient', '')
            subject = metadata.get('subject', '')

            # Extract body from content
            content_lines = approval.get('content', '').split('\n')
            body = '\n'.join(content_lines[5:]) if len(content_lines) > 5 else ''

            # Call Email MCP server
            mcp_url = 'http://localhost:3001/send-email'
            payload = {
                'to': recipient,
                'subject': subject,
                'body': body.strip()
            }

            response = requests.post(mcp_url, json=payload, timeout=10)

            if response.status_code == 200:
                result = response.json()
                print(f"✓ Email sent to {recipient}")
                return {
                    'success': True,
                    'message': f'Email sent to {recipient}',
                    'messageId': result.get('messageId')
                }
            else:
                error = response.json().get('error', 'Unknown error')
                print(f"✗ Email send failed: {error}")
                return {'success': False, 'error': error}

        except requests.exceptions.ConnectionError:
            print("✗ Email MCP server not running on port 3001")
            return {'success': False, 'error': 'Email MCP server not available'}
        except Exception as e:
            print(f"✗ Error sending email: {e}")
            return {'success': False, 'error': str(e)}

    def _execute_linkedin_post(self, metadata: Dict, approval: Dict) -> Dict:
        """Execute LinkedIn posting via MCP server"""
        try:
            # Extract post content from approval content
            content_lines = approval.get('content', '').split('\n')
            post_content = '\n'.join(content_lines[5:]) if len(content_lines) > 5 else ''

            # LinkedIn MCP server (Phase 8)
            mcp_url = 'http://localhost:3002/post-linkedin'
            payload = {
                'content': post_content.strip(),
                'media': metadata.get('media', []),
                'hashtags': metadata.get('hashtags', [])
            }

            response = requests.post(mcp_url, json=payload, timeout=10)

            if response.status_code == 200:
                result = response.json()
                print(f"✓ Post published to LinkedIn")
                return {
                    'success': True,
                    'message': 'Post published to LinkedIn',
                    'postId': result.get('postId')
                }
            else:
                error = response.json().get('error', 'Unknown error')
                print(f"✗ LinkedIn post failed: {error}")
                return {'success': False, 'error': error}

        except requests.exceptions.ConnectionError:
            print("✗ LinkedIn MCP server not running on port 3002")
            return {'success': False, 'error': 'LinkedIn MCP server not available'}
        except Exception as e:
            print(f"✗ Error posting to LinkedIn: {e}")
            return {'success': False, 'error': str(e)}

    def _log_execution(self, approval_file: Path, action_type: str, result: Dict):
        """Log execution result"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'approval_file': approval_file.name,
            'action_type': action_type,
            'success': result.get('success'),
            'message': result.get('message'),
            'error': result.get('error')
        }

        print(f"\n📝 Result:")
        print(f"   Success: {result.get('success')}")
        print(f"   Message: {result.get('message', result.get('error'))}")


def main():
    """Main entry point for approval workflow"""
    import os

    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')

    workflow = ApprovalWorkflow(vault_path)

    print("=" * 60)
    print("🔄 Approval Workflow Processor")
    print("=" * 60)

    # Get approved actions
    approved_actions = workflow.get_approved_actions()

    if not approved_actions:
        print("\n✓ No approved actions to process")
    else:
        print(f"\n📋 Found {len(approved_actions)} approved action(s)")
        for approval_file in approved_actions:
            workflow.execute_approved_action(approval_file)

    # Show pending approvals
    pending = workflow.get_pending_approvals()
    if pending:
        print(f"\n⏳ Pending approvals: {len(pending)}")
        for p in pending:
            print(f"   - {p.name}")
    else:
        print("\n✓ No pending approvals")

    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
