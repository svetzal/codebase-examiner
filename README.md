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

### HTTP Server

Start the HTTP server:

```bash
codebase-examiner serve --port 8080
```

Send a POST request to `/examine`:

```bash
curl -X POST http://localhost:8080/examine \
     -H "Content-Type: application/json" \
     -d '{"directory":".", "exclude_dirs":[".venv"], "format":"markdown", "include_dotfiles":false}'
```

Response:

```json
{
  "documentation": "# Codebase Documentation...",
  "modules_found": 5
}
```

### STDIO Server

Start the STDIO server:

```bash
codebase-examiner-stdio
```

Send JSON commands to stdin and read JSON responses on stdout. For example:

```json
{ "command": "examine", "directory": ".", "exclude_dirs": [".venv"], "format": "markdown", "include_dotfiles": false }
```

```json
{ "status": "success", "documentation": "# Codebase Documentation...", "modules_found": 5 }
```

```json
{ "command": "ping" }
```

```json
{ "status": "success", "message": "pong" }
```

```json
{ "command": "exit" }
```

## API Endpoints

When running as an HTTP server:

- `/examine` - Examine a codebase and return documentation

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

## License

MIT
