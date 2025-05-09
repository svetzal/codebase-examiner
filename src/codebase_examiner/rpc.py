"""Common RPC infrastructure for Codebase Examiner.

This module provides a common JSONRPC infrastructure that can be used by different
transport mechanisms (HTTP, STDIO, etc.) to handle RPC requests.
"""

import os
from importlib.metadata import version
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Union, Callable

from codebase_examiner.core.code_inspector import inspect_codebase
from codebase_examiner.core.doc_generator import generate_documentation


class JsonRpcError(Exception):
    """Exception raised for JSON-RPC errors."""

    def __init__(self, code: int, message: str, data: Any = None):
        """Initialize a JSON-RPC error.

        Args:
            code (int): The error code
            message (str): The error message
            data (Any, optional): Additional error data. Defaults to None.
        """
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)


class JsonRpcHandler:
    """Base class for handling JSON-RPC 2.0 requests."""

    def __init__(self):
        """Initialize the JSON-RPC handler."""
        self.should_exit = False
        self.methods = {
            "initialize": self._handle_initialize,
            "shutdown": self._handle_shutdown,
            "exit": self._handle_exit,
            "tools/list": self._handle_tools_list,
            "tools/call": self._handle_tools_call,
        }

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a JSON-RPC 2.0 request.

        Args:
            request (Dict[str, Any]): The JSON-RPC request

        Returns:
            Dict[str, Any]: The JSON-RPC response
        """
        # Check if this is a valid JSON-RPC 2.0 request
        if not self._is_valid_jsonrpc_request(request):
            return self._create_error_response(
                request.get("id"),
                -32600,
                "Invalid Request"
            )

        method = request.get("method")
        request_id = request.get("id")
        params = request.get("params", {})

        # Check if the method exists
        if method not in self.methods:
            return self._create_error_response(
                request_id,
                -32601,
                f"Method not found: {method}"
            )

        # Call the method handler
        try:
            result = self.methods[method](params)
            return self._create_result_response(request_id, result)
        except JsonRpcError as e:
            return self._create_error_response(
                request_id,
                e.code,
                e.message,
                e.data
            )
        except Exception as e:
            return self._create_error_response(
                request_id,
                -32603,
                f"Internal error: {str(e)}"
            )

    def _is_valid_jsonrpc_request(self, request: Dict[str, Any]) -> bool:
        """Check if a request is a valid JSON-RPC 2.0 request.

        Args:
            request (Dict[str, Any]): The request to check

        Returns:
            bool: True if the request is valid, False otherwise
        """
        return (
            isinstance(request, dict) and
            request.get("jsonrpc") == "2.0" and
            "method" in request and
            isinstance(request.get("method"), str)
        )

    def _create_result_response(self, request_id: Any, result: Any) -> Dict[str, Any]:
        """Create a JSON-RPC 2.0 result response.

        Args:
            request_id (Any): The request ID
            result (Any): The result

        Returns:
            Dict[str, Any]: The JSON-RPC response
        """
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }

    def _create_error_response(self, request_id: Any, code: int, message: str, data: Any = None) -> Dict[str, Any]:
        """Create a JSON-RPC 2.0 error response.

        Args:
            request_id (Any): The request ID
            code (int): The error code
            message (str): The error message
            data (Any, optional): Additional error data. Defaults to None.

        Returns:
            Dict[str, Any]: The JSON-RPC response
        """
        error = {
            "code": code,
            "message": message
        }
        if data is not None:
            error["data"] = data

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": error
        }

    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the initialize method.

        Args:
            params (Dict[str, Any]): The method parameters

        Returns:
            Dict[str, Any]: The result
        """
        protocol_version = params.get("protocolVersion")
        capabilities = params.get("capabilities", {})

        return {
            "serverInfo": {
                "name": "Codebase Examiner",
                "version": version("codebase-examiner")
            },
            "capabilities": {
                "examineProvider": True
            },
            "protocolVersion": protocol_version
        }

    def _handle_shutdown(self, params: Dict[str, Any]) -> None:
        """Handle the shutdown method.

        Args:
            params (Dict[str, Any]): The method parameters

        Returns:
            None: No result
        """
        self.should_exit = True
        return None

    def _handle_exit(self, params: Dict[str, Any]) -> None:
        """Handle the exit method.

        Args:
            params (Dict[str, Any]): The method parameters

        Returns:
            None: No result
        """
        self.should_exit = True
        return None

    def _handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the tools/list method.

        Args:
            params (Dict[str, Any]): The method parameters

        Returns:
            Dict[str, Any]: The result
        """
        return {
            "tools": [
                {
                    "name": "examine",
                    "description": "Examine a Python codebase and generate documentation"
                }
            ]
        }

    def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the tools/call method.

        Args:
            params (Dict[str, Any]): The method parameters

        Returns:
            Dict[str, Any]: The result
        """
        tool_name = params.get("name")
        tool_arguments = params.get("arguments", {})

        if tool_name == "examine":
            return self._handle_examine(tool_arguments)
        else:
            raise JsonRpcError(-32601, f"Tool not found: {tool_name}")

    def _handle_examine(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an examine request.

        Args:
            params (Dict[str, Any]): The examination request parameters

        Returns:
            Dict[str, Any]: The examination result
        """
        try:
            # Extract parameters from request
            directory = params.get("directory", ".")
            exclude_dirs = set(params.get("exclude_dirs", [".venv", ".git", "__pycache__", "tests", "build", "dist"]))
            format_type = params.get("format", "markdown")
            include_dotfiles = params.get("include_dotfiles", False)

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