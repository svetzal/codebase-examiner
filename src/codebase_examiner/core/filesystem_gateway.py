"""Module for abstracting filesystem operations."""

import os
import pathlib
import configparser
import re
from typing import List, Set, Optional, Tuple, Dict, Any


class FileSystemGateway:
    """Gateway for filesystem operations.

    This class abstracts all filesystem operations to allow for easier testing
    by providing a single point for mocking filesystem interactions.
    """

    def path_exists(self, path: pathlib.Path) -> bool:
        """Check if a path exists.

        Args:
            path (pathlib.Path): The path to check.

        Returns:
            bool: True if the path exists, False otherwise.
        """
        return path.exists()

    def read_file(self, path: pathlib.Path) -> str:
        """Read the contents of a file.

        Args:
            path (pathlib.Path): The path to the file.

        Returns:
            str: The contents of the file.
        """
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def write_file(self, path: pathlib.Path, content: str) -> None:
        """Write content to a file.

        Args:
            path (pathlib.Path): The path to the file.
            content (str): The content to write.
        """
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def walk_directory(self, directory: pathlib.Path, exclude_dirs: Set[str] = None) -> List[Tuple[str, List[str], List[str]]]:
        """Walk a directory recursively.

        Args:
            directory (pathlib.Path): The directory to walk.
            exclude_dirs (Set[str], optional): Set of directory names to exclude.

        Returns:
            List[Tuple[str, List[str], List[str]]]: A list of tuples containing
                (root, dirs, files) for each directory in the tree.
        """
        if exclude_dirs is None:
            exclude_dirs = set()

        results = []
        for root, dirs, files in os.walk(directory):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            results.append((root, dirs, files))

        return results

    def resolve_path(self, path: pathlib.Path) -> pathlib.Path:
        """Resolve a path to its absolute form.

        Args:
            path (pathlib.Path): The path to resolve.

        Returns:
            pathlib.Path: The resolved path.
        """
        return path.resolve()

    def join_paths(self, root: str, file: str) -> pathlib.Path:
        """Join two path components.

        Args:
            root (str): The root path.
            file (str): The file or directory name.

        Returns:
            pathlib.Path: The joined path.
        """
        return pathlib.Path(os.path.join(root, file))

    def read_config(self, path: pathlib.Path) -> configparser.ConfigParser:
        """Read a configuration file.

        Args:
            path (pathlib.Path): The path to the configuration file.

        Returns:
            configparser.ConfigParser: The parsed configuration.
        """
        config = configparser.ConfigParser()
        config.read(path)
        return config

    def get_file_stem(self, path: pathlib.Path) -> str:
        """Get the stem (filename without extension) of a file.

        Args:
            path (pathlib.Path): The path to the file.

        Returns:
            str: The stem of the file.
        """
        return path.stem

    def get_file_suffix(self, path: pathlib.Path) -> str:
        """Get the suffix (extension) of a file.

        Args:
            path (pathlib.Path): The path to the file.

        Returns:
            str: The suffix of the file.
        """
        return path.suffix

    def load_module(self, module_name: str, file_path: pathlib.Path) -> Any:
        """Load a Python module from a file path.

        Args:
            module_name (str): The name to give the module.
            file_path (pathlib.Path): The path to the Python file.

        Returns:
            Any: The loaded module.
        """
        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module from {file_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        return module

