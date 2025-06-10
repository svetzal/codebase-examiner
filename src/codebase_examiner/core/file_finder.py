"""Module for finding Python files in a directory structure."""

import pathlib
import re
from typing import List, Set, Optional, Tuple

from codebase_examiner.core.filesystem_gateway import FileSystemGateway
from codebase_examiner.core.gitignore_parser import GitignoreParser


def parse_pytest_ini(
    directory: str, fs_gateway: Optional[FileSystemGateway] = None
) -> Tuple[Optional[Set[str]], Optional[List[str]]]:
    """Parse pytest.ini file to extract test file patterns and testpaths.

    Args:
        directory (str): The directory to search for pytest.ini.
        fs_gateway (Optional[FileSystemGateway]): The filesystem gateway to use.
            If None, a new instance will be created.

    Returns:
        Tuple[Optional[Set[str]], Optional[List[str]]]: A tuple containing:
            - A set of test file patterns (or None if not found)
            - A list of test paths (or None if not found)
    """
    if fs_gateway is None:
        fs_gateway = FileSystemGateway()

    pytest_ini_path = pathlib.Path(directory) / "pytest.ini"
    if not fs_gateway.path_exists(pytest_ini_path):
        return None, None

    config = fs_gateway.read_config(pytest_ini_path)

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


def is_test_file(
    file_path: pathlib.Path,
    test_patterns: Optional[Set[str]],
    fs_gateway: Optional[FileSystemGateway] = None,
) -> bool:
    """Check if a file is a test file based on pytest patterns.

    Args:
        file_path (pathlib.Path): The file path to check.
        test_patterns (Optional[Set[str]]): Set of regex patterns for test files.
        fs_gateway (Optional[FileSystemGateway]): The filesystem gateway to use.
            If None, a new instance will be created.

    Returns:
        bool: True if the file is a test file, False otherwise.
    """
    if fs_gateway is None:
        fs_gateway = FileSystemGateway()

    file_name = file_path.name

    if test_patterns is None:
        # Default patterns if none provided
        default_patterns = {r"test_.*\.py", r".*_test\.py", r".*_spec\.py"}
        for pattern in default_patterns:
            if re.match(pattern, file_name):
                return True
        return False

    for pattern in test_patterns:
        if re.match(pattern, file_name):
            return True
    return False


def find_python_files(
    directory: str = ".",
    exclude_dirs: Set[str] = None,
    exclude_dotfiles: bool = True,
    fs_gateway: Optional[FileSystemGateway] = None,
    include_test_files: bool = False,
    use_gitignore: bool = True,
) -> List[pathlib.Path]:
    """Find all Python files in the given directory and its subdirectories.

    This function automatically detects and respects pytest.ini configuration to identify
    test files based on the project's test organization strategy. It supports both:

    1. Traditional test organization with a separate 'tests' directory
    2. Tests alongside implementation files (e.g., module.py, module_test.py or module_spec.py)

    If a pytest.ini file is found, it will use the 'python_files' patterns to identify test files
    and the 'testpaths' to identify directories containing tests. If no pytest.ini is found,
    it will use default patterns (test_*.py, *_test.py, *_spec.py) to identify test files.

    By default, test files are excluded from the returned list to focus on implementation files.
    Set include_test_files=True to include test files in the results.

    If use_gitignore=True (the default), this function will also read the .gitignore file
    (if present) and exclude files and directories that match the patterns in it.

    This function also supports different project layouts:
    1. Standard Python package structure with code directly in the root directory
    2. Standard Python package structure with code in a 'src' directory
    3. Other custom layouts

    Args:
        directory (str): The root directory to search in. Defaults to current directory.
        exclude_dirs (Set[str]): Set of directory names to exclude from the search.
            Defaults to {".venv", ".git", "__pycache__", "tests", "build", "dist"}.
        exclude_dotfiles (bool): Whether to exclude all files and directories starting with a dot.
            Defaults to True.
        fs_gateway (Optional[FileSystemGateway]): The filesystem gateway to use.
            If None, a new instance will be created.
        include_test_files (bool): Whether to include test files in the results.
            Defaults to False.
        use_gitignore (bool): Whether to use .gitignore patterns for exclusion.
            Defaults to True.

    Returns:
        List[pathlib.Path]: A list of paths to Python files, optionally excluding test files.
    """
    if fs_gateway is None:
        fs_gateway = FileSystemGateway()

    if exclude_dirs is None:
        exclude_dirs = {".venv", ".git", "__pycache__", "tests", "build", "dist"}

    # Parse pytest.ini if it exists
    test_patterns, test_paths = parse_pytest_ini(directory, fs_gateway)

    # If testpaths are defined in pytest.ini, add them to exclude_dirs
    if test_paths:
        exclude_dirs = exclude_dirs.union(set(test_paths))

    # Parse .gitignore if requested
    gitignore_patterns = []
    gitignore_parser = None
    if use_gitignore:
        gitignore_parser = GitignoreParser(fs_gateway)
        gitignore_patterns = gitignore_parser.parse_gitignore(pathlib.Path(directory))

    python_files = []
    root_path = fs_gateway.resolve_path(pathlib.Path(directory))

    # Check if we're in the root directory of a project with a src directory
    src_dir = root_path / "src"
    if directory == "." and fs_gateway.path_exists(src_dir) and src_dir.is_dir():
        # If we're in the root directory and there's a src directory, also search in the src
        # directory
        src_files = find_python_files(
            directory=str(src_dir),
            exclude_dirs=exclude_dirs,
            exclude_dotfiles=exclude_dotfiles,
            fs_gateway=fs_gateway,
            include_test_files=include_test_files,
            use_gitignore=use_gitignore,
        )
        python_files.extend(src_files)

    # Prepare the exclude_dirs set with dotfiles if needed
    walk_exclude_dirs = exclude_dirs.copy() if exclude_dirs else set()

    # Add dotfiles to exclude_dirs if requested
    if exclude_dotfiles:
        # We can't know all dotfile directories in advance, so we'll filter them in the
        # walk_directory callback
        pass

    for root, dirs, files in fs_gateway.walk_directory(root_path, walk_exclude_dirs):
        # Skip directories starting with a dot if requested
        if exclude_dotfiles:
            dirs[:] = [d for d in dirs if not d.startswith(".")]

        # Skip directories that match gitignore patterns
        if gitignore_patterns and gitignore_parser:
            root_path_obj = pathlib.Path(root_path)
            dirs[:] = [
                d
                for d in dirs
                if not gitignore_parser.is_path_ignored(
                    fs_gateway.join_paths(root, d),
                    gitignore_patterns,
                    root_path_obj,
                    is_directory=True,
                )
            ]

        for file in files:
            # Skip files starting with a dot if requested
            if file.endswith(".py") and (
                not exclude_dotfiles or not file.startswith(".")
            ):
                file_path = fs_gateway.join_paths(root, file)

                # Skip files that match gitignore patterns
                if (
                    gitignore_patterns
                    and gitignore_parser
                    and gitignore_parser.is_path_ignored(
                        file_path, gitignore_patterns, root_path, is_directory=False
                    )
                ):
                    continue

                # Skip test files based on patterns from pytest.ini,
                # unless include_test_files is True
                if include_test_files or not is_test_file(
                    file_path, test_patterns, fs_gateway
                ):
                    python_files.append(file_path)

    return python_files
