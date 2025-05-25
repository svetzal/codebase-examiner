"""Tests for the CLI module."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from codebase_examiner.cli import app
from codebase_examiner.core.code_inspector import ModuleDocumentation


@pytest.fixture
def runner():
    """Return a Typer CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_inspector():
    """Mock the CodebaseInspector class."""
    with patch("codebase_examiner.cli.CodebaseInspector") as mock_class:
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        
        # Create a mock module for the result
        from codebase_examiner.core.models import ExtractionResult, ModuleDocumentation
        module_doc = ModuleDocumentation(
            name="test_module",
            docstring="Test module docstring.",
            file_path="/path/to/module.py",
            extractor_name="python",
            functions=[],
            classes=[]
        )
        
        # Create a mock ExtractionResult
        mock_result = ExtractionResult(
            extractors_used=["python"],
            file_count=1,
            data=[module_doc]
        )
        
        # Set up the mock instance to return our mock result
        mock_instance.inspect_directory.return_value = mock_result
        
        yield mock_class, mock_instance


class DescribeCLI:
    """Tests for the CLI component."""
    
    def it_should_execute_examine_command(self, runner, mock_inspector):
        """Test the examine command."""
        mock_class, mock_instance = mock_inspector
        
        # Test with default options (output to console, markdown format)
        result = runner.invoke(app, ["examine"])
        
        assert result.exit_code == 0
        assert "Examining codebase in directory: ." in result.stdout
        assert "Finding and analyzing Python files..." in result.stdout
        assert "Generating markdown documentation..." in result.stdout
        assert "# Codebase Documentation" in result.stdout

        # Check that the function was called with the right arguments
        mock_instance.inspect_directory.assert_called_once_with(
            directory=".", 
            exclude_dirs={".venv"},
            exclude_dotfiles=True
        )

    def it_should_support_json_format(self, runner, mock_inspector):
        """Test the examine command with format option."""
        mock_class, mock_instance = mock_inspector
        
        # Test with JSON format
        result = runner.invoke(app, ["examine", "--format", "json"])
        
        assert result.exit_code == 0
        assert "Generating json documentation..." in result.stdout

        # Verify that JSON output can be parsed
        output = result.stdout
        start_idx = output.find("JSON_OUTPUT_START") + len("JSON_OUTPUT_START")
        end_idx = output.find("JSON_OUTPUT_END")
        json_output = output[start_idx:end_idx].strip()
        json_data = json.loads(json_output)
        assert isinstance(json_data, list)
        assert len(json_data) == 1
        assert json_data[0]["name"] == "test_module"

    def it_should_write_to_output_file(self, runner, mock_inspector):
        """Test the examine command with output file."""
        mock_class, mock_instance = mock_inspector
        
        with tempfile.TemporaryDirectory() as tmpdirname:
            output_file = Path(tmpdirname) / "output.md"

            # Run the command with output file
            result = runner.invoke(app, ["examine", "--output", str(output_file)])
            
            assert result.exit_code == 0
            assert f"Documentation written to {output_file}" in result.stdout

            # Verify the file was created
            assert output_file.exists()
            content = output_file.read_text()
            assert "# Codebase Documentation" in content
