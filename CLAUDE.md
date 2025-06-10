# Codebase Examiner - Agent Guidelines

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Codebase Examiner is a command-line tool and MCP server that analyzes Python codebases to generate comprehensive documentation. The tool scans Python files to extract information about modules, classes, functions, and their documentation, then outputs structured documentation in markdown or JSON format.

Key features:
- Find all Python files in a project directory tree (excluding .venv and other configurable directories)
- Automatically detect and respect .gitignore patterns for file exclusion
- Extract documentation from modules, classes, and functions
- Parse Google-style docstrings for parameter and return value documentation
- Generate documentation in Markdown or JSON format
- Run as a CLI tool, MCP over HTTP, or MCP over STDIO

Users can install it with pipx to make "codebase-examiner" available as a command-line tool.

## Code Organization

### Import Structure
1. Imports should be grouped in the following order, with one blank line between groups:
   - Standard library imports
   - Third-party library imports
   - Local application imports
2. Within each group, imports should be sorted alphabetically

### Naming Conventions
1. Use descriptive variable names that indicate the purpose or content
2. Prefix test mock objects with 'mock_' (e.g., mock_memory)
3. Prefix test data variables with 'test_' (e.g., test_query)
4. Use '_' for unused variables or return values

### Type Hints and Documentation
1. Use type hints for method parameters and class dependencies
2. Include return type hints when the return type isn't obvious
3. Use docstrings for methods that aren't self-explanatory
4. Class docstrings should describe the purpose and behavior of the component
5. Follow Google-style docstrings (consistent with existing code)

### Logging Conventions
1. Use structlog for all logging
2. Initialize logger at module level using `logger = structlog.get_logger()`
3. Include relevant context data in log messages
4. Use appropriate log levels:
   - INFO for normal operations
   - DEBUG for detailed information
   - WARNING for concerning but non-critical issues
   - ERROR for critical issues
5. Use print statements only for direct user feedback

### Code Conventions
1. Do not write comments that just restate what the code does
2. Use pydantic BaseModel classes, do not use @dataclass
3. This project should use a pyproject.toml file and not a requirements.txt file for project requirements

## Testing Guidelines

### General Rules
1. Use pytest for all testing
2. Test files:
   - Named with prefix `test_` (e.g., test_file_finder.py)
   - Located in the tests directory, mirroring the src structure
3. Code style:
   - Max line length: 100 (as set in pyproject.toml)
   - Max complexity: 10
4. Run tests with: `pytest`
5. Run linting with: `flake8 src`

### BDD-Style Tests
We follow a Behavior-Driven Development (BDD) style using the "Describe/should" pattern to make tests readable and focused on component behavior.

#### Test Structure
1. Tests are organized in classes that start with "Describe" followed by the component name
2. Test methods:
   - Start with "should_"
   - Describe the expected behavior in plain English
   - Follow the Arrange/Act/Assert pattern (separated by blank lines)
3. Do not use comments (eg Arrange, Act, Assert) to delineate test sections - just use a blank line
4. No conditional statements in tests - each test should fail for only one clear reason
5. Do not test private methods directly (those starting with '_') - test through the public API

#### Fixtures and Mocking
1. Use pytest @fixture for test prerequisites:
   - Break large fixtures into smaller, reusable ones
   - Place fixtures in module scope for sharing between classes
   - Place module-level fixtures at the top of the file
2. Mocking:
   - Use pytest's `mocker` for dependencies
   - Use Mock's spec parameter for type safety (e.g., `Mock(spec=SmartMemory)`)
   - Only mock our own gateway classes
   - Do not mock library internals or private functions
   - Do not use unittest or MagicMock directly

#### Best Practices
1. Test organization:
   - Place instantiation/initialization tests first
   - Group related scenarios together (success and failure cases)
   - Keep tests focused on single behaviors
2. Assertions:
   - One assertion per line for better error identification
   - Use 'in' operator for partial string matches
   - Use '==' for exact matches
3. Test data:
   - Use fixtures for reusable prerequisites
   - Define complex test data structures within test methods

### Example Test
```python
class DescribeSmartMemory:
    """
    Tests for the SmartMemory component which handles memory operations
    """
    def should_be_instantiated_with_chroma_gateway(self):
        mock_chroma_gateway = Mock(spec=ChromaGateway)

        memory = SmartMemory(mock_chroma_gateway)

        assert isinstance(memory, SmartMemory)
        assert memory.chroma == mock_chroma_gateway
```

## Release Process

This project follows [Semantic Versioning](https://semver.org/) (SemVer) for version numbering. The version format is MAJOR.MINOR.PATCH, where:

1. MAJOR version increases for incompatible API changes
2. MINOR version increases for backward-compatible functionality additions
3. PATCH version increases for backward-compatible bug fixes

### Preparing a Release

When preparing a release, follow these steps:

1. **Update CHANGELOG.md**:
   - Move items from the "[Next]" section to a new version section
   - Add the new version number and release date: `## [x.y.z] - YYYY-MM-DD`
   - Ensure all changes are properly categorized under "Added", "Changed", "Deprecated", "Removed", "Fixed", or "Security"
   - Keep the empty "[Next]" section at the top for future changes

2. **Update Version Number**:
   - Update the version number in `pyproject.toml`
   - Ensure the version number follows semantic versioning principles based on the nature of changes:
     - **Major Release**: Breaking changes that require users to modify their code
     - **Minor Release**: New features that don't break backward compatibility
     - **Patch Release**: Bug fixes that don't add features or break compatibility

3. **Update Documentation**:
   - Review and update `README.md` to reflect any new features, changed behavior, or updated requirements
   - Update any other documentation files that reference features or behaviors that have changed
   - Ensure installation instructions and examples are up to date

4. **Final Verification**:
   - Run all tests to ensure they pass
   - Verify that the application works as expected with the updated version
   - Check that all documentation accurately reflects the current state of the project
