"""Tests for the file_finder module."""

import os
import pathlib
import tempfile
from typing import Set

import pytest

from codebase_examiner.core.file_finder import find_python_files, parse_pytest_ini, is_test_file


def create_test_file_structure(root_path: pathlib.Path) -> None:
    """Create a test file structure for testing."""
    # Create a few Python files
    (root_path / "module1.py").write_text("# Test module 1")
    (root_path / "module2.py").write_text("# Test module 2")

    # Create test files with different naming patterns
    (root_path / "test_module.py").write_text("# Test file")
    (root_path / "module_test.py").write_text("# Test file")
    (root_path / "module_spec.py").write_text("# Test file")

    # Create a subdirectory with Python files
    subdir = root_path / "subpkg"
    subdir.mkdir()
    (subdir / "__init__.py").write_text("")
    (subdir / "submodule.py").write_text("# Test submodule")

    # Create an excluded directory with Python files
    venv_dir = root_path / ".venv"
    venv_dir.mkdir()
    (venv_dir / "env_module.py").write_text("# Should be excluded")


class DescribeFileFinder:
    """Tests for the FileFinder component."""
    
    def it_should_find_python_files(self):
        """Test finding Python files in a directory structure."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Create test file structure
            root_path = pathlib.Path(tmpdirname)
            create_test_file_structure(root_path)

            # Run the function
            python_files = find_python_files(tmpdirname)

            # Get file names for easier assertions
            file_names = [path.name for path in python_files]

            # Verify results
            assert len(python_files) == 4
            assert "module1.py" in file_names
            assert "module2.py" in file_names
            assert "__init__.py" in file_names
            assert "submodule.py" in file_names

            # Test files should be excluded
            assert "test_module.py" not in file_names
            assert "module_test.py" not in file_names
            assert "module_spec.py" not in file_names
            assert "env_module.py" not in file_names  # Should be excluded

    def it_should_find_python_files_with_custom_excludes(self):
        """Test finding Python files with custom excludes."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Create test file structure
            root_path = pathlib.Path(tmpdirname)
            create_test_file_structure(root_path)

            # Create an additional directory that we'll exclude
            custom_exclude_dir = root_path / "custom_exclude"
            custom_exclude_dir.mkdir()
            (custom_exclude_dir / "excluded_module.py").write_text("# Should be excluded")

            # Run the function with custom excludes
            python_files = find_python_files(tmpdirname, exclude_dirs={".venv", "custom_exclude"})

            # Get file names for easier assertions
            file_names = [path.name for path in python_files]

            # Verify results
            assert len(python_files) == 4
            assert "module1.py" in file_names
            assert "module2.py" in file_names
            assert "__init__.py" in file_names
            assert "submodule.py" in file_names

            # Test files should be excluded
            assert "test_module.py" not in file_names
            assert "module_test.py" not in file_names
            assert "module_spec.py" not in file_names
            assert "env_module.py" not in file_names  # Should be excluded
            assert "excluded_module.py" not in file_names  # Should be excluded by custom rule

    def it_should_identify_test_files(self):
        """Test identifying test files based on patterns."""
        # Test with default patterns
        assert is_test_file(pathlib.Path("test_module.py"), None) is True
        assert is_test_file(pathlib.Path("module_test.py"), None) is True
        assert is_test_file(pathlib.Path("module_spec.py"), None) is True
        assert is_test_file(pathlib.Path("regular_module.py"), None) is False

        # Test with custom patterns
        custom_patterns = {r"custom_.*\.py", r".*_custom\.py"}
        assert is_test_file(pathlib.Path("custom_module.py"), custom_patterns) is True
        assert is_test_file(pathlib.Path("module_custom.py"), custom_patterns) is True
        assert is_test_file(pathlib.Path("test_module.py"), custom_patterns) is False

    def it_should_parse_pytest_ini(self):
        """Test parsing pytest.ini configuration."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            root_path = pathlib.Path(tmpdirname)

            # Create a pytest.ini file with custom configuration
            pytest_ini_content = """
[pytest]
python_files = test_*.py *_test.py *_spec.py custom_*.py
testpaths = tests integration_tests
"""
            (root_path / "pytest.ini").write_text(pytest_ini_content)

            # Parse the pytest.ini file
            test_patterns, test_paths = parse_pytest_ini(tmpdirname)

            # Verify test patterns
            assert test_patterns is not None
            assert len(test_patterns) == 4
            assert r"test_.*\.py" in test_patterns
            assert r".*_test\.py" in test_patterns
            assert r".*_spec\.py" in test_patterns
            assert r"custom_.*\.py" in test_patterns

            # Verify test paths
            assert test_paths is not None
            assert len(test_paths) == 2
            assert "tests" in test_paths
            assert "integration_tests" in test_paths

            # Test with non-existent pytest.ini
            non_existent_dir = root_path / "non_existent"
            non_existent_dir.mkdir()
            test_patterns, test_paths = parse_pytest_ini(str(non_existent_dir))
            assert test_patterns is None
            assert test_paths is None

    def it_should_find_python_files_with_pytest_ini(self):
        """Test finding Python files with pytest.ini configuration."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Create test file structure
            root_path = pathlib.Path(tmpdirname)
            create_test_file_structure(root_path)

            # Create additional test files with custom patterns
            (root_path / "custom_module.py").write_text("# Custom test file")
            (root_path / "module_custom.py").write_text("# Custom test file")

            # Create a pytest.ini file with custom configuration
            pytest_ini_content = """
[pytest]
python_files = test_*.py *_test.py *_spec.py custom_*.py *_custom.py
testpaths = tests
"""
            (root_path / "pytest.ini").write_text(pytest_ini_content)

            # Create a tests directory that should be excluded
            tests_dir = root_path / "tests"
            tests_dir.mkdir()
            (tests_dir / "test_in_tests_dir.py").write_text("# Test in tests dir")

            # Run the function
            python_files = find_python_files(tmpdirname)

            # Get file names for easier assertions
            file_names = [path.name for path in python_files]

            # Verify results
            assert len(python_files) == 4
            assert "module1.py" in file_names
            assert "module2.py" in file_names
            assert "__init__.py" in file_names
            assert "submodule.py" in file_names

            # Test files should be excluded based on pytest.ini patterns
            assert "test_module.py" not in file_names
            assert "module_test.py" not in file_names
            assert "module_spec.py" not in file_names
            assert "custom_module.py" not in file_names
            assert "module_custom.py" not in file_names

            # Files in testpaths should be excluded
            assert "test_in_tests_dir.py" not in file_names
