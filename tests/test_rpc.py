"""Tests for the JSON-RPC handler."""

import pytest
from unittest.mock import patch, Mock

from codebase_examiner.rpc import JsonRpcHandler, JsonRpcRequest, JsonRpcError
from codebase_examiner.tools import ToolRegistry, Tool


@pytest.fixture
def mock_tool():
    """Create a mock tool for testing."""
    mock = Mock(spec=Tool)
    mock.name = "examine"
    mock.description = "Examine a Python codebase and generate documentation"
    mock.execute.return_value = {
        "status": "success",
        "documentation": "# Test Documentation",
        "modules_found": 5
    }
    return mock


@pytest.fixture
def mock_tool_registry(mock_tool):
    """Create a mock tool registry for testing."""
    mock = Mock(spec=ToolRegistry)
    mock.list_tools.return_value = [
        {
            "name": "examine",
            "description": "Examine a Python codebase and generate documentation"
        }
    ]
    mock.has_tool.return_value = True
    mock.get_tool.return_value = mock_tool
    return mock


class TestJsonRpcHandler:
    """Tests for the JsonRpcHandler class."""

    def test_should_be_instantiated(self, mock_tool_registry):
        """Test that JsonRpcHandler can be instantiated."""
        with patch('codebase_examiner.rpc.ToolRegistry', return_value=mock_tool_registry):
            handler = JsonRpcHandler()

            assert isinstance(handler, JsonRpcHandler)
            assert handler.should_exit is False
            assert len(handler.methods) > 0
            assert handler.tool_registry == mock_tool_registry

    def test_should_handle_initialize_request(self, mock_tool_registry):
        """Test handling of initialize request."""
        with patch('codebase_examiner.rpc.ToolRegistry', return_value=mock_tool_registry):
            handler = JsonRpcHandler()
            request = JsonRpcRequest(
                jsonrpc="2.0",
                id=1,
                method="initialize",
                params={
                    "protocolVersion": "2025-03-26",
                    "capabilities": {}
                }
            )

            response = handler.handle_request(request)

            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "result" in response
            assert "serverInfo" in response["result"]
            assert "capabilities" in response["result"]
            assert response["result"]["protocolVersion"] == "2025-03-26"

    def test_should_handle_tools_list_request(self, mock_tool_registry):
        """Test handling of tools/list request."""
        with patch('codebase_examiner.rpc.ToolRegistry', return_value=mock_tool_registry):
            handler = JsonRpcHandler()
            request = JsonRpcRequest(
                jsonrpc="2.0",
                id=8,
                method="tools/list",
                params={}
            )

            response = handler.handle_request(request)

            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 8
            assert "result" in response
            assert "tools" in response["result"]
            assert isinstance(response["result"]["tools"], list)
            assert len(response["result"]["tools"]) > 0

            # Verify the examine tool is in the list
            examine_tool = next((tool for tool in response["result"]["tools"] if tool["name"] == "examine"), None)
            assert examine_tool is not None
            assert "description" in examine_tool

            # Verify that the mock tool registry's list_tools method was called
            mock_tool_registry.list_tools.assert_called_once()

    def test_should_handle_tools_call_examine_request(self, mock_tool_registry, mock_tool):
        """Test handling of tools/call request for the examine tool."""
        with patch('codebase_examiner.rpc.ToolRegistry', return_value=mock_tool_registry):
            handler = JsonRpcHandler()
            request = JsonRpcRequest(
                jsonrpc="2.0",
                id=9,
                method="tools/call",
                params={
                    "name": "examine",
                    "arguments": {
                        "directory": ".",
                        "format": "markdown"
                    }
                }
            )

            response = handler.handle_request(request)

            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 9
            assert "result" in response
            assert "status" in response["result"]
            assert response["result"]["status"] == "success"
            assert "documentation" in response["result"]
            assert "modules_found" in response["result"]

            # Verify that the mock tool registry's has_tool and get_tool methods were called
            mock_tool_registry.has_tool.assert_called_once_with("examine")
            mock_tool_registry.get_tool.assert_called_once_with("examine")

            # Verify that the mock tool's execute method was called with the correct arguments
            mock_tool.execute.assert_called_once_with({
                "directory": ".",
                "format": "markdown"
            })

    def test_should_handle_shutdown_request(self, mock_tool_registry):
        """Test handling of shutdown request."""
        with patch('codebase_examiner.rpc.ToolRegistry', return_value=mock_tool_registry):
            handler = JsonRpcHandler()
            request = JsonRpcRequest(
                jsonrpc="2.0",
                id=10,
                method="shutdown",
                params={}
            )

            response = handler.handle_request(request)

            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 10
            assert "result" in response
            assert response["result"] is None
            assert handler.should_exit is True

    def test_should_handle_exit_request(self, mock_tool_registry):
        """Test handling of exit request."""
        with patch('codebase_examiner.rpc.ToolRegistry', return_value=mock_tool_registry):
            handler = JsonRpcHandler()
            request = JsonRpcRequest(
                jsonrpc="2.0",
                id=11,
                method="exit",
                params={}
            )

            response = handler.handle_request(request)

            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 11
            assert "result" in response
            assert response["result"] is None
            assert handler.should_exit is True

    def test_should_handle_unknown_method(self, mock_tool_registry):
        """Test handling of unknown method."""
        with patch('codebase_examiner.rpc.ToolRegistry', return_value=mock_tool_registry):
            handler = JsonRpcHandler()
            request = JsonRpcRequest(
                jsonrpc="2.0",
                id=12,
                method="unknown_method",
                params={}
            )

            response = handler.handle_request(request)

            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 12
            assert "error" in response
            assert response["error"]["code"] == -32601
            assert "Method not found" in response["error"]["message"]

    def test_should_handle_tools_call_unknown_tool(self, mock_tool_registry):
        """Test handling of tools/call request for an unknown tool."""
        # Configure the mock tool registry to return False for has_tool("unknown_tool")
        mock_tool_registry.has_tool.side_effect = lambda name: name == "examine"

        with patch('codebase_examiner.rpc.ToolRegistry', return_value=mock_tool_registry):
            handler = JsonRpcHandler()
            request = JsonRpcRequest(
                jsonrpc="2.0",
                id=13,
                method="tools/call",
                params={
                    "name": "unknown_tool",
                    "arguments": {}
                }
            )

            response = handler.handle_request(request)

            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 13
            assert "error" in response
            assert response["error"]["code"] == -32601
            assert "Tool not found" in response["error"]["message"]

            # Verify that the mock tool registry's has_tool method was called with the correct argument
            mock_tool_registry.has_tool.assert_called_with("unknown_tool")

