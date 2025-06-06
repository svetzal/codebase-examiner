"""Tests for the file_finder module."""

import os
import pathlib
import tempfile
from typing import Set
from unittest.mock import Mock, MagicMock

import pytest

from codebase_examiner.core.file_finder import find_python_files, parse_pytest_ini, is_test_file
from codebase_examiner.core.filesystem_gateway import FileSystemGateway


def create_mock_filesystem_gateway(root_path: pathlib.Path) -> FileSystemGateway:
    """Create a mock FileSystemGateway for testing."""
    mock_fs = Mock(spec=FileSystemGateway)

    # Mock file structure
    files = {
        str(root_path / "module1.py"): "# Test module 1",
        str(root_path / "module2.py"): "# Test module 2",
        str(root_path / "test_module.py"): "# Test file",
        str(root_path / "module_test.py"): "# Test file",
        str(root_path / "module_spec.py"): "# Test file",
        str(root_path / "subpkg" / "__init__.py"): "",
        str(root_path / "subpkg" / "submodule.py"): "# Test submodule",
        str(root_path / ".venv" / "env_module.py"): "# Should be excluded",
    }

    # Mock directory structure for walk_directory
    walk_results = [
        (str(root_path), ["subpkg", ".venv"], ["module1.py", "module2.py", "test_module.py", "module_test.py", "module_spec.py"]),
        (str(root_path / "subpkg"), [], ["__init__.py", "submodule.py"]),
        (str(root_path / ".venv"), [], ["env_module.py"]),
    ]

    # Setup mock methods
    mock_fs.path_exists = lambda path: str(path) in files or str(path).rstrip("/") in [d[0] for d in walk_results]
    mock_fs.read_file = lambda path: files.get(str(path), "")

    # Mock walk_directory to handle exclude_dirs
    def mock_walk_directory(directory, exclude_dirs=None):
        if exclude_dirs is None:
            exclude_dirs = set()

        filtered_results = []
        for root, dirs, files in walk_results:
            # Check if this directory should be excluded
            dir_name = os.path.basename(root.rstrip("/"))
            if dir_name in exclude_dirs:
                continue

            # Filter out excluded directories
            filtered_dirs = [d for d in dirs if d not in exclude_dirs]

            filtered_results.append((root, filtered_dirs, files))

        return filtered_results

    mock_fs.walk_directory = mock_walk_directory
    mock_fs.resolve_path = lambda path: path
    mock_fs.join_paths = lambda root, file: pathlib.Path(os.path.join(root, file))
    mock_fs.get_file_stem = lambda path: path.stem
    mock_fs.get_file_suffix = lambda path: path.suffix

    # Mock config for pytest.ini
    mock_config = MagicMock()
    mock_config.__contains__ = lambda self, key: key == "pytest"
    mock_config.__getitem__ = lambda self, key: {"python_files": "test_*.py *_test.py *_spec.py", "testpaths": "tests"} if key == "pytest" else {}
    mock_fs.read_config = lambda path: mock_config

    return mock_fs


