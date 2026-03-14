"""WhatsApp Watcher - Monitors WhatsApp Web for unread messages"""

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


class WhatsAppWatcher(BaseWatcher):
    """Watches WhatsApp Web for unread messages"""

    def __init__(
        self,
        vault_path: str,
        session_path: str = None,
        check_interval: int = 30,
        keyword_filters: str = None,
    ):
        """
        Initialize WhatsApp Watcher.

        Args:
            vault_path: Path to the Obsidian vault
            session_path: Path to store WhatsApp session (cookies, local storage)
            check_interval: Seconds between checks (default 30)
            keyword_filters: Comma-separated keywords to filter important messages
        """
        super().__init__(vault_path, check_interval)

        self.session_path = Path(session_path or '~/.secrets/whatsapp_session').expanduser()
        self.keyword_filters = [
            k.strip().lower()
            for k in (keyword_filters or 'urgent,invoice,payment,important,asap').split(',')
        ]

        self.browser = None
        self.page = None
        self.playwright = None
        self.processed_messages = set()

        self.logger.info(f"WhatsApp Watcher initialized (checking every {check_interval}s)")

    def _start_browser(self):
        """Start Playwright browser with WhatsApp session"""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )

            # Load session if exists, otherwise create new context
            context_args = {'locale': 'en-US'}
            if self.session_path.exists():
                self.logger.info(f"Loading WhatsApp session from {self.session_path}")
                context_args['storage_state'] = str(self.session_path / 'state.json')

            context = self.browser.new_context(**context_args)
            self.page = context.new_page()

            return context

        except Exception as e:
            self.logger.error(f"Error starting browser: {e}")
            raise

    def _authenticate_whatsapp(self):
        """
        Authenticate with WhatsApp Web using QR code.
        On first run, requires QR code scan with phone.
        On subsequent runs, uses cached session.
        """
        try:
            self.logger.info("Loading WhatsApp Web...")
            self.page.goto('https://web.whatsapp.com', wait_until='networkidle', timeout=30000)

            # Check if already logged in
            try:
                self.page.wait_for_selector('div[role="button"][aria-label*="Emoji"]', timeout=5000)
                self.logger.info("Already logged in (using cached session)")
                return True
            except PlaywrightTimeout:
                pass

            # If not logged in, wait for QR code and scan
            self.logger.info("Waiting for QR code (scan with your phone)...")
            try:
                qr_selector = 'canvas[aria-label="Scan this QR code to log in to WhatsApp"]'
                self.page.wait_for_selector(qr_selector, timeout=60000)
                self.logger.info("QR code displayed - please scan with your phone")

                # Wait for login to complete (look for main chat area)
                self.page.wait_for_selector(
                    'div[role="button"][aria-label*="Emoji"]',
                    timeout=120000
                )
                self.logger.info("Login successful!")

                # Save session for future use
                self._save_session()
                return True

            except PlaywrightTimeout:
                self.logger.error("QR code timeout - user did not scan within 2 minutes")
                return False

        except Exception as e:
            self.logger.error(f"Error authenticating WhatsApp: {e}")
            return False

    def _save_session(self):
        """Save WhatsApp session (cookies, local storage) for future logins"""
        try:
            self.session_path.mkdir(parents=True, exist_ok=True)

            # Save storage state (cookies, local storage, etc.)
            state = self.page.context.storage_state()
            state_file = self.session_path / 'state.json'
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)

            self.logger.info(f"Session saved to {self.session_path}")
        except Exception as e:
            self.logger.error(f"Error saving session: {e}")

    def check_for_updates(self) -> list:
        """
        Check WhatsApp for unread messages.

        Returns:
            List of unread message dicts with contact_name, message_snippet, keyword_match
        """
        try:
            # Start browser if needed
            if not self.page:
                context = self._start_browser()
                authenticated = self._authenticate_whatsapp()
                if not authenticated:
                    self.logger.error("Failed to authenticate WhatsApp")
                    return []

            # Get list of chats with unread badges
            unread_messages = self._extract_unread_messages()

            if unread_messages:
                self.logger.info(f"Found {len(unread_messages)} unread message(s)")

            return unread_messages

        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}")
            return []

    def _extract_unread_messages(self) -> list:
        """
        Extract unread messages from chat list.

        Returns:
            List of unread message dicts
        """
        unread_messages = []

        try:
            # Find all chat items with unread badges
            # WhatsApp marks unread chats with a green badge
            chat_items = self.page.query_selector_all(
                'div[role="option"]'  # Chat list items
            )

            for chat_item in chat_items:
                try:
                    # Check if chat has unread indicator (usually a badge with number or dot)
                    unread_badge = chat_item.query_selector('span[aria-label*="unread"]')
                    if not unread_badge:
                        # Try alternative: look for highlighted chat (darker background)
                        classes = chat_item.get_attribute('class') or ''
                        if 'unread' not in classes.lower():
                            continue

                    # Get contact name
                    contact_name = self._get_contact_name(chat_item)
                    if not contact_name:
                        continue

                    # Get message snippet
                    message_snippet = self._get_message_snippet(chat_item)

                    # Check for keyword match
                    keyword_match = self._check_keywords(message_snippet)

                    msg_dict = {
                        'contact_name': contact_name,
                        'message_snippet': message_snippet,
                        'keyword_match': keyword_match,
                        'timestamp': datetime.now().isoformat(),
                    }

                    # Deduplicate
                    msg_key = f"{contact_name}_{message_snippet[:20]}_{datetime.now().date()}"
                    if msg_key not in self.processed_messages:
                        unread_messages.append(msg_dict)
                        self.processed_messages.add(msg_key)

                except Exception as e:
                    self.logger.debug(f"Error processing chat item: {e}")

        except Exception as e:
            self.logger.error(f"Error extracting unread messages: {e}")

        return unread_messages

    def _get_contact_name(self, chat_item) -> str:
        """Extract contact/group name from chat item"""
        try:
            # Contact name is typically in a span or div with title
            name_elem = chat_item.query_selector('span[title]')
            if name_elem:
                return name_elem.get_attribute('title')

            # Fallback: look for any text in the chat header area
            text_elem = chat_item.query_selector('span.x3nfvp2')  # Common WhatsApp class
            if text_elem:
                return text_elem.text_content()

            return 'Unknown Contact'
        except Exception as e:
            self.logger.debug(f"Error getting contact name: {e}")
            return 'Unknown Contact'

    def _get_message_snippet(self, chat_item) -> str:
        """Extract message preview/snippet from chat item"""
        try:
            # Message preview is usually in a secondary text element
            msg_elem = chat_item.query_selector('span.x3nfvp2:nth-of-type(2)')
            if msg_elem:
                return msg_elem.text_content().strip()

            # Fallback: look for any secondary text
            msg_elem = chat_item.query_selector('div[role="option"] div:nth-child(2)')
            if msg_elem:
                text = msg_elem.text_content().strip()
                if text and text != 'Unknown Contact':
                    return text

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
            message: Message dict with contact_name, message_snippet, keyword_match

        Returns:
            Path to created action file
        """
        contact_name = message.get('contact_name', 'Unknown')
        safe_contact = self._sanitize_filename(contact_name)
        keyword_match = message.get('keyword_match', 'none')

        # Create base filename
        base_filename = f"WHATSAPP_{safe_contact}_{keyword_match}"
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
            type='whatsapp',
            contact_name=contact_name,
            message_snippet=message.get('message_snippet', ''),
            keyword_match=keyword_match,
            timestamp=timestamp,
            detected_at=detected_at,
            status='pending',
            priority='high' if keyword_match != 'none' else 'normal'
        )

        priority_label = '🔴 HIGH' if keyword_match != 'none' else '🟢 NORMAL'
        keyword_note = f"\n**Keyword Match**: {keyword_match}" if keyword_match != 'none' else ''

        content = f"""{metadata}

# WhatsApp Message: {contact_name}

## Message Details
- **From**: {contact_name}
- **Timestamp**: {timestamp}
- **Priority**: {priority_label}{keyword_note}

## Message Content
{message.get('message_snippet', '[Message preview unavailable]')}

## Status
- [ ] Review message
- [ ] Determine response needed
- [ ] Create response plan if required
- [ ] Move to Done when processed

## Response Draft
Add your response draft below:

---

---
**Source**: WhatsApp Watcher
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
            self.logger.info("WhatsApp Watcher stopping...")
        finally:
            self.close()


def main():
    """Entry point for WhatsApp Watcher"""
    vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')
    session_path = os.getenv('WHATSAPP_SESSION_PATH', '~/.secrets/whatsapp_session')
    check_interval = int(os.getenv('WHATSAPP_CHECK_INTERVAL', '30'))
    keyword_filters = os.getenv('WHATSAPP_KEYWORD_FILTERS', 'urgent,invoice,payment,important,asap')

    watcher = WhatsAppWatcher(vault_path, session_path, check_interval, keyword_filters)
    watcher.run()


if __name__ == '__main__':
    main()
