"""LinkedIn Watcher - Monitors LinkedIn for messages and opportunities"""

import os
import time
import json
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher
from dotenv import load_dotenv

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    raise ImportError(
        "Playwright not installed. Run: pip install playwright\n"
        "Then: playwright install chromium"
    )

# Load environment variables
load_dotenv()


class LinkedInWatcher(BaseWatcher):
    """Watches LinkedIn for messages and business opportunities"""

    def __init__(
        self,
        vault_path: str,
        email: str = None,
        password: str = None,
        session_path: str = None,
        check_interval: int = 300,
        keyword_filters: str = None,
    ):
        """
        Initialize LinkedIn Watcher.

        Args:
            vault_path: Path to the Obsidian vault
            email: LinkedIn email for login
            password: LinkedIn password for login
            session_path: Path to store LinkedIn session (cookies, local storage)
            check_interval: Seconds between checks (default 300 = 5 minutes)
            keyword_filters: Comma-separated keywords to filter opportunities
        """
        super().__init__(vault_path, check_interval)

        self.email = email or os.getenv('LINKEDIN_EMAIL')
        self.password = password or os.getenv('LINKEDIN_PASSWORD')

        if not self.email or not self.password:
            raise ValueError(
                "LinkedIn credentials not found. "
                "Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD in .env file"
            )

        self.session_path = Path(session_path or '~/.secrets/linkedin_session').expanduser()
        self.keyword_filters = [
            k.strip().lower()
            for k in (keyword_filters or 'opportunity,collaboration,job,client,contract,project,partnership,consulting').split(',')
        ]

        self.browser = None
        self.page = None
        self.playwright = None
        self.processed_messages = set()

        self.logger.info(f"LinkedIn Watcher initialized (checking every {check_interval}s)")

    def _start_browser(self):
        """Start Playwright browser with LinkedIn session"""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )

            # Load session if exists
            context_args = {'locale': 'en-US'}
            if self.session_path.exists():
                self.logger.info(f"Loading LinkedIn session from {self.session_path}")
                context_args['storage_state'] = str(self.session_path / 'state.json')

            context = self.browser.new_context(**context_args)
            self.page = context.new_page()
            self.page.set_default_timeout(60000)  # 60 second default timeout

            return context

        except Exception as e:
            self.logger.error(f"Error starting browser: {e}")
            raise

    def _authenticate_linkedin(self):
        """
        Authenticate with LinkedIn using email and password.
        On first run, logs in and saves session.
        On subsequent runs, uses cached session.
        """
        try:
            self.logger.info("Loading LinkedIn...")
            self.page.goto('https://www.linkedin.com/login', wait_until='networkidle', timeout=30000)

            # Check if already logged in
            try:
                self.page.wait_for_selector('a[href="/feed/"]', timeout=5000)
                self.logger.info("Already logged in (using cached session)")
                return True
            except PlaywrightTimeout:
                pass

            # Login with email and password
            self.logger.info("Logging in with provided credentials...")

            # Fill email field
            email_field = self.page.query_selector('input[type="email"]')
            if email_field:
                email_field.fill(self.email)
                self.logger.info("Email entered")

            # Fill password field
            password_field = self.page.query_selector('input[type="password"]')
            if password_field:
                password_field.fill(self.password)
                self.logger.info("Password entered")

            # Click sign in button
            signin_button = self.page.query_selector('button[type="submit"]')
            if signin_button:
                signin_button.click()
                self.logger.info("Sign in button clicked")

            # Wait for feed to load (indicates successful login)
            try:
                self.page.wait_for_selector('a[href="/feed/"]', timeout=60000)
                self.logger.info("Login successful!")

                # Navigate to messaging
                time.sleep(2)  # Give page time to stabilize
                self.page.goto('https://www.linkedin.com/messaging', wait_until='networkidle', timeout=30000)

                # Save session
                self._save_session()
                return True

            except PlaywrightTimeout:
                self.logger.error("Login timeout - may require 2FA approval or account verification")
                return False

        except Exception as e:
            self.logger.error(f"Error authenticating LinkedIn: {e}")
            return False

    def _save_session(self):
        """Save LinkedIn session for future logins"""
        try:
            self.session_path.mkdir(parents=True, exist_ok=True)

            # Save storage state
            state = self.page.context.storage_state()
            state_file = self.session_path / 'state.json'
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)

            self.logger.info(f"Session saved to {self.session_path}")
        except Exception as e:
            self.logger.error(f"Error saving session: {e}")

    def check_for_updates(self) -> list:
        """
        Check LinkedIn for unread messages.

        Returns:
            List of unread message dicts with sender_name, message_snippet, keyword_match
        """
        try:
            # Start browser if needed
            if not self.page:
                context = self._start_browser()
                authenticated = self._authenticate_linkedin()
                if not authenticated:
                    self.logger.error("Failed to authenticate LinkedIn")
                    return []

            # Navigate to messaging if not already there
            try:
                self.page.goto('https://www.linkedin.com/messaging', wait_until='networkidle', timeout=30000)
            except Exception as e:
                self.logger.debug(f"Error navigating to messaging: {e}")
                return []

            # Get list of unread messages
            unread_messages = self._extract_unread_messages()

            if unread_messages:
                self.logger.info(f"Found {len(unread_messages)} unread message(s)")

            return unread_messages

        except Exception as e:
            self.logger.error(f"Error checking LinkedIn: {e}")
            return []

    def _extract_unread_messages(self) -> list:
        """
        Extract unread messages from LinkedIn messaging page.

        Returns:
            List of unread message dicts
        """
        unread_messages = []

        try:
            # Wait for message list to load
            time.sleep(2)

            # Find all unread messages
            # LinkedIn marks unread with bold text or specific class
            message_items = self.page.query_selector_all(
                'li[data-item-id]'  # Message items in conversation list
            )

            for i, msg_item in enumerate(message_items[:20]):  # Check first 20
                try:
                    # Check if unread (bold text or specific indicator)
                    item_html = msg_item.inner_html()
                    is_unread = 'font-weight' in item_html or 'unread' in item_html.lower()

                    if not is_unread:
                        continue

                    # Get sender name
                    sender_name = self._get_sender_name(msg_item)
                    if not sender_name:
                        continue

                    # Get message snippet
                    message_snippet = self._get_message_snippet(msg_item)

                    # Check for keyword match
                    keyword_match = self._check_keywords(message_snippet)

                    msg_dict = {
                        'sender_name': sender_name,
                        'message_snippet': message_snippet,
                        'keyword_match': keyword_match,
                        'timestamp': datetime.now().isoformat(),
                    }

                    # Deduplicate
                    msg_key = f"{sender_name}_{message_snippet[:20]}_{datetime.now().date()}"
                    if msg_key not in self.processed_messages:
                        unread_messages.append(msg_dict)
                        self.processed_messages.add(msg_key)

                except Exception as e:
                    self.logger.debug(f"Error processing message item {i}: {e}")

        except Exception as e:
            self.logger.error(f"Error extracting unread messages: {e}")

        return unread_messages

    def _get_sender_name(self, msg_item) -> str:
        """Extract sender name from message item"""
        try:
            # Try to find name in various LinkedIn structures
            name_elem = msg_item.query_selector('[data-test="message-participant-name"]')
            if name_elem:
                return name_elem.text_content().strip()

            # Fallback: look for any strong/bold text (unread items are bold)
            name_elem = msg_item.query_selector('strong')
            if name_elem:
                return name_elem.text_content().strip()

            # Fallback: look for heading
            name_elem = msg_item.query_selector('h4, h3')
            if name_elem:
                return name_elem.text_content().strip()

            return 'Unknown Sender'
        except Exception as e:
            self.logger.debug(f"Error getting sender name: {e}")
            return 'Unknown Sender'

    def _get_message_snippet(self, msg_item) -> str:
        """Extract message preview/snippet from message item"""
        try:
            # Try to find message text
            msg_elem = msg_item.query_selector('[data-test="message-preview"]')
            if msg_elem:
                return msg_elem.text_content().strip()

            # Fallback: look for secondary text
            msg_elem = msg_item.query_selector('p, span[data-test*="message"]')
            if msg_elem:
                text = msg_elem.text_content().strip()
                if text and len(text) > 5:
                    return text

            # Last resort: get all text content and extract preview
            full_text = msg_item.text_content().strip()
            lines = [l.strip() for l in full_text.split('\n') if l.strip()]
            if len(lines) > 1:
                return lines[-1]  # Usually last line is preview

            return '[Message preview unavailable]'
        except Exception as e:
            self.logger.debug(f"Error getting message snippet: {e}")
            return '[Message preview unavailable]'

    def _check_keywords(self, text: str) -> str:
        """
        Check if message contains any keywords.

        Args:
            text: Message text to check

        Returns:
            Matching keyword or 'none'
        """
        text_lower = text.lower()
        for keyword in self.keyword_filters:
            if keyword in text_lower:
                return keyword
        return 'none'

    def create_action_file(self, message: dict) -> Path:
        """
        Create a markdown action file for the message.

        Args:
            message: Message dict with sender_name, message_snippet, keyword_match

        Returns:
            Path to created action file
        """
        sender_name = message.get('sender_name', 'Unknown')
        safe_sender = self._sanitize_filename(sender_name)
        keyword_match = message.get('keyword_match', 'none')

        # Create base filename
        base_filename = f"LINKEDIN_{safe_sender}_{keyword_match}"
        filename = f"{base_filename}.md"
        filepath = self.needs_action / filename

        # Handle duplicates
        counter = 1
        while filepath.exists():
            filename = f"{base_filename}_{counter}.md"
            filepath = self.needs_action / filename
            counter += 1

        # Create markdown content
        detected_at = datetime.now().isoformat()
        timestamp = message.get('timestamp', detected_at)

        metadata = self.create_metadata_header(
            type='linkedin',
            sender_name=sender_name,
            message_snippet=message.get('message_snippet', ''),
            keyword_match=keyword_match,
            timestamp=timestamp,
            detected_at=detected_at,
            status='pending',
            priority='high' if keyword_match != 'none' else 'normal'
        )

        priority_label = '🔴 HIGH' if keyword_match != 'none' else '🟢 NORMAL'
        keyword_note = f"\n**Opportunity Type**: {keyword_match}" if keyword_match != 'none' else ''

        content = f"""{metadata}

# LinkedIn Message: {sender_name}

## Message Details
- **From**: {sender_name}
- **Timestamp**: {timestamp}
- **Priority**: {priority_label}{keyword_note}

## Message Content
{message.get('message_snippet', '[Message preview unavailable]')}

## Action Items
- [ ] Read full message on LinkedIn
- [ ] Assess opportunity/relevance
- [ ] Draft response if interested
- [ ] Move to Done when processed

## Analysis
Add your analysis and next steps below:

---

---
**Source**: LinkedIn Watcher
**Next Step**: Claude will analyze and create a Plan if action is needed.
"""

        filepath.write_text(content)
        self.logger.info(f"Created action file: {filepath}")

        return filepath

    @staticmethod
    def _sanitize_filename(text: str, max_length: int = 40) -> str:
        """Sanitize text to create safe filename"""
        safe = ''.join(c if c.isalnum() or c == '_' else '_' for c in text)
        safe = safe.strip('_')[:max_length]
        return safe or 'message'

    def close(self):
        """Clean up browser resources"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            self.logger.info("Browser closed")
        except Exception as e:
            self.logger.error(f"Error closing browser: {e}")

    def run(self):
        """Main loop with proper cleanup"""
        try:
            super().run()
        except KeyboardInterrupt:
            self.logger.info("LinkedIn Watcher stopping...")
        finally:
            self.close()


def main():
    """Entry point for LinkedIn Watcher"""
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    session_path = os.getenv('LINKEDIN_SESSION_PATH', '~/.secrets/linkedin_session')
    check_interval = int(os.getenv('LINKEDIN_CHECK_INTERVAL', '300'))
    keyword_filters = os.getenv(
        'LINKEDIN_KEYWORD_FILTERS',
        'opportunity,collaboration,job,client,contract,project,partnership,consulting'
    )

    watcher = LinkedInWatcher(vault_path, email, password, session_path, check_interval, keyword_filters)
    watcher.run()


if __name__ == '__main__':
    main()