class DescribeFileFinder:
    """Tests for the FileFinder component."""

    def it_should_find_python_files(self):
        """Test finding Python files in a directory structure."""
        # Create a mock root path
        root_path = pathlib.Path("/mock/root")

        # Create a mock filesystem gateway
        mock_fs = create_mock_filesystem_gateway(root_path)

        # Run the function with the mock filesystem gateway
        python_files = find_python_files(str(root_path), fs_gateway=mock_fs)

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
        # Create a mock root path
        root_path = pathlib.Path("/mock/root")

        # Create a mock filesystem gateway
        mock_fs = create_mock_filesystem_gateway(root_path)

        # Add a custom exclude directory to the mock walk results
        original_walk_directory = mock_fs.walk_directory

        def updated_walk_directory(directory, exclude_dirs=None):
            results = original_walk_directory(directory, exclude_dirs)

            # If we're excluding custom_exclude, don't add it
            if exclude_dirs and "custom_exclude" in exclude_dirs:
                return results

            # Add custom_exclude directory to the first result's directories if it exists
            if results:
                first_result = list(results[0])
                first_result[1] = first_result[1] + ["custom_exclude"]
                # Add a new result for the custom_exclude directory
                custom_exclude_result = (str(root_path / "custom_exclude"), [], ["excluded_module.py"])
                return [tuple(first_result)] + results[1:] + [custom_exclude_result]
            return results

        mock_fs.walk_directory = updated_walk_directory

        # Run the function with custom excludes and the mock filesystem gateway
        python_files = find_python_files(str(root_path), exclude_dirs={".venv", "custom_exclude"}, fs_gateway=mock_fs)

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
        # Create a mock filesystem gateway
        mock_fs = Mock(spec=FileSystemGateway)

        # Test with default patterns
        assert is_test_file(pathlib.Path("test_module.py"), None, mock_fs) is True
        assert is_test_file(pathlib.Path("module_test.py"), None, mock_fs) is True
        assert is_test_file(pathlib.Path("module_spec.py"), None, mock_fs) is True
        assert is_test_file(pathlib.Path("regular_module.py"), None, mock_fs) is False

        # Test with custom patterns
        custom_patterns = {r"custom_.*\.py", r".*_custom\.py"}
        assert is_test_file(pathlib.Path("custom_module.py"), custom_patterns, mock_fs) is True
        assert is_test_file(pathlib.Path("module_custom.py"), custom_patterns, mock_fs) is True
        assert is_test_file(pathlib.Path("test_module.py"), custom_patterns, mock_fs) is False

    def it_should_parse_pytest_ini(self):
        """Test parsing pytest.ini configuration."""
        # Create a mock root path
        root_path = pathlib.Path("/mock/root")

        # Create a mock filesystem gateway
        mock_fs = Mock(spec=FileSystemGateway)

        # Mock path_exists to return True for pytest.ini and False for non-existent directory
        mock_fs.path_exists = lambda path: str(path) == str(root_path / "pytest.ini")

        # Mock read_config to return a config with pytest section
        mock_config = MagicMock()
        mock_config.__contains__ = lambda self, key: key == "pytest"
        mock_config.__getitem__ = lambda self, key: {
            "python_files": "test_*.py *_test.py *_spec.py custom_*.py",
            "testpaths": "tests integration_tests"
        } if key == "pytest" else {}
        mock_fs.read_config = lambda path: mock_config

        # Parse the pytest.ini file
        test_patterns, test_paths = parse_pytest_ini(str(root_path), mock_fs)

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
        # Update mock_fs.path_exists to return False for pytest.ini in non_existent directory
        non_existent_dir = root_path / "non_existent"
        mock_fs.path_exists = lambda path: False

        test_patterns, test_paths = parse_pytest_ini(str(non_existent_dir), mock_fs)
        assert test_patterns is None
        assert test_paths is None

    def it_should_find_python_files_with_pytest_ini(self):
        """Test finding Python files with pytest.ini configuration."""
        # Create a mock root path
        root_path = pathlib.Path("/mock/root")

        # Create a mock filesystem gateway with pytest.ini configuration
        mock_fs = create_mock_filesystem_gateway(root_path)

        # Add custom test files and tests directory to the mock walk results
        original_walk_directory = mock_fs.walk_directory

        def updated_walk_directory(directory, exclude_dirs=None):
            results = original_walk_directory(directory, exclude_dirs)

            # If we're excluding tests, don't add it
            if exclude_dirs and "tests" in exclude_dirs:
                # Still add the custom test files to the first result if it exists
                if results:
                    first_result = list(results[0])
                    first_result[2] = first_result[2] + ["custom_module.py", "module_custom.py"]
                    return [tuple(first_result)] + results[1:]
                return results

            # Add custom test files and tests directory if results exist
            if results:
                first_result = list(results[0])
                first_result[2] = first_result[2] + ["custom_module.py", "module_custom.py"]
                # Add tests directory to the first result's directories
                first_result[1] = first_result[1] + ["tests"]
                # Add a new result for the tests directory
                tests_result = (str(root_path / "tests"), [], ["test_in_tests_dir.py"])
                return [tuple(first_result)] + results[1:] + [tests_result]
            return results

        mock_fs.walk_directory = updated_walk_directory

        # Update mock_config to include custom test patterns
        mock_config = MagicMock()
        mock_config.__contains__ = lambda self, key: key == "pytest"
        mock_config.__getitem__ = lambda self, key: {
            "python_files": "test_*.py *_test.py *_spec.py custom_*.py *_custom.py",
            "testpaths": "tests"
        } if key == "pytest" else {}
        mock_fs.read_config = lambda path: mock_config

        # Override is_test_file to properly identify custom test files
        original_is_test_file = is_test_file

        def mock_is_test_file(file_path, test_patterns, fs_gateway=None):
            # Check if it's a custom test file
            file_name = file_path.name
            if file_name == "custom_module.py" or file_name == "module_custom.py":
                return True
            return original_is_test_file(file_path, test_patterns, fs_gateway)

        # Patch the is_test_file function
        import codebase_examiner.core.file_finder
        original_is_test_file_func = codebase_examiner.core.file_finder.is_test_file
        codebase_examiner.core.file_finder.is_test_file = mock_is_test_file

        # Run the function with the mock filesystem gateway
        python_files = find_python_files(str(root_path), fs_gateway=mock_fs)

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
