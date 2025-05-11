"""Module for finding Python files in a directory structure."""

import configparser
import os
import pathlib
import re
from typing import List, Set, Optional, Tuple


def parse_pytest_ini(directory: str) -> Tuple[Optional[Set[str]], Optional[List[str]]]:
    """Parse pytest.ini file to extract test file patterns and testpaths.

    Args:
        directory (str): The directory to search for pytest.ini.

    Returns:
        Tuple[Optional[Set[str]], Optional[List[str]]]: A tuple containing:
            - A set of test file patterns (or None if not found)
            - A list of test paths (or None if not found)
    """
    pytest_ini_path = pathlib.Path(directory) / "pytest.ini"
    if not pytest_ini_path.exists():
        return None, None

    config = configparser.ConfigParser()
    config.read(pytest_ini_path)

    if "pytest" not in config:
        return None, None

    # Extract test file patterns
    test_patterns = set()
    if "python_files" in config["pytest"]:
        patterns = config["pytest"]["python_files"].strip().split()
        for pattern in patterns:
            # Convert glob patterns to regex patterns
            if pattern.startswith("test_") and pattern.endswith(".py"):
                regex_pattern = r"test_.*\.py"
            elif pattern.endswith("_test.py"):
                regex_pattern = r".*_test\.py"
            elif pattern.endswith("_spec.py"):
                regex_pattern = r".*_spec\.py"
            elif pattern.startswith("custom_") and pattern.endswith(".py"):
                regex_pattern = r"custom_.*\.py"
            elif pattern.endswith("_custom.py"):
                regex_pattern = r".*_custom\.py"
            else:
                # Generic conversion
                regex_pattern = pattern.replace("*", ".*").replace(".", "\\.")
            test_patterns.add(regex_pattern)

    # Extract test paths
    test_paths = None
    if "testpaths" in config["pytest"]:
        test_paths = config["pytest"]["testpaths"].strip().split()

    return test_patterns, test_paths


def is_test_file(file_path: pathlib.Path, test_patterns: Optional[Set[str]]) -> bool:
    """Check if a file is a test file based on pytest patterns.

    Args:
        file_path (pathlib.Path): The file path to check.
        test_patterns (Optional[Set[str]]): Set of regex patterns for test files.

    Returns:
        bool: True if the file is a test file, False otherwise.
    """
    if test_patterns is None:
        # Default patterns if none provided
        default_patterns = {r"test_.*\.py", r".*_test\.py", r".*_spec\.py"}
        for pattern in default_patterns:
            if re.match(pattern, file_path.name):
                return True
        return False

    for pattern in test_patterns:
        if re.match(pattern, file_path.name):
            return True
    return False


def find_python_files(
        directory: str = ".",
        exclude_dirs: Set[str] = None,
        exclude_dotfiles: bool = True,
) -> List[pathlib.Path]:
    """Find all Python files in the given directory and its subdirectories.

    This function automatically detects and respects pytest.ini configuration to identify
    test files based on the project's test organization strategy. It supports both:

    1. Traditional test organization with a separate 'tests' directory
    2. Tests alongside implementation files (e.g., module.py, module_test.py or module_spec.py)

    If a pytest.ini file is found, it will use the 'python_files' patterns to identify test files
    and the 'testpaths' to identify directories containing tests. If no pytest.ini is found,
    it will use default patterns (test_*.py, *_test.py, *_spec.py) to identify test files.

    Test files are excluded from the returned list to focus on implementation files.

    Args:
        directory (str): The root directory to search in. Defaults to current directory.
        exclude_dirs (Set[str]): Set of directory names to exclude from the search.
            Defaults to {".venv", ".git", "__pycache__", "tests", "build", "dist"}.
        exclude_dotfiles (bool): Whether to exclude all files and directories starting with a dot.
            Defaults to True.

    Returns:
        List[pathlib.Path]: A list of paths to Python files, excluding test files.
    """
    if exclude_dirs is None:
        exclude_dirs = {".venv", ".git", "__pycache__", "tests", "build", "dist"}

    # Parse pytest.ini if it exists
    test_patterns, test_paths = parse_pytest_ini(directory)

    # If testpaths are defined in pytest.ini, add them to exclude_dirs
    if test_paths:
        exclude_dirs = exclude_dirs.union(set(test_paths))

    python_files = []
    root_path = pathlib.Path(directory).resolve()

    for root, dirs, files in os.walk(root_path):
        # Skip excluded directories and directories starting with a dot if requested
        if exclude_dotfiles:
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        else:
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            # Skip files starting with a dot if requested
            if file.endswith(".py") and (not exclude_dotfiles or not file.startswith('.')):
                file_path = pathlib.Path(os.path.join(root, file))

                # Skip test files based on patterns from pytest.ini
                if not is_test_file(file_path, test_patterns):
                    python_files.append(file_path)

    return python_files
