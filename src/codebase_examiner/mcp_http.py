"""HTTP-based MCP server implementation for Codebase Examiner."""

import json
from typing import Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel, Field

from codebase_examiner.rpc import JsonRpcHandler


class JsonRpcRequest(BaseModel):
    """JSON-RPC 2.0 request model."""
    jsonrpc: str = Field("2.0", description="JSON-RPC version")
    id: Optional[Any] = Field(None, description="Request ID")
    method: str = Field(..., description="Method name")
    params: Optional[Dict[str, Any]] = Field(None, description="Method parameters")


# Legacy models for backward compatibility
class ExamineRequest(BaseModel):
    """Request model for examining a codebase (legacy)."""
    directory: str = Field(default=".", description="Directory to examine")
    exclude_dirs: Optional[list[str]] = Field(default=[".venv", ".git", "__pycache__", "tests", "build", "dist"], description="Directories to exclude")
    format: str = Field(default="markdown", description="Output format (markdown or json)")
    include_dotfiles: bool = Field(default=False, description="Include files and directories starting with a dot")


class ExamineResponse(BaseModel):
    """Response model for examine endpoint (legacy)."""
    documentation: str
    modules_found: int


app = FastAPI(title="Codebase Examiner MCP", description="MCP server for examining Python codebases")
rpc_handler = JsonRpcHandler()


@app.post("/jsonrpc")
async def handle_jsonrpc(request: Request) -> Response:
    """Handle JSON-RPC 2.0 requests.

    Args:
        request (Request): The FastAPI request object

    Returns:
        Response: The JSON-RPC response
    """
    try:
        # Parse the request body
        body = await request.json()

        # Handle the JSON-RPC request
        response = rpc_handler.handle_request(body)

        # Return the response
        return Response(
            content=json.dumps(response),
            media_type="application/json"
        )
    except json.JSONDecodeError:
        # Invalid JSON
        error_response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32700,
                "message": "Parse error"
            }
        }
        return Response(
            content=json.dumps(error_response),
            media_type="application/json",
            status_code=400
        )
    except Exception as e:
        # Server error
        error_response = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }
        return Response(
            content=json.dumps(error_response),
            media_type="application/json",
            status_code=500
        )


@app.post("/examine", response_model=ExamineResponse)
async def examine_codebase(request: ExamineRequest):
    """Examine a Python codebase and generate documentation (legacy endpoint).

    Args:
        request (ExamineRequest): The examination request parameters

    Returns:
        ExamineResponse: The generated documentation
    """
    try:
        # Convert to JSON-RPC format and use the RPC handler
        jsonrpc_request = {
            "jsonrpc": "2.0",
            "id": "legacy",
            "method": "tools/call",
            "params": {
                "name": "examine",
                "arguments": {
                    "directory": request.directory,
                    "exclude_dirs": request.exclude_dirs,
                    "format": request.format,
                    "include_dotfiles": request.include_dotfiles
                }
            }
        }

        # Handle the JSON-RPC request
        response = rpc_handler.handle_request(jsonrpc_request)

        # Check for errors
        if "error" in response:
            raise Exception(response["error"]["message"])

        # Extract the result
        result = response["result"]

        # Return the response
        return ExamineResponse(
            documentation=result["documentation"],
            modules_found=result["modules_found"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def start_server(port: int):
    """Start the MCP server.

    Args:
        port (int): The port to run the server on
    """
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m codebase_examiner.mcp_http <port>")
        sys.exit(1)
    port = int(sys.argv[1])
    start_server(port)