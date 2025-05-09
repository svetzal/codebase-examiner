"""Tests for the file_finder module."""

import os
import pathlib
import tempfile
from typing import Set

import pytest

from codebase_examiner.core.file_finder import find_python_files


def create_test_file_structure(root_path: pathlib.Path) -> None:
    """Create a test file structure for testing."""
    # Create a few Python files
    (root_path / "module1.py").write_text("# Test module 1")
    (root_path / "module2.py").write_text("# Test module 2")
    
    # Create a subdirectory with Python files
    subdir = root_path / "subpkg"
    subdir.mkdir()
    (subdir / "__init__.py").write_text("")
    (subdir / "submodule.py").write_text("# Test submodule")
    
    # Create an excluded directory with Python files
    venv_dir = root_path / ".venv"
    venv_dir.mkdir()
    (venv_dir / "env_module.py").write_text("# Should be excluded")


def test_find_python_files():
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
        assert "env_module.py" not in file_names  # Should be excluded


def test_find_python_files_with_custom_excludes():
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
        assert "env_module.py" not in file_names  # Should be excluded
        assert "excluded_module.py" not in file_names  # Should be excluded by custom rule