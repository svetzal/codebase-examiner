"""Command handlers for the serve and serve_stdio commands."""

from typing import Optional

from rich.console import Console

from codebase_examiner.commands.base import CommandHandler
from codebase_examiner.core.examiner_tool import ExaminerTool


class ServeCommandHandler(CommandHandler):
    """Command handler for the serve command."""

    def handle(self, port: int = 8080, **kwargs) -> int:
        """Handle the serve command.

        Args:
            port: Port to run the MCP server on.
            **kwargs: Additional arguments.

        Returns:
            int: The exit code (0 for success, non-zero for failure).
        """
        try:
            from mojentic_mcp.mcp_http import start_server
            from mojentic_mcp.rpc import JsonRpcHandler

            self.console.print(f"[bold blue]Starting MCP server on port {port}...[/bold blue]")
            rpc_handler = JsonRpcHandler(tools=[ExaminerTool()])
            start_server(port, rpc_handler)
            return 0
        except ImportError:
            self.console.print(
                "[bold red]Error: MCP server dependencies not installed[/bold red]"
            )
            self.console.print("Try installing with: pip install codebase-examiner[mcp]")
            return 1
        except Exception as e:
            self.console.print(f"[bold red]Error: {str(e)}[/bold red]")
            return 1


class ServeStdioCommandHandler(CommandHandler):
    """Command handler for the serve_stdio command."""

    def handle(self, **kwargs) -> int:
        """Handle the serve_stdio command.

        Args:
            **kwargs: Additional arguments.

        Returns:
            int: The exit code (0 for success, non-zero for failure).
        """
        try:
            from mojentic_mcp.mcp_stdio import start_server
            from mojentic_mcp.rpc import JsonRpcHandler

            self.console.print("[bold blue]Starting STDIO MCP server...[/bold blue]")
            # This print must be the last console output before the server takes over stdout
            self.console.print(
                "[bold green]Server ready to receive commands on stdin[/bold green]"
            )
            rpc_handler = JsonRpcHandler(tools=[ExaminerTool()])
            start_server(rpc_handler)
            return 0
        except ImportError:
            self.console.print(
                "[bold red]Error: MCP server dependencies not installed[/bold red]"
            )
            self.console.print("Try installing with: pip install codebase-examiner[mcp]")
            return 1
        except Exception as e:
            self.console.print(f"[bold red]Error: {str(e)}[/bold red]")
            return 1