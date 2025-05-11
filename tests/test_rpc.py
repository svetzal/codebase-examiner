"""Tests for the JSON-RPC handler."""

import pytest
from unittest.mock import patch, Mock

from codebase_examiner.rpc import JsonRpcHandler, JsonRpcRequest, JsonRpcError


class TestJsonRpcHandler:
    """Tests for the JsonRpcHandler class."""

    def test_should_be_instantiated(self):
        """Test that JsonRpcHandler can be instantiated."""
        handler = JsonRpcHandler()

        assert isinstance(handler, JsonRpcHandler)
        assert handler.should_exit is False
        assert len(handler.methods) > 0

    def test_should_handle_initialize_request(self):
        """Test handling of initialize request."""
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

    def test_should_handle_tools_list_request(self):
        """Test handling of tools/list request."""
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

    def test_should_handle_tools_call_examine_request(self):
        """Test handling of tools/call request for the examine tool."""
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

        # Mock the _handle_examine method to avoid actual codebase examination
        with patch.object(handler, '_handle_examine', return_value={
            "status": "success",
            "documentation": "# Test Documentation",
            "modules_found": 5
        }):
            response = handler.handle_request(request)

        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 9
        assert "result" in response
        assert "status" in response["result"]
        assert response["result"]["status"] == "success"
        assert "documentation" in response["result"]
        assert "modules_found" in response["result"]

    def test_should_handle_shutdown_request(self):
        """Test handling of shutdown request."""
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

    def test_should_handle_exit_request(self):
        """Test handling of exit request."""
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

    def test_should_handle_unknown_method(self):
        """Test handling of unknown method."""
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

    def test_should_handle_tools_call_unknown_tool(self):
        """Test handling of tools/call request for an unknown tool."""
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

    def test_should_handle_examine_with_mocked_inspect_codebase(self):
        """Test handling of examine request with mocked inspect_codebase."""
        handler = JsonRpcHandler()

        # Mock the inspect_codebase and generate_documentation functions
        with patch('codebase_examiner.rpc.inspect_codebase', return_value=["module1", "module2"]), \
             patch('codebase_examiner.rpc.generate_documentation', return_value="# Test Documentation"):

            result = handler._handle_examine({
                "directory": ".",
                "format": "markdown"
            })

        assert result["status"] == "success"
        assert result["documentation"] == "# Test Documentation"
        assert result["modules_found"] == 2


