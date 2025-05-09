"""STDIO-based MCP server implementation for Codebase Examiner."""

import json
import os
import sys
import threading
from importlib.metadata import version
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Union



from codebase_examiner.core.code_inspector import inspect_codebase
from codebase_examiner.core.doc_generator import generate_documentation


class StdioMcpServer:
    """An MCP server that communicates over standard input/output."""

    def __init__(self):
        """Initialize the STDIO MCP server."""
        self.should_exit = False

    def _read_request(self) -> Dict[str, Any]:
        """Read a JSON request from standard input.

        Returns:
            Dict[str, Any]: The parsed JSON request
        """
        try:
            line = sys.stdin.readline()
            if not line:
                self.should_exit = True
                return {}

            return json.loads(line)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON request"}

    def _write_response(self, response: Dict[str, Any]) -> None:
        """Write a JSON response to standard output.

        Args:
            response (Dict[str, Any]): The response to write
        """
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()

    def _handle_examine_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a request to examine a codebase.

        Args:
            request (Dict[str, Any]): The examination request

        Returns:
            Dict[str, Any]: The response with generated documentation
        """
        try:
            # Extract parameters from request
            directory = request.get("directory", ".")
            exclude_dirs = set(request.get("exclude_dirs", [".venv", ".git", "__pycache__", "tests", "build", "dist"]))
            format_type = request.get("format", "markdown")
            include_dotfiles = request.get("include_dotfiles", False)

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



    def _handle_ping(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a ping request.

        Args:
            request (Dict[str, Any]): The ping request

        Returns:
            Dict[str, Any]: A pong response
        """
        return {
            "status": "success",
            "message": "pong"
        }

    def _handle_jsonrpc_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a JSON-RPC 2.0 request.

        Args:
            request (Dict[str, Any]): The JSON-RPC request

        Returns:
            Dict[str, Any]: The JSON-RPC response
        """
        method = request.get("method")
        request_id = request.get("id")
        params = request.get("params", {})

        # Basic response structure
        response = {
            "jsonrpc": "2.0",
            "id": request_id
        }

        if method == "initialize":
            # Handle initialize method
            protocol_version = params.get("protocolVersion")
            capabilities = params.get("capabilities", {})

            # Check if the protocol version is supported
            # For now, accept any protocol version
            response["result"] = {
                "serverInfo": {
                    "name": "Codebase Examiner",
                    "version": version("codebase-examiner")
                },
                "capabilities": {
                    "examineProvider": True
                },
                "protocolVersion": protocol_version
            }
        elif method == "shutdown":
            # Handle shutdown method
            self.should_exit = True
            response["result"] = None
        elif method == "exit":
            # Handle exit method
            self.should_exit = True
            response["result"] = None
        else:
            # Unknown method
            response["error"] = {
                "code": -32601,
                "message": f"Method not found: {method}"
            }

        return response

    def _handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a single request.

        Args:
            request (Dict[str, Any]): The request to handle

        Returns:
            Dict[str, Any]: The response
        """
        if "error" in request:
            return {"status": "error", "message": request["error"]}

        # Check if this is a JSON-RPC 2.0 request
        if "jsonrpc" in request and request.get("jsonrpc") == "2.0" and "method" in request:
            return self._handle_jsonrpc_request(request)

        # Handle legacy command-based requests
        command = request.get("command")

        if command == "examine":
            return self._handle_examine_request(request)
        elif command == "ping":
            return self._handle_ping(request)
        elif command == "exit":
            self.should_exit = True
            return {"status": "success", "message": "Server exiting"}
        else:
            return {
                "status": "error",
                "message": f"Unknown command: {command}"
            }

    def run(self) -> None:
        """Run the STDIO MCP server loop."""
        # Output an initialization message
        self._write_response({"status": "ready", "message": "STDIO MCP server ready"})

        while not self.should_exit:
            try:
                request = self._read_request()
                if self.should_exit:
                    break

                response = self._handle_request(request)
                self._write_response(response)
            except Exception as e:
                self._write_response({
                    "status": "error",
                    "message": f"Server error: {str(e)}"
                })


def start_server() -> None:
    """Start the STDIO MCP server."""
    server = StdioMcpServer()
    server.run()


if __name__ == "__main__":
    start_server()
