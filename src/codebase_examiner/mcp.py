"""MCP server implementation for Codebase Examiner."""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Set

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


from codebase_examiner.core.code_inspector import inspect_codebase
from codebase_examiner.core.doc_generator import generate_documentation


class ExamineRequest(BaseModel):
    """Request model for examining a codebase."""
    directory: str = Field(default=".", description="Directory to examine")
    exclude_dirs: Optional[List[str]] = Field(default=[".venv", ".git", "__pycache__", "tests", "build", "dist"], description="Directories to exclude")
    format: str = Field(default="markdown", description="Output format (markdown or json)")
    include_dotfiles: bool = Field(default=False, description="Include files and directories starting with a dot")


class ExamineResponse(BaseModel):
    """Response model for examine endpoint."""
    documentation: str
    modules_found: int


app = FastAPI(title="Codebase Examiner MCP", description="MCP server for examining Python codebases")


@app.post("/examine", response_model=ExamineResponse)
async def examine_codebase(request: ExamineRequest):
    """Examine a Python codebase and generate documentation.
    
    Args:
        request (ExamineRequest): The examination request parameters
        
    Returns:
        ExamineResponse: The generated documentation
    """
    try:
        # Convert directory to absolute path if it's relative
        directory = request.directory
        if not os.path.isabs(directory):
            directory = str(Path(directory).resolve())
        
        # Convert exclude_dirs list to set
        exclude_dirs = set(request.exclude_dirs or [".venv", ".git", "__pycache__", "tests", "build", "dist"])
        
        # Inspect the codebase
        modules = inspect_codebase(directory, exclude_dirs, not request.include_dotfiles)
        
        # Generate documentation
        documentation = generate_documentation(modules, request.format)
        
        return ExamineResponse(
            documentation=documentation,
            modules_found=len(modules)
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
        print("Usage: python -m codebase_examiner.mcp <port>")
        sys.exit(1)
    port = int(sys.argv[1])
    start_server(port)