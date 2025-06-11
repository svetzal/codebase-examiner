"""Tests for the serve command handlers."""

import sys
from unittest.mock import Mock, patch

import pytest
from rich.console import Console

from codebase_examiner.commands.serve import ServeCommandHandler, ServeStdioCommandHandler


@pytest.fixture
def mock_console():
    """Mock the Console class."""
    return Mock(spec=Console)


class DescribeServeCommandHandler:
    """Tests for the ServeCommandHandler."""

    def it_should_be_instantiated_with_console(self):
        """Test that ServeCommandHandler can be instantiated with a console."""
        console = Console()

        handler = ServeCommandHandler(console=console)

        assert isinstance(handler, ServeCommandHandler)
        assert handler.console == console

    def it_should_handle_serve_command_with_default_port(self, mock_console):
        """Test handling the serve command with the default port."""
        handler = ServeCommandHandler(console=mock_console)

        with patch("mojentic_mcp.mcp_http.start_server") as mock_start_server, \
             patch("mojentic_mcp.rpc.JsonRpcHandler") as mock_rpc_handler:
            result = handler.handle()

        assert result == 0
        mock_console.print.assert_any_call("[bold blue]Starting MCP server on port 8080...[/bold blue]")
        mock_rpc_handler.assert_called_once()
        mock_start_server.assert_called_once_with(8080, mock_rpc_handler.return_value)

    def it_should_handle_serve_command_with_custom_port(self, mock_console):
        """Test handling the serve command with a custom port."""
        handler = ServeCommandHandler(console=mock_console)

        with patch("mojentic_mcp.mcp_http.start_server") as mock_start_server, \
             patch("mojentic_mcp.rpc.JsonRpcHandler") as mock_rpc_handler:
            result = handler.handle(port=9000)

        assert result == 0
        mock_console.print.assert_any_call("[bold blue]Starting MCP server on port 9000...[/bold blue]")
        mock_rpc_handler.assert_called_once()
        mock_start_server.assert_called_once_with(9000, mock_rpc_handler.return_value)

    def it_should_handle_import_error(self, mock_console):
        """Test handling ImportError when MCP dependencies are not installed."""
        handler = ServeCommandHandler(console=mock_console)

        # Mock the import to raise ImportError
        with patch.dict('sys.modules', {'mojentic_mcp': None}):
            with patch('builtins.__import__', side_effect=ImportError("No module named 'mojentic_mcp'")):
                result = handler.handle()

        assert result == 1
        mock_console.print.assert_any_call("[bold red]Error: MCP server dependencies not installed[/bold red]")
        mock_console.print.assert_any_call("Try installing with: pip install codebase-examiner[mcp]")

    def it_should_handle_other_exceptions(self, mock_console):
        """Test handling other exceptions during execution."""
        handler = ServeCommandHandler(console=mock_console)

        with patch("mojentic_mcp.mcp_http.start_server", side_effect=Exception("Test error")):
            result = handler.handle()

        assert result == 1
        mock_console.print.assert_any_call("[bold red]Error: Test error[/bold red]")


class DescribeServeStdioCommandHandler:
    """Tests for the ServeStdioCommandHandler."""

    def it_should_be_instantiated_with_console(self):
        """Test that ServeStdioCommandHandler can be instantiated with a console."""
        console = Console()

        handler = ServeStdioCommandHandler(console=console)

        assert isinstance(handler, ServeStdioCommandHandler)
        assert handler.console == console

    def it_should_handle_serve_stdio_command(self, mock_console):
        """Test handling the serve_stdio command."""
        handler = ServeStdioCommandHandler(console=mock_console)

        with patch("mojentic_mcp.mcp_stdio.start_server") as mock_start_server, \
             patch("mojentic_mcp.rpc.JsonRpcHandler") as mock_rpc_handler:
            result = handler.handle()

        assert result == 0
        mock_console.print.assert_any_call("[bold blue]Starting STDIO MCP server...[/bold blue]")
        mock_console.print.assert_any_call("[bold green]Server ready to receive commands on stdin[/bold green]")
        mock_rpc_handler.assert_called_once()
        mock_start_server.assert_called_once_with(mock_rpc_handler.return_value)

    def it_should_handle_import_error(self, mock_console):
        """Test handling ImportError when MCP dependencies are not installed."""
        handler = ServeStdioCommandHandler(console=mock_console)

        # Mock the import to raise ImportError
        with patch.dict('sys.modules', {'mojentic_mcp': None}):
            with patch('builtins.__import__', side_effect=ImportError("No module named 'mojentic_mcp'")):
                result = handler.handle()

        assert result == 1
        mock_console.print.assert_any_call("[bold red]Error: MCP server dependencies not installed[/bold red]")
        mock_console.print.assert_any_call("Try installing with: pip install codebase-examiner[mcp]")

    def it_should_handle_other_exceptions(self, mock_console):
        """Test handling other exceptions during execution."""
        handler = ServeStdioCommandHandler(console=mock_console)

        with patch("mojentic_mcp.mcp_stdio.start_server", side_effect=Exception("Test error")):
            result = handler.handle()

        assert result == 1
        mock_console.print.assert_any_call("[bold red]Error: Test error[/bold red]")
