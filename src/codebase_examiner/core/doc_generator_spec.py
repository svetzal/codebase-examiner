"""Tests for the doc_generator module."""

import json

import pytest

from codebase_examiner.core.doc_generator import (
    generate_markdown_documentation,
    generate_json_documentation,
    generate_documentation,
)
from codebase_examiner.core.extractors.base import Capability
from codebase_examiner.core.models import (
    ModuleDocumentation,
    ClassDocumentation,
    FunctionDocumentation,
    ExtractionResult,
)


@pytest.fixture
def test_modules():
    """Create test module documentation for testing."""
    # Create function documentation
    func_doc = FunctionDocumentation(
        name="test_function",
        docstring="Test function docstring.",
        signature="(param1: int, param2: str = 'default') -> bool",
        parameters={
            "param1": {
                "kind": "POSITIONAL_OR_KEYWORD",
                "default": None,
                "annotation": "int",
                "description": "The first parameter.",
            },
            "param2": {
                "kind": "POSITIONAL_OR_KEYWORD",
                "default": "'default'",
                "annotation": "str",
                "description": "The second parameter.",
            },
        },
        return_type="bool",
        return_description="True if successful, False otherwise.",
        module_path="/path/to/module.py",
        file_path="/path/to/module.py",
        extractor_name="python",
        capability=Capability.CODE_STRUCTURE,
    )

    # Create class documentation
    class_doc = ClassDocumentation(
        name="TestClass",
        docstring="Test class docstring.",
        methods=[
            FunctionDocumentation(
                name="__init__",
                docstring="Initialize the TestClass.",
                signature="(self, value: int)",
                parameters={
                    "self": {
                        "kind": "POSITIONAL_OR_KEYWORD",
                        "default": None,
                        "annotation": None,
                        "description": None,
                    },
                    "value": {
                        "kind": "POSITIONAL_OR_KEYWORD",
                        "default": None,
                        "annotation": "int",
                        "description": "The initial value.",
                    },
                },
                return_type=None,
                return_description=None,
                module_path="/path/to/module.py",
                file_path="/path/to/module.py",
                extractor_name="python",
                capability=Capability.CODE_STRUCTURE,
            ),
            FunctionDocumentation(
                name="test_method",
                docstring="Test method docstring.",
                signature="(self, factor: float) -> float",
                parameters={
                    "self": {
                        "kind": "POSITIONAL_OR_KEYWORD",
                        "default": None,
                        "annotation": None,
                        "description": None,
                    },
                    "factor": {
                        "kind": "POSITIONAL_OR_KEYWORD",
                        "default": None,
                        "annotation": "float",
                        "description": "The factor to multiply by.",
                    },
                },
                return_type="float",
                return_description="The result of the calculation.",
                module_path="/path/to/module.py",
                file_path="/path/to/module.py",
                extractor_name="python",
                capability=Capability.CODE_STRUCTURE,
            ),
        ],
        module_path="/path/to/module.py",
        file_path="/path/to/module.py",
        extractor_name="python",
        capability=Capability.CODE_STRUCTURE,
    )

    # Create module documentation
    module_doc = ModuleDocumentation(
        name="test_module",
        docstring="Test module docstring.",
        file_path="/path/to/module.py",
        functions=[func_doc],
        classes=[class_doc],
        extractor_name="python",
        capability=Capability.CODE_STRUCTURE,
    )

    return [module_doc]


@pytest.fixture
def test_extraction_result(test_modules):
    """Create test extraction result for testing."""
    return ExtractionResult(extractors_used=["python"], file_count=1, data=test_modules)


class DescribeDocGenerator:
    """Tests for the DocGenerator component."""

    def it_should_generate_markdown_documentation(self, test_modules):
        """Test generating markdown documentation."""
        markdown = generate_markdown_documentation(test_modules)

        # Basic checks for the markdown output
        assert "# Codebase Documentation" in markdown
        assert "## Table of Contents" in markdown
        assert "## Module: test_module" in markdown
        assert "### Functions" in markdown
        assert "#### `test_function" in markdown
        assert "**Parameters:**" in markdown
        assert "- `param1` (int):" in markdown
        assert "- `param2` (str), default: `'default'`:" in markdown
        assert "**Returns:**" in markdown
        assert "(bool) True if successful, False otherwise." in markdown
        assert "### Classes" in markdown
        assert "#### `TestClass`" in markdown
        assert "**Methods:**" in markdown
        assert "##### `__init__" in markdown
        assert "##### `test_method" in markdown

    def it_should_generate_json_documentation(self, test_modules):
        """Test generating JSON documentation."""
        json_str = generate_json_documentation(test_modules)

        # Parse the JSON and verify structure
        json_data = json.loads(json_str)
        assert isinstance(json_data, list)
        assert len(json_data) == 1

        module = json_data[0]
        assert module["name"] == "test_module"
        assert module["docstring"] == "Test module docstring."
        assert module["file_path"] == "/path/to/module.py"

        assert len(module["functions"]) == 1
        function = module["functions"][0]
        assert function["name"] == "test_function"
        assert len(function["parameters"]) == 2

        assert len(module["classes"]) == 1
        cls = module["classes"][0]
        assert cls["name"] == "TestClass"
        assert len(cls["methods"]) == 2

    def it_should_generate_documentation(self, test_modules):
        """Test the main generate_documentation function."""
        # Test markdown format
        markdown = generate_documentation(test_modules, "markdown")
        assert "# Codebase Documentation" in markdown

        # Test JSON format
        json_str = generate_documentation(test_modules, "json")
        json_data = json.loads(json_str)
        assert isinstance(json_data, list)
        assert len(json_data) == 1

    def it_should_support_custom_sections(self, test_modules):
        """Test generating markdown documentation with custom sections."""
        # Import section generators
        from codebase_examiner.core.section_generators import (
            TitleSection,
            ModulesSection,
        )

        # Generate only title and modules sections
        markdown = generate_markdown_documentation(
            test_modules, sections=[TitleSection(), ModulesSection()]
        )

        # Should include title and modules, but not table of contents
        assert markdown.startswith("# Codebase Documentation")
        assert "## Table of Contents" not in markdown
        assert "## Module: test_module" in markdown

    def it_should_handle_extraction_result(self, test_extraction_result):
        """Test handling ExtractionResult objects."""
        # Test markdown format
        markdown = generate_documentation(test_extraction_result, "markdown")
        assert "# Codebase Documentation" in markdown
        assert "## Module: test_module" in markdown

        # Test JSON format
        json_str = generate_documentation(test_extraction_result, "json")
        json_data = json.loads(json_str)
        assert isinstance(json_data, list)
        assert len(json_data) == 1
