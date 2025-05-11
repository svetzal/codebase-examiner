import json
import sys
import unittest
from io import StringIO
from unittest.mock import patch, Mock

from codebase_examiner.mcp_stdio import StdioMcpServer
from codebase_examiner.rpc import JsonRpcHandler


class TestStdioMcpServer(unittest.TestCase):
    """Tests for the StdioMcpServer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.rpc_handler = JsonRpcHandler()
        self.server = StdioMcpServer(self.rpc_handler)
        self.mock_stdout = StringIO()
        self.mock_stdin = StringIO()

    def test_initialize_request(self):
        """Test handling of initialize request with protocol version 2025-03-26."""
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

        # Convert request to JSON and add to mock stdin
        self.mock_stdin.write(json.dumps(initialize_request) + "\n")
        self.mock_stdin.seek(0)  # Reset position to beginning

        # Patch stdin and stdout
        with patch('sys.stdin', self.mock_stdin), patch('sys.stdout', self.mock_stdout):
            # Process one request
            request = self.server._read_request()
            response = self.server._handle_request(request)
            self.server._write_response(response)

        # Get the response from mock stdout
        self.mock_stdout.seek(0)
        response_json = json.loads(self.mock_stdout.getvalue().strip())

        # Verify the response
        self.assertEqual(response_json["jsonrpc"], "2.0")
        self.assertEqual(response_json["id"], 1)
        self.assertIn("result", response_json)
        self.assertIn("serverInfo", response_json["result"])
        self.assertIn("capabilities", response_json["result"])
        self.assertEqual(response_json["result"]["protocolVersion"], "2025-03-26")

        # Verify the version matches the one in pyproject.toml
        self.assertEqual(response_json["result"]["serverInfo"]["version"], "0.1.0")

    def test_tools_list_request(self):
        """Test handling of tools/list request."""
        # Prepare the tools/list request
        tools_list_request = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/list",
            "params": {}
        }

        # Convert request to JSON and add to mock stdin
        self.mock_stdin.write(json.dumps(tools_list_request) + "\n")
        self.mock_stdin.seek(0)  # Reset position to beginning

        # Patch stdin and stdout
        with patch('sys.stdin', self.mock_stdin), patch('sys.stdout', self.mock_stdout):
            # Process one request
            request = self.server._read_request()
            response = self.server._handle_request(request)
            self.server._write_response(response)

        # Get the response from mock stdout
        self.mock_stdout.seek(0)
        response_json = json.loads(self.mock_stdout.getvalue().strip())

        # Verify the response
        self.assertEqual(response_json["jsonrpc"], "2.0")
        self.assertEqual(response_json["id"], 8)
        self.assertIn("result", response_json)
        self.assertIn("tools", response_json["result"])
        self.assertIsInstance(response_json["result"]["tools"], list)
        self.assertTrue(len(response_json["result"]["tools"]) > 0)

        # Verify the examine tool is in the list
        examine_tool = next((tool for tool in response_json["result"]["tools"] if tool["name"] == "examine"), None)
        self.assertIsNotNone(examine_tool)
        self.assertIn("description", examine_tool)

    def test_tools_call_examine_request(self):
        """Test handling of tools/call request for the examine tool."""
        # Prepare the tools/call request
        tools_call_request = {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {
                "name": "examine",
                "arguments": {}
            }
        }

        # Convert request to JSON and add to mock stdin
        self.mock_stdin.write(json.dumps(tools_call_request) + "\n")
        self.mock_stdin.seek(0)  # Reset position to beginning

        # Patch stdin and stdout
        with patch('sys.stdin', self.mock_stdin), patch('sys.stdout', self.mock_stdout):
            # Process one request
            request = self.server._read_request()
            response = self.server._handle_request(request)
            self.server._write_response(response)

        # Get the response from mock stdout
        self.mock_stdout.seek(0)
        response_json = json.loads(self.mock_stdout.getvalue().strip())

        # Verify the response
        self.assertEqual(response_json["jsonrpc"], "2.0")
        self.assertEqual(response_json["id"], 9)
        self.assertIn("result", response_json)
        self.assertNotIn("error", response_json)

        # Verify the result contains expected fields from examine response
        self.assertIn("status", response_json["result"])
        self.assertEqual(response_json["result"]["status"], "success")
        self.assertIn("documentation", response_json["result"])
        self.assertIn("modules_found", response_json["result"])

    def test_legacy_examine_request(self):
        """Test handling of legacy examine request."""
        # Prepare the legacy examine request
        legacy_request = {
            "command": "examine",
            "directory": ".",
            "format": "markdown"
        }

        # Mock the RPC handler to avoid actual codebase examination
        mock_result = {
            "status": "success",
            "documentation": "# Test Documentation",
            "modules_found": 5
        }
        mock_response = {
            "jsonrpc": "2.0",
            "id": "legacy",
            "result": mock_result
        }

        with patch.object(self.server.rpc_handler, 'handle_request', return_value=mock_response):
            # Convert request to JSON and add to mock stdin
            self.mock_stdin.write(json.dumps(legacy_request) + "\n")
            self.mock_stdin.seek(0)  # Reset position to beginning

            # Patch stdin and stdout
            with patch('sys.stdin', self.mock_stdin), patch('sys.stdout', self.mock_stdout):
                # Process one request
                request = self.server._read_request()
                response = self.server._handle_request(request)
                self.server._write_response(response)

        # Get the response from mock stdout
        self.mock_stdout.seek(0)
        response_json = json.loads(self.mock_stdout.getvalue().strip())

        # Verify the response
        self.assertEqual(response_json["status"], "success")
        self.assertEqual(response_json["documentation"], "# Test Documentation")
        self.assertEqual(response_json["modules_found"], 5)


if __name__ == "__main__":
    unittest.main()
