# Codebase Examiner

A command-line tool that examines Python codebases and generates comprehensive documentation about modules, classes, and functions. It can be run as a standalone CLI tool or as an HTTP/STDIO MCP server to provide this service to GenAI agents.

## Features

- Find all Python files in a project directory tree
- Automatically detect and respect pytest.ini configuration for test file organization
- Support different test layout strategies (separate tests directory or tests alongside implementation)
- Extract documentation from modules, classes, and functions
- Parse Google-style docstrings for parameter and return value documentation
- Generate documentation in Markdown or JSON format
- Run as an HTTP or STDIO-based server to retrieve documentation programmatically

## Installation

### Using pipx (Recommended)

```bash
pipx install codebase-examiner
```

### From Source

Clone the repository and install in development mode:

```bash
git clone https://github.com/username/codebase-examiner.git
cd codebase-examiner
pip install -e .
```

## Usage

### CLI Tool

Examine the current directory:

```bash
codebase-examiner examine
```

Examine a specific directory:

```bash
codebase-examiner examine --directory /path/to/project
```

Generate documentation in JSON format:

```bash
codebase-examiner examine --format json
```

Save documentation to a file:

```bash
codebase-examiner examine --output docs/codebase.md
```

Exclude additional directories:

```bash
codebase-examiner examine --exclude .venv --exclude tests --exclude docs
```

Generate markdown with only specific sections (e.g., title and modules):

```bash
codebase-examiner examine --section title --section modules
```

### HTTP Server

Start the HTTP server:

```bash
codebase-examiner serve --port 8080
```

Send a JSON-RPC request to `/jsonrpc`:

```bash
curl -X POST http://localhost:8080/jsonrpc \
     -H "Content-Type: application/json" \
     -d '{
       "jsonrpc": "2.0",
       "id": "1",
       "method": "tools/call",
       "params": {
         "name": "examine",
         "arguments": {
           "directory": ".",
           "exclude_dirs": [".venv"],
           "format": "markdown",
           "include_dotfiles": false
         }
       }
     }'
```

Response:

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "status": "success",
    "documentation": "# Codebase Documentation...",
    "modules_found": 5
  }
}
```


### STDIO Server

Start the STDIO server:

```bash
codebase-examiner-stdio
```

Send JSON-RPC commands to stdin and read JSON-RPC responses on stdout. For example:

```json
{ "jsonrpc": "2.0", "id": "1", "method": "tools/call", "params": { "name": "examine", "arguments": { "directory": ".", "exclude_dirs": [".venv"], "format": "markdown", "include_dotfiles": false } } }
```

```json
{ "jsonrpc": "2.0", "id": "1", "result": { "status": "success", "documentation": "# Codebase Documentation...", "modules_found": 5 } }
```

```json
{ "jsonrpc": "2.0", "id": "2", "method": "initialize", "params": {} }
```

```json
{ "jsonrpc": "2.0", "id": "2", "result": { "serverInfo": { "name": "Codebase Examiner", "version": "1.0.0" }, "capabilities": { "examineProvider": true }, "protocolVersion": null } }
```

```json
{ "jsonrpc": "2.0", "id": "3", "method": "exit", "params": {} }
```

```json
{ "jsonrpc": "2.0", "id": "3", "result": null }
```

Legacy command-based format is still supported for backward compatibility:

```json
{ "command": "examine", "directory": ".", "exclude_dirs": [".venv"], "format": "markdown", "include_dotfiles": false }
```

```json
{ "status": "success", "documentation": "# Codebase Documentation...", "modules_found": 5 }
```

## API Endpoints

When running as an HTTP server:

- `/jsonrpc` - JSON-RPC 2.0 endpoint for all operations

## Development

### Setup Development Environment

```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Project Structure

- `src/codebase_examiner/core/` - Core functionality  
  - `file_finder.py` - Finding Python files  
  - `code_inspector.py` - Extracting documentation from code  
  - `doc_generator.py` - Generating documentation output  
- `src/codebase_examiner/cli.py` - Command-line interface  
- `src/codebase_examiner/mcp.py` - HTTP server implementation  
- `src/codebase_examiner/mcp_stdio.py` - STDIO server implementation  
- `tests/` - Test suite

### Architecture

The Codebase Examiner is built with a layered architecture that separates concerns and allows for multiple interfaces to the core functionality.

#### C4 Model Diagrams

##### Context Diagram (Level 1)

```mermaid
C4Context
  title System Context Diagram for Codebase Examiner

  Person(user, "User", "A developer who needs to understand a Python codebase")
  System(llmAgent, "LLM Agent", "An AI agent that assists the user in understanding codebases")
  System(codebaseExaminer, "Codebase Examiner", "Analyzes Python codebases and generates comprehensive documentation")
  System_Ext(pythonCodebase, "Python Codebase", "The target Python project to be analyzed")

  Rel(user, codebaseExaminer, "Uses directly via CLI")
  Rel(user, llmAgent, "Interacts with")
  Rel(llmAgent, codebaseExaminer, "Uses via MCP protocol")
  Rel(codebaseExaminer, pythonCodebase, "Analyzes")
```

##### Container Diagram (Level 2)

```mermaid
C4Container
  title Container Diagram for Codebase Examiner

  Person(user, "User", "A developer who needs to understand a Python codebase")
  System(llmAgent, "LLM Agent", "An AI agent that assists the user in understanding codebases")

  System_Boundary(codebaseExaminer, "Codebase Examiner") {
    Container(cli, "CLI Runner", "Python/Typer", "Command-line interface for the Codebase Examiner")
    Container(httpServer, "HTTP Server", "Python/FastAPI", "HTTP-based MCP server for remote access")
    Container(stdioServer, "STDIO Server", "Python", "STDIO-based MCP server for direct integration")
    Container(rpcLayer, "RPC Layer", "Python", "Handles JSON-RPC requests and routes them to appropriate handlers")
    Container(examiner, "Examiner", "Python", "Core functionality for analyzing Python code and generating documentation")
  }

  System_Ext(pythonCodebase, "Python Codebase", "The target Python project to be analyzed")

  Rel(user, cli, "Uses directly", "Command line")
  Rel(user, llmAgent, "Interacts with")
  Rel(llmAgent, httpServer, "Uses via MCP protocol", "HTTP/JSON")
  Rel(llmAgent, stdioServer, "Uses via MCP protocol", "STDIO/JSON")

  Rel(cli, examiner, "Uses")
  Rel(httpServer, rpcLayer, "Uses")
  Rel(stdioServer, rpcLayer, "Uses")
  Rel(rpcLayer, examiner, "Uses")
  Rel(examiner, pythonCodebase, "Analyzes")
```

##### Component Diagram (Level 3)

```mermaid
C4Component
  title Component Diagram for Codebase Examiner

  Person(user, "User", "A developer who needs to understand a Python codebase")
  System(llmAgent, "LLM Agent", "An AI agent that assists the user in understanding codebases")

  Container_Boundary(cli, "CLI Runner") {
    Component(cliApp, "CLI Application", "Python/Typer", "Provides command-line interface")
  }

  Container_Boundary(transport, "Transport Layer") {
    Component(httpServer, "HTTP Server", "Python/FastAPI", "Handles HTTP requests")
    Component(stdioServer, "STDIO Server", "Python", "Handles STDIO communication")
  }

  Container_Boundary(rpc, "RPC Layer") {
    Component(jsonRpcHandler, "JSON-RPC Handler", "Python", "Processes JSON-RPC requests")
  }

  Container_Boundary(examiner, "Examiner") {
    Component(fileFinder, "File Finder", "Python", "Finds Python files in a directory tree")
    Component(codeInspector, "Code Inspector", "Python", "Extracts documentation from Python code")
    Component(docGenerator, "Documentation Generator", "Python", "Generates documentation in various formats")
  }

  Rel(user, cliApp, "Uses directly", "Command line")
  Rel(user, llmAgent, "Interacts with")
  Rel(llmAgent, httpServer, "Uses via MCP protocol", "HTTP/JSON")
  Rel(llmAgent, stdioServer, "Uses via MCP protocol", "STDIO/JSON")

  Rel(cliApp, codeInspector, "Uses")
  Rel(cliApp, docGenerator, "Uses")

  Rel(httpServer, jsonRpcHandler, "Uses")
  Rel(stdioServer, jsonRpcHandler, "Uses")

  Rel(jsonRpcHandler, codeInspector, "Uses")
  Rel(jsonRpcHandler, docGenerator, "Uses")

  Rel(codeInspector, fileFinder, "Uses")
```

## License

MIT
