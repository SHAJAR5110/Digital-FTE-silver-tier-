"""Gmail Watcher - Monitors Gmail inbox for unread emails"""

import os
import pickle
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.api_core import gapic_v1
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gmail API scopes (read-only)
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailWatcher(BaseWatcher):
    """Watches Gmail inbox for unread emails"""

    def __init__(self, vault_path: str, credentials_path: str, check_interval: int = 120):
        """
        Initialize Gmail Watcher.

        Args:
            vault_path: Path to the Obsidian vault
            credentials_path: Path to Gmail OAuth2 credentials.json
            check_interval: Seconds between checks (default 120)
        """
        super().__init__(vault_path, check_interval)

        self.credentials_path = Path(credentials_path).expanduser()
        self.token_path = Path('~/.secrets/gmail_token.pickle').expanduser()
        self.processed_ids = set()

        # Authenticate with Gmail API
        self.service = self._authenticate()
        self.logger.info("Gmail Watcher initialized successfully")

    def _authenticate(self):
        """
        Authenticate with Gmail API using OAuth2.

        Returns:
            Google API service object for Gmail
        """
        creds = None

        # Load existing token if available
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token_file:
                creds = pickle.load(token_file)
                self.logger.info("Loaded existing Gmail token")

        # If no valid credentials, run OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.info("Refreshing Gmail token")
                creds.refresh(Request())
            else:
                self.logger.info("Starting Gmail OAuth flow (browser will open)")
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"Gmail credentials not found at {self.credentials_path}. "
                        f"Follow instructions in requirements.txt to set up OAuth2."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
                self.logger.info("Gmail OAuth flow completed")

            # Save token for future use
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, 'wb') as token_file:
                pickle.dump(creds, token_file)
                self.logger.info(f"Gmail token saved to {self.token_path}")

        return build('gmail', 'v1', credentials=creds)

    def check_for_updates(self) -> list:
        """
        Check Gmail inbox for unread emails.

        Returns:
            List of email dicts with id, subject, sender, date, snippet
        """
        try:
            # Query for unread emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=20
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                return []

            # Process each message
            new_emails = []
            for msg in messages:
                msg_id = msg['id']

                # Skip if already processed
                if msg_id in self.processed_ids:
                    continue

                # Get full message details
                try:
                    message = self.service.users().messages().get(
                        userId='me',
                        id=msg_id,
                        format='metadata',
                        metadataHeaders=['Subject', 'From', 'Date']
                    ).execute()

                    headers = message.get('payload', {}).get('headers', [])

                    # Extract header values
                    email_data = {
                        'id': msg_id,
                        'subject': self._get_header(headers, 'Subject'),
                        'sender': self._get_header(headers, 'From'),
                        'date': self._get_header(headers, 'Date'),
                        'snippet': message.get('snippet', '')
                    }

                    new_emails.append(email_data)
                    self.logger.info(f"Found email: {email_data['subject'][:50]}")

                except Exception as e:
                    self.logger.error(f"Error processing message {msg_id}: {e}")

            return new_emails

        except Exception as e:
            self.logger.error(f"Error checking Gmail: {e}")
            return []

    def create_action_file(self, email: dict) -> Path:
        """
        Create a markdown action file for the email.

        Args:
            email: Email dict with id, subject, sender, date, snippet

        Returns:
            Path to created action file
        """
        # Sanitize subject to create safe filename
        safe_subject = self._sanitize_filename(email['subject'])
        msg_id_short = email['id'][:8]

        # Create base filename
        base_filename = f"EMAIL_{safe_subject}_{msg_id_short}"
        filename = f"{base_filename}.md"
        filepath = self.needs_action / filename

        # Handle duplicate filenames
        counter = 1
        while filepath.exists():
            filename = f"{base_filename}_{counter}.md"
            filepath = self.needs_action / filename
            counter += 1

        # Track this email
        self.processed_ids.add(email['id'])

        # Create markdown content
        detected_at = datetime.now().isoformat()

        metadata = self.create_metadata_header(
            type='email',
            message_id=email['id'],
            sender=email['sender'],
            subject=email['subject'],
            date=email['date'],
            detected_at=detected_at,
            status='pending',
            priority='normal'
        )

        content = f"""{metadata}

# Email: {email['subject']}

## Email Details
- **From**: {email['sender']}
- **Subject**: {email['subject']}
- **Date**: {email['date']}
- **Message ID**: {email['id']}

## Summary
{email['snippet']}

## Status
- [ ] Review email
- [ ] Determine response needed
- [ ] Create response plan if required
- [ ] Move to Done when processed

## Notes
Add analysis or response draft below.

---
**Source**: Gmail Watcher
**Next Step**: Claude will analyze and create a Plan if action is needed.
"""

        filepath.write_text(content)
        self.logger.info(f"Created action file: {filepath}")

        return filepath

    @staticmethod
    def _get_header(headers: list, header_name: str) -> str:
        """Extract a header value from email headers list."""
        for header in headers:
            if header.get('name') == header_name:
                return header.get('value', '')
        return ''

    @staticmethod
    def _sanitize_filename(text: str, max_length: int = 40) -> str:
        """
        Sanitize text to create a safe filename.

        Args:
            text: Text to sanitize
            max_length: Maximum filename length

        Returns:
            Safe filename string
        """
        # Keep only alphanumeric and underscores
        safe = ''.join(c if c.isalnum() or c == '_' else '_' for c in text)
        # Remove leading/trailing underscores and truncate
        safe = safe.strip('_')[:max_length]
        return safe or 'email'


def main():
    """Entry point for Gmail Watcher"""
    # Get configuration from environment
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')
    credentials_path = os.getenv(
        'GMAIL_CREDENTIALS_PATH',
        '~/.secrets/gmail_credentials.json'
    )
    check_interval = int(os.getenv('GMAIL_CHECK_INTERVAL', '120'))

    # Create and run watcher
    watcher = GmailWatcher(vault_path, credentials_path, check_interval)
    watcher.run()


if __name__ == '__main__':
    main()
