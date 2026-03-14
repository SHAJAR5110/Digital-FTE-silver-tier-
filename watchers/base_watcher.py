"""Base Watcher class for all Digital FTE watchers"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime


class BaseWatcher(ABC):
    """Abstract base class for all Watcher implementations"""

    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the Watcher.

        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval

        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

        # Validate vault exists
        if not self.vault_path.exists():
            self.logger.error(f"Vault path does not exist: {self.vault_path}")
            raise ValueError(f"Vault path not found: {self.vault_path}")

        if not self.needs_action.exists():
            self.logger.warning(f"Creating /Needs_Action folder: {self.needs_action}")
            self.needs_action.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items to process.

        Returns:
            List of new items (format depends on subclass)
        """
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create a markdown file in /Needs_Action.

        Args:
            item: Item to process (format depends on subclass)

        Returns:
            Path to created file
        """
        pass

    def run(self):
        """Main loop: continuously check for updates"""
        self.logger.info(
            f"Starting {self.__class__.__name__} "
            f"(checking every {self.check_interval}s)"
        )

        while True:
            try:
                items = self.check_for_updates()
                if items:
                    self.logger.info(f"Found {len(items)} new item(s)")
                    for item in items:
                        try:
                            self.create_action_file(item)
                        except Exception as e:
                            self.logger.error(
                                f"Error creating action file for {item}: {e}"
                            )
            except Exception as e:
                self.logger.error(f"Error checking for updates: {e}")

            time.sleep(self.check_interval)

    def create_metadata_header(self, **kwargs) -> str:
        """
        Create YAML front-matter for markdown files.

        Args:
            **kwargs: Key-value pairs for metadata

        Returns:
            YAML header string
        """
        lines = ['---']
        for key, value in kwargs.items():
            if isinstance(value, str):
                lines.append(f'{key}: {value}')
            else:
                lines.append(f'{key}: {value}')
        lines.append('---')
        return '\n'.join(lines)
