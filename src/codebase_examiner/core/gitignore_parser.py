"""Module for parsing .gitignore files and matching paths against gitignore patterns."""

import fnmatch
import pathlib
from typing import List


class GitignoreParser:
    """Class for parsing .gitignore files and matching paths against gitignore patterns.

    This class is responsible for parsing .gitignore files and checking if paths
    match gitignore patterns. It follows the Git specification for .gitignore files.
    """

    def __init__(self, fs_gateway=None):
        """Initialize the GitignoreParser.

        Args:
            fs_gateway: The filesystem gateway to use for reading .gitignore files.
                If None, the FileSystemGateway will be imported and instantiated.
        """
        if fs_gateway is None:
            from codebase_examiner.core.filesystem_gateway import FileSystemGateway

            self._fs_gateway = FileSystemGateway()
        else:
            self._fs_gateway = fs_gateway

    def parse_gitignore(self, directory: pathlib.Path) -> List[str]:
        """Parse .gitignore file in the given directory.

        Args:
            directory (pathlib.Path): The directory containing the .gitignore file.

        Returns:
            List[str]: A list of gitignore patterns.
        """
        gitignore_path = directory / ".gitignore"
        if not self._fs_gateway.path_exists(gitignore_path):
            return []

        content = self._fs_gateway.read_file(gitignore_path)
        patterns = []

        for line in content.splitlines():
            # Skip empty lines and comments
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Add the pattern
            patterns.append(line)

        return patterns

    def is_path_ignored(
        self,
        path: pathlib.Path,
        gitignore_patterns: List[str],
        base_dir: pathlib.Path,
        is_directory: bool = None,
        rel_path_str: str = None,
    ) -> bool:
        """Check if a path should be ignored based on gitignore patterns.

        Args:
            path (pathlib.Path): The path to check.
            gitignore_patterns (List[str]): List of gitignore patterns.
            base_dir (pathlib.Path): The base directory for relative paths.
            is_directory (bool, optional): Whether the path is a directory. If None,
                the method will try to determine it using the filesystem gateway.
            rel_path_str (str, optional): The relative path string to use for matching.
                If None, it will be computed from path and base_dir.

        Returns:
            bool: True if the path should be ignored, False otherwise.
        """
        if not gitignore_patterns:
            return False

        # Get the relative path from the base directory
        if rel_path_str is None:
            try:
                rel_path = path.relative_to(base_dir)
                rel_path_str = str(rel_path).replace("\\", "/")
            except ValueError:
                # If path is not relative to base_dir, use the full path
                rel_path_str = str(path).replace("\\", "/")

        # Check if the path matches any pattern
        for pattern in gitignore_patterns:
            # Handle negation (patterns starting with !)
            is_negation = pattern.startswith("!")
            if is_negation:
                pattern = pattern[1:]

            # Handle directory-specific patterns (ending with /)
            is_dir_only = pattern.endswith("/")
            if is_dir_only:
                pattern = pattern[:-1]
                # Check if the path is a directory
                if is_directory is None:
                    # Use the filesystem gateway to check if the path exists and is a directory
                    try:
                        is_dir = self._fs_gateway.path_exists(path) and path.is_dir()
                    except (AttributeError, ValueError):
                        # If we can't determine if it's a directory, assume it's not
                        is_dir = False
                else:
                    is_dir = is_directory
                if not is_dir:
                    continue

            # Convert gitignore pattern to fnmatch pattern
            if pattern.startswith("/"):
                # Patterns starting with / match only at the root level
                pattern = pattern[1:]
                if fnmatch.fnmatch(rel_path_str, pattern):
                    return not is_negation
            elif pattern.startswith("**/"):
                # Patterns starting with **/ match in any directory
                pattern = pattern[3:]
                if fnmatch.fnmatch(rel_path_str, pattern) or any(
                    fnmatch.fnmatch(part, pattern) for part in rel_path_str.split("/")
                ):
                    return not is_negation
            elif "/" in pattern:
                # Patterns with / are treated as relative to the .gitignore location
                if fnmatch.fnmatch(rel_path_str, pattern):
                    return not is_negation
            else:
                # Patterns without / match files or directories in any location
                if fnmatch.fnmatch(rel_path_str, pattern) or any(
                    fnmatch.fnmatch(part, pattern) for part in rel_path_str.split("/")
                ):
                    return not is_negation

        return False
