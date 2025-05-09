"""Module for finding Python files in a directory structure."""

import os
import pathlib
from typing import List, Set


def find_python_files(
    directory: str = ".",
    exclude_dirs: Set[str] = None,
    exclude_dotfiles: bool = True,
) -> List[pathlib.Path]:
    """Find all Python files in the given directory and its subdirectories.

    Args:
        directory (str): The root directory to search in. Defaults to current directory.
        exclude_dirs (Set[str]): Set of directory names to exclude from the search.
            Defaults to {".venv", ".git", "__pycache__", "tests", "build", "dist"}.
        exclude_dotfiles (bool): Whether to exclude all files and directories starting with a dot.
            Defaults to True.

    Returns:
        List[pathlib.Path]: A list of paths to Python files.
    """
    if exclude_dirs is None:
        exclude_dirs = {".venv", ".git", "__pycache__", "tests", "build", "dist"}

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
                python_files.append(pathlib.Path(os.path.join(root, file)))

    return python_files