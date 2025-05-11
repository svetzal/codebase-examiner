"""Tool implementations for Codebase Examiner.

This module provides LLMTool implementations that can be used with the JsonRpcHandler.
"""

import os
from pathlib import Path
from typing import Dict, Any, List

from mojentic.llm.tools.llm_tool import LLMTool

from codebase_examiner.core.code_inspector import inspect_codebase
from codebase_examiner.core.doc_generator import generate_documentation


class LLMExaminerTool(LLMTool):
    """LLM Tool for examining a Python codebase and generating documentation."""

    def run(self, directory: str = ".", exclude_dirs: List[str] = None, format_type: str = "markdown", include_dotfiles: bool = False) -> Dict[str, Any]:
        """
        Examines a Python codebase and generates documentation.

        Parameters
        ----------
        directory : str, optional
            The directory to examine, by default "."
        exclude_dirs : List[str], optional
            Directories to exclude from examination, by default [".venv", ".git", "__pycache__", "tests", "build", "dist"]
        format_type : str, optional
            The format of the generated documentation, by default "markdown"
        include_dotfiles : bool, optional
            Whether to include dotfiles in the examination, by default False

        Returns
        -------
        dict
            A dictionary containing the generated documentation and metadata
        """
        try:
            # Set default exclude_dirs if None
            if exclude_dirs is None:
                exclude_dirs = [".venv", ".git", "__pycache__", "tests", "build", "dist"]

            # Convert directory to absolute path if it's relative
            if not os.path.isabs(directory):
                directory = str(Path(directory).resolve())

            # Inspect the codebase
            modules = inspect_codebase(directory, set(exclude_dirs), not include_dotfiles)

            # Generate documentation
            documentation = generate_documentation(modules, format_type)

            return {
                "status": "success",
                "documentation": documentation,
                "modules_found": len(modules)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    @property
    def descriptor(self):
        return {
            "type": "function",
            "function": {
                "name": "examine_codebase",
                "description": "Examine a Python codebase and generate documentation. This tool analyzes Python files to extract information about modules, classes, functions, and their documentation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "The directory to examine. Default is the current directory."
                        },
                        "exclude_dirs": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Directories to exclude from examination. Default is ['.venv', '.git', '__pycache__', 'tests', 'build', 'dist']."
                        },
                        "format_type": {
                            "type": "string",
                            "enum": ["markdown", "json"],
                            "description": "The format of the generated documentation. Default is 'markdown'."
                        },
                        "include_dotfiles": {
                            "type": "boolean",
                            "description": "Whether to include dotfiles in the examination. Default is false."
                        }
                    },
                    "required": []
                }
            }
        }




