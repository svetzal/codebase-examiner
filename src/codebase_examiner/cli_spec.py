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
def mock_inspect_codebase():
    """Mock the inspect_codebase function."""
    with patch("codebase_examiner.cli.inspect_codebase") as mock:
        # Create a simple mock module
        module_doc = ModuleDocumentation(
            name="test_module",
            docstring="Test module docstring.",
            file_path="/path/to/module.py",
            functions=[],
            classes=[]
        )
        mock.return_value = [module_doc]
        yield mock


class DescribeCLI:
    """Tests for the CLI component."""
    
    def it_should_execute_examine_command(self, runner, mock_inspect_codebase):
        """Test the examine command."""
        # Test with default options (output to console, markdown format)
        result = runner.invoke(app, ["examine"])
        
        assert result.exit_code == 0
        assert "Examining codebase in directory: ." in result.stdout
        assert "Finding and analyzing Python files..." in result.stdout
        assert "Generating markdown documentation..." in result.stdout
        assert "# Codebase Documentation" in result.stdout

        # Check that the function was called with the right arguments
        mock_inspect_codebase.assert_called_once_with(".", {".venv"})

    def it_should_support_json_format(self, runner, mock_inspect_codebase):
        """Test the examine command with format option."""
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

    def it_should_write_to_output_file(self, runner, mock_inspect_codebase):
        """Test the examine command with output file."""
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
