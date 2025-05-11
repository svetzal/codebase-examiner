"""Tests for the HTTP-based MCP server."""

import json
import unittest
from unittest.mock import patch, Mock

from fastapi.testclient import TestClient

from codebase_examiner.mcp_http import HttpMcpServer
from codebase_examiner.rpc import JsonRpcHandler


class TestMcpServer(unittest.TestCase):
    """Tests for the HTTP-based MCP server."""

    def setUp(self):
        """Set up test fixtures."""
        self.rpc_handler = JsonRpcHandler()
        self.server = HttpMcpServer(self.rpc_handler)
        self.client = TestClient(self.server.app)

    def test_jsonrpc_initialize_request(self):
        """Test handling of JSON-RPC initialize request."""
        # Prepare the initialize request
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {}
            }
        }

        # Mock the RPC handler to avoid actual initialization
        mock_response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {
                "serverInfo": {
                    "name": "Codebase Examiner",
                    "version": "0.1.0"
                },
                "capabilities": {
                    "examineProvider": True
                },
                "protocolVersion": "2025-03-26"
            }
        }

        with patch.object(self.rpc_handler, 'handle_request', return_value=mock_response):
            # Send the request
            response = self.client.post(
                "/jsonrpc",
                json=initialize_request
            )

        # Verify the response
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json["jsonrpc"], "2.0")
        self.assertEqual(response_json["id"], 1)
        self.assertIn("result", response_json)
        self.assertIn("serverInfo", response_json["result"])
        self.assertIn("capabilities", response_json["result"])
        self.assertEqual(response_json["result"]["protocolVersion"], "2025-03-26")

    def test_jsonrpc_tools_list_request(self):
        """Test handling of JSON-RPC tools/list request."""
        # Prepare the tools/list request
        tools_list_request = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/list",
            "params": {}
        }

        # Mock the RPC handler to avoid actual tools listing
        mock_response = {
            "jsonrpc": "2.0",
            "id": 8,
            "result": {
                "tools": [
                    {
                        "name": "examine",
                        "description": "Examine a Python codebase and generate documentation"
                    }
                ]
            }
        }

        with patch.object(self.rpc_handler, 'handle_request', return_value=mock_response):
            # Send the request
            response = self.client.post(
                "/jsonrpc",
                json=tools_list_request
            )

        # Verify the response
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json["jsonrpc"], "2.0")
        self.assertEqual(response_json["id"], 8)
        self.assertIn("result", response_json)
        self.assertIn("tools", response_json["result"])
        self.assertIsInstance(response_json["result"]["tools"], list)
        self.assertTrue(len(response_json["result"]["tools"]) > 0)

    def test_jsonrpc_tools_call_examine_request(self):
        """Test handling of JSON-RPC tools/call request for the examine tool."""
        # Prepare the tools/call request
        tools_call_request = {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {
                "name": "examine",
                "arguments": {
                    "directory": ".",
                    "format": "markdown"
                }
            }
        }

        # Mock the RPC handler to avoid actual codebase examination
        mock_response = {
            "jsonrpc": "2.0",
            "id": 9,
            "result": {
                "status": "success",
                "documentation": "# Test Documentation",
                "modules_found": 5
            }
        }

        with patch.object(self.rpc_handler, 'handle_request', return_value=mock_response):
            # Send the request
            response = self.client.post(
                "/jsonrpc",
                json=tools_call_request
            )

        # Verify the response
        self.assertEqual(response.status_code, 200)
        response_json = response.json()
        self.assertEqual(response_json["jsonrpc"], "2.0")
        self.assertEqual(response_json["id"], 9)
        self.assertIn("result", response_json)
        self.assertNotIn("error", response_json)
        self.assertIn("status", response_json["result"])
        self.assertEqual(response_json["result"]["status"], "success")
        self.assertIn("documentation", response_json["result"])
        self.assertIn("modules_found", response_json["result"])


    def test_jsonrpc_invalid_json(self):
        """Test handling of invalid JSON in JSON-RPC request."""
        # Send an invalid JSON request
        response = self.client.post(
            "/jsonrpc",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )

        # Verify the response
        self.assertEqual(response.status_code, 400)
        response_json = response.json()
        self.assertEqual(response_json["jsonrpc"], "2.0")
        self.assertIsNone(response_json["id"])
        self.assertIn("error", response_json)
        self.assertEqual(response_json["error"]["code"], -32700)
        self.assertEqual(response_json["error"]["message"], "Parse error")


if __name__ == "__main__":
    unittest.main()
