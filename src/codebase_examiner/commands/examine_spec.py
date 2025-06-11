"""Tests for the examine command handler."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from rich.console import Console
from rich.markdown import Markdown

from codebase_examiner.commands.examine import ExamineCommandHandler
from codebase_examiner.core.doc_generator import OutputFormat
from codebase_examiner.core.models import ExtractionResult, ModuleDocumentation


@pytest.fixture
def mock_inspector():
    """Mock the CodebaseInspector class."""
    with patch("codebase_examiner.commands.examine.CodebaseInspector") as mock_class:
        mock_instance = Mock()
        mock_class.return_value = mock_instance

        # Create a mock module for the result
        module_doc = ModuleDocumentation(
            name="test_module",
            docstring="Test module docstring.",
            file_path="/path/to/module.py",
            extractor_name="python",
            functions=[],
            classes=[],
        )

        # Create a mock ExtractionResult
        mock_result = ExtractionResult(
            extractors_used=["python"], file_count=1, data=[module_doc]
        )

        # Set up the mock instance to return our mock result
        mock_instance.inspect_directory.return_value = mock_result

        yield mock_class, mock_instance


@pytest.fixture
def mock_console():
    """Mock the Console class."""
    return Mock(spec=Console)


class DescribeExamineCommandHandler:
    """Tests for the ExamineCommandHandler."""

    def it_should_be_instantiated_with_console(self):
        """Test that ExamineCommandHandler can be instantiated with a console."""
        console = Console()

        handler = ExamineCommandHandler(console=console)

        assert isinstance(handler, ExamineCommandHandler)
        assert handler.console == console

    def it_should_handle_examine_command_with_default_options(self, mock_inspector, mock_console):
        """Test handling the examine command with default options."""
        mock_class, mock_instance = mock_inspector
        handler = ExamineCommandHandler(console=mock_console)

        result = handler.handle()

        assert result == 0
        mock_instance.inspect_directory.assert_called_once_with(
            directory=".",
            exclude_dirs={".venv", ".git"},
            exclude_dotfiles=True,
            include_test_files=False,
            use_gitignore=True,
        )
        mock_console.print.assert_any_call("[bold blue]Examining codebase in directory: .[/bold blue]")
        mock_console.print.assert_any_call("[bold]Finding and analyzing Python files...[/bold]")
        mock_console.print.assert_any_call("[bold]Generating markdown documentation...[/bold]")

    def it_should_handle_examine_command_with_custom_options(self, mock_inspector, mock_console):
        """Test handling the examine command with custom options."""
        mock_class, mock_instance = mock_inspector
        handler = ExamineCommandHandler(console=mock_console)

        result = handler.handle(
            directory="/custom/dir",
            output_format=OutputFormat.JSON,
            exclude=["node_modules"],
            include_dotfiles=True,
            include_test_files=True,
            use_gitignore=False,
        )

        assert result == 0
        mock_instance.inspect_directory.assert_called_once_with(
            directory="/custom/dir",
            exclude_dirs={"node_modules"},
            exclude_dotfiles=False,
            include_test_files=True,
            use_gitignore=False,
        )
        mock_console.print.assert_any_call("[bold blue]Examining codebase in directory: /custom/dir[/bold blue]")
        mock_console.print.assert_any_call("[bold]Generating json documentation...[/bold]")

    def it_should_write_to_output_file_when_specified(self, mock_inspector, mock_console, tmp_path):
        """Test that documentation is written to the output file when specified."""
        mock_class, mock_instance = mock_inspector
        handler = ExamineCommandHandler(console=mock_console)
        output_file = tmp_path / "output.md"

        with patch("codebase_examiner.commands.examine.generate_documentation", return_value="# Test Documentation"):
            result = handler.handle(output_file=str(output_file))

        assert result == 0
        assert output_file.exists()
        mock_console.print.assert_any_call(f"[bold green]Documentation written to {output_file}[/bold green]")

    def it_should_handle_custom_sections(self, mock_inspector, mock_console):
        """Test handling custom sections for markdown output."""
        mock_class, mock_instance = mock_inspector
        handler = ExamineCommandHandler(console=mock_console)

        with patch("codebase_examiner.commands.examine.generate_markdown_documentation", return_value="# Test Documentation"):
            result = handler.handle(sections=["title", "toc"])

        assert result == 0
        # Verify that the correct section generators were used
        mock_console.print.assert_any_call("[bold]Generating markdown documentation...[/bold]")

    def it_should_handle_errors_during_execution(self, mock_inspector, mock_console):
        """Test handling errors during execution."""
        mock_class, mock_instance = mock_inspector
        handler = ExamineCommandHandler(console=mock_console)

        # Make the inspect_directory method raise an exception
        mock_instance.inspect_directory.side_effect = Exception("Test error")

        result = handler.handle()

        assert result == 1
        mock_console.print.assert_any_call("[bold red]Error: Test error[/bold red]")

    def it_should_handle_unknown_section_error(self, mock_inspector, mock_console):
        """Test handling unknown section error."""
        mock_class, mock_instance = mock_inspector
        handler = ExamineCommandHandler(console=mock_console)

        # The handle method catches the KeyError and returns 1, so we need to check
        # that the error message is printed and the return value is 1
        result = handler.handle(sections=["unknown_section"])

        assert result == 1
        mock_console.print.assert_any_call("[bold red]Error: 'unknown_section'[/bold red]")
