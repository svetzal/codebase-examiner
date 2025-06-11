"""Tests for the base command handler."""

import pytest
from rich.console import Console
from unittest.mock import Mock

from codebase_examiner.commands.base import CommandHandler


class ConcreteCommandHandler(CommandHandler):
    """Concrete implementation of CommandHandler for testing."""
    
    def handle(self, **kwargs) -> int:
        """Handle the command."""
        return 0


class DescribeCommandHandler:
    """Tests for the CommandHandler base class."""
    
    def it_should_be_instantiated_with_console(self):
        """Test that CommandHandler can be instantiated with a console."""
        console = Console()
        
        handler = ConcreteCommandHandler(console=console)
        
        assert isinstance(handler, CommandHandler)
        assert handler.console == console
    
    def it_should_create_default_console_when_none_provided(self):
        """Test that CommandHandler creates a default console when none is provided."""
        handler = ConcreteCommandHandler()
        
        assert isinstance(handler, CommandHandler)
        assert isinstance(handler.console, Console)
    
    def it_should_require_subclasses_to_implement_handle(self):
        """Test that subclasses must implement the handle method."""
        # This test verifies that CommandHandler is an abstract class
        # that requires subclasses to implement the handle method
        with pytest.raises(TypeError):
            CommandHandler()