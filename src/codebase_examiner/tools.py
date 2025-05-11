"""Tool interface and implementations for Codebase Examiner.

This module provides a base Tool class and implementations for specific tools
that can be registered with the JsonRpcHandler.
"""

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Set

from pydantic import BaseModel

from codebase_examiner.core.code_inspector import inspect_codebase
from codebase_examiner.core.doc_generator import generate_documentation


class Tool(ABC):
    """Base class for tools that can be registered with the JsonRpcHandler."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the tool.

        Returns:
            str: The name of the tool
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Get the description of the tool.

        Returns:
            str: The description of the tool
        """
        pass

    @abstractmethod
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with the given arguments.

        Args:
            arguments (Dict[str, Any]): The tool arguments

        Returns:
            Dict[str, Any]: The result of the tool execution
        """
        pass


class ExaminerTool(Tool):
    """Tool for examining a Python codebase and generating documentation."""

    @property
    def name(self) -> str:
        """Get the name of the tool.

        Returns:
            str: The name of the tool
        """
        return "examine"

    @property
    def description(self) -> str:
        """Get the description of the tool.

        Returns:
            str: The description of the tool
        """
        return "Examine a Python codebase and generate documentation"

    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with the given arguments.

        Args:
            arguments (Dict[str, Any]): The tool arguments

        Returns:
            Dict[str, Any]: The result of the tool execution
        """
        try:
            # Extract parameters from arguments
            directory = arguments.get("directory", ".")
            exclude_dirs = set(arguments.get("exclude_dirs", [".venv", ".git", "__pycache__", "tests", "build", "dist"]))
            format_type = arguments.get("format", "markdown")
            include_dotfiles = arguments.get("include_dotfiles", False)

            # Convert directory to absolute path if it's relative
            if not os.path.isabs(directory):
                directory = str(Path(directory).resolve())

            # Inspect the codebase
            modules = inspect_codebase(directory, exclude_dirs, not include_dotfiles)

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


class ToolRegistry:
    """Registry for tools that can be used with the JsonRpcHandler."""

    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, Tool] = {}

    def register_tool(self, tool: Tool) -> None:
        """Register a tool with the registry.

        Args:
            tool (Tool): The tool to register
        """
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Tool:
        """Get a tool by name.

        Args:
            name (str): The name of the tool

        Returns:
            Tool: The tool with the given name

        Raises:
            KeyError: If no tool with the given name is registered
        """
        return self._tools[name]

    def list_tools(self) -> List[Dict[str, str]]:
        """List all registered tools.

        Returns:
            List[Dict[str, str]]: A list of tool information dictionaries
        """
        return [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in self._tools.values()
        ]

    def has_tool(self, name: str) -> bool:
        """Check if a tool with the given name is registered.

        Args:
            name (str): The name of the tool

        Returns:
            bool: True if a tool with the given name is registered, False otherwise
        """
        return name in self._tools
