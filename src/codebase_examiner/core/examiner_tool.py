import os
from pathlib import Path
from typing import List, Dict, Any

from mojentic.llm.tools.llm_tool import LLMTool

from codebase_examiner.core.code_inspector import CodebaseInspector
from codebase_examiner.core.doc_generator import generate_documentation


class ExaminerTool(LLMTool):
    """LLM Tool for examining a Python codebase and generating documentation."""

    def run(
        self,
        directory: str = ".",
        exclude_dirs: List[str] = None,
        format_type: str = "markdown",
        include_dotfiles: bool = False,
        include_test_files: bool = False,
        use_gitignore: bool = True,
    ) -> Dict[str, Any]:
        """
        Examines a Python codebase and generates documentation.

        Parameters
        ----------
        directory : str, optional
            The directory to examine, by default "."
        exclude_dirs : List[str], optional
            Directories to exclude from examination (uses .gitignore patterns first if present,
            then falls back to these directories), by default [".venv", ".git", "__pycache__",
            "tests", "build", "dist"]
        format_type : str, optional
            The format of the generated documentation, by default "markdown"
        include_dotfiles : bool, optional
            Whether to include dotfiles in the examination, by default False
        include_test_files : bool, optional
            Whether to include test files in the examination, by default False
        use_gitignore : bool, optional
            Whether to use .gitignore patterns for exclusion, by default True

        Returns
        -------
        dict
            A dictionary containing the generated documentation and metadata
        """
        try:
            # Set default exclude_dirs if None
            if exclude_dirs is None:
                exclude_dirs = [
                    ".venv",
                    ".git",
                    "__pycache__",
                    "tests",
                    "build",
                    "dist",
                ]

            # Convert directory to absolute path if it's relative
            if not os.path.isabs(directory):
                directory = str(Path(directory).resolve())

            # Inspect the codebase
            inspector = CodebaseInspector()
            result = inspector.inspect_directory(
                directory=directory,
                exclude_dirs=set(exclude_dirs),
                exclude_dotfiles=not include_dotfiles,
                include_test_files=include_test_files,
                use_gitignore=use_gitignore,
            )

            # Generate documentation
            documentation = generate_documentation(result, format_type)

            return {
                "status": "success",
                "documentation": documentation,
                "modules_found": len(result.get_modules()),
                "extractors_used": result.extractors_used,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    @property
    def descriptor(self):
        return {
            "type": "function",
            "function": {
                "name": "examine_codebase",
                "description": "Examine a Python codebase and generate documentation. This tool "
                               "analyzes Python files to extract information about modules, "
                               "classes, functions, and their documentation.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "The directory to examine. Default is the current "
                                           "directory.",
                        },
                        "exclude_dirs": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Directories to exclude from examination (uses "
                                           ".gitignore patterns first if present, then falls back "
                                           "to these directories). Default is ['.venv', '.git', "
                                           "'__pycache__', 'tests', 'build', 'dist'].",
                        },
                        "format_type": {
                            "type": "string",
                            "enum": ["markdown", "json"],
                            "description": "The format of the generated documentation. Default is "
                                           "'markdown'.",
                        },
                        "include_dotfiles": {
                            "type": "boolean",
                            "description": "Whether to include dotfiles in the examination. "
                                           "Default is false.",
                        },
                        "include_test_files": {
                            "type": "boolean",
                            "description": "Whether to include test files in the examination. "
                                           "Default is false.",
                        },
                        "use_gitignore": {
                            "type": "boolean",
                            "description": "Whether to use .gitignore patterns for exclusion. "
                                           "Default is true.",
                        },
                    },
                    "required": [],
                },
            },
        }
