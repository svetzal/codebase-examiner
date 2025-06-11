"""Base command handler for the Codebase Examiner CLI."""

from abc import ABC, abstractmethod
from rich.console import Console


class CommandHandler(ABC):
    """Base class for command handlers."""

    def __init__(self, console: Console = None):
        """Initialize the command handler.

        Args:
            console: The console to use for output. If None, a new console will be created.
        """
        self.console = console or Console()

    @abstractmethod
    def handle(self, **kwargs) -> int:
        """Handle the command.

        Args:
            **kwargs: Command-specific arguments.

        Returns:
            int: The exit code (0 for success, non-zero for failure).
        """
        pass