"""Command-line interface for the Codebase Examiner tool."""


import sys
import json
from pathlib import Path
from typing import Optional, Set, List

import typer
from rich.console import Console
from rich.markdown import Markdown


from codebase_examiner.core.code_inspector import inspect_codebase
from codebase_examiner.core.doc_generator import generate_documentation

app = typer.Typer(help="Codebase Examiner - A tool to analyze Python codebases and generate documentation")
console = Console()


@app.command()
def examine(
    directory: str = typer.Option(".", "--directory", "-d", help="The directory to examine"),
    output_format: str = typer.Option("markdown", "--format", "-f", help="Output format (markdown or json)"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
    exclude: List[str] = typer.Option([".venv"], "--exclude", "-e", help="Directories to exclude"),
    include_dotfiles: bool = typer.Option(False, "--include-dotfiles", help="Include files and directories starting with a dot"),
):
    """Examine a Python codebase and generate documentation."""
    console.print(f"[bold blue]Examining codebase in directory: {directory}[/bold blue]")
    
    # Convert exclude list to set
    exclude_dirs = set(exclude)
    
    try:
        # Inspect the codebase
        console.print("[bold]Finding and analyzing Python files...[/bold]")
        modules = inspect_codebase(directory, exclude_dirs, not include_dotfiles)
        
        # Generate documentation
        console.print(f"[bold]Generating {output_format} documentation...[/bold]")
        documentation = generate_documentation(modules, output_format)
        
        # Output the documentation
        if output_file:
            output_path = Path(output_file)
            output_path.write_text(documentation)
            console.print(f"[bold green]Documentation written to {output_file}[/bold green]")
        else:
            if output_format.lower() == "markdown":
                console.print(Markdown(documentation))
            else:
                console.print_json(json.loads(documentation))
        
        return 0
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        return 1


@app.command()
def serve(
    port: int = typer.Option(8080, "--port", "-p", help="Port to run the MCP server on"),
):
    """Run the Codebase Examiner as an MCP server over HTTP."""

    
    try:
        from codebase_examiner.mcp import start_server
        console.print(f"[bold blue]Starting MCP server on port {port}...[/bold blue]")
        start_server(port)
        return 0
    except ImportError:
        console.print("[bold red]Error: MCP server dependencies not installed[/bold red]")
        console.print("Try installing with: pip install codebase-examiner[mcp]")
        return 1
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        return 1


@app.command()
def serve_stdio():
    """Run the Codebase Examiner as an MCP server over standard input/output."""

    
    try:
        from codebase_examiner.mcp_stdio import start_server
        console.print("[bold blue]Starting STDIO MCP server...[/bold blue]")
        # This print must be the last console output before the server takes over stdout
        console.print("[bold green]Server ready to receive commands on stdin[/bold green]")
        start_server()
        return 0
    except ImportError:
        console.print("[bold red]Error: MCP server dependencies not installed[/bold red]")
        console.print("Try installing with: pip install codebase-examiner[mcp]")
        return 1
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        return 1


if __name__ == "__main__":
    sys.exit(app())