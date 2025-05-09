import json
import sys
import unittest
from io import StringIO
from unittest.mock import patch

from codebase_examiner.mcp_stdio import StdioMcpServer


class TestStdioMcpServer(unittest.TestCase):
    """Tests for the StdioMcpServer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.server = StdioMcpServer()
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


if __name__ == "__main__":
    unittest.main()
