"""Command-line interface for the Codebase Examiner tool."""

import sys
from typing import Optional, List

import typer
from rich.console import Console

from codebase_examiner.commands.examine import ExamineCommandHandler
from codebase_examiner.commands.serve import ServeCommandHandler, ServeStdioCommandHandler
from codebase_examiner.core.doc_generator import OutputFormat

app = typer.Typer(
    help="Codebase Examiner - A tool to analyze Python codebases and generate documentation"
)
console = Console()  # Use stdout for console output


@app.command()
def examine(
    directory: str = typer.Option(
        ".", "--directory", "-d", help="The directory to examine"
    ),
    output_format: OutputFormat = typer.Option(
        OutputFormat.MARKDOWN, "--format", "-f", help="Output format (markdown or json)"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
    exclude: List[str] = typer.Option(
        [".venv", ".git"],
        "--exclude",
        "-e",
        help="Directories to exclude (uses .gitignore patterns first if present, "
        "then falls back to these directories)",
    ),
    include_dotfiles: bool = typer.Option(
        False,
        "--include-dotfiles",
        help="Include files and directories starting with a dot",
    ),
    include_test_files: bool = typer.Option(
        False, "--include-test-files", help="Include test files in the documentation"
    ),
    sections: Optional[List[str]] = typer.Option(
        None,
        "--section",
        "-s",
        help="Sections to include in order (title, toc, modules)",
    ),
    use_gitignore: bool = typer.Option(
        True,
        "--use-gitignore/--no-gitignore",
        help="Use .gitignore file for exclusion patterns",
    ),
):
    """Examine a Python codebase and generate documentation."""
    handler = ExamineCommandHandler(console=console)
    return handler.handle(
        directory=directory,
        output_format=output_format,
        output_file=output_file,
        exclude=exclude,
        include_dotfiles=include_dotfiles,
        include_test_files=include_test_files,
        sections=sections,
        use_gitignore=use_gitignore,
    )


@app.command()
def serve(
    port: int = typer.Option(
        8080, "--port", "-p", help="Port to run the MCP server on"
    ),
):
    """Run the Codebase Examiner as an MCP server over HTTP."""
    handler = ServeCommandHandler(console=console)
    return handler.handle(port=port)


@app.command()
def serve_stdio():
    """Run the Codebase Examiner as an MCP server over standard input/output."""
    handler = ServeStdioCommandHandler(console=console)
    return handler.handle()


if __name__ == "__main__":
    sys.exit(app())
