# Codebase Examiner Documentation

Welcome to the Codebase Examiner documentation! This site provides comprehensive information about the Codebase Examiner tool, its architecture, and how to use and extend it.

## What is Codebase Examiner?

Codebase Examiner is a command-line tool and MCP server that analyzes Python codebases to generate comprehensive documentation. The tool scans Python files to extract information about modules, classes, functions, and their documentation, then outputs structured documentation in markdown or JSON format.

### Key Features

- Find all Python files in a project directory tree (excluding .venv and other configurable directories)
- Extract documentation from modules, classes, and functions
- Parse Google-style docstrings for parameter and return value documentation
- Generate documentation in Markdown or JSON format
- Run as a CLI tool, MCP over HTTP, or MCP over STDIO

## Getting Started

### Installation

You can install Codebase Examiner using pipx:

```bash
pipx install codebase-examiner
```

This makes the `codebase-examiner` command available in your terminal.

### Basic Usage

To generate documentation for a Python project:

```bash
codebase-examiner examine --directory /path/to/your/project --output docs.md
```

This will analyze all Python files in the specified directory and generate markdown documentation.

## Documentation Sections

- [Architecture](architecture.md) - Detailed explanation of the codebase architecture with diagrams
- [Extending for Other Languages](extending.md) - Guide on how to extend Codebase Examiner for languages other than Python
- [API Reference](api-reference.md) - Detailed API documentation for developers

## Command-Line Interface

Codebase Examiner provides several commands:

### examine

Analyze a Python codebase and generate documentation.

```bash
codebase-examiner examine [OPTIONS]
```

Options:
- `--directory`, `-d`: The directory to examine (default: current directory)
- `--format`, `-f`: Output format (markdown or json) (default: markdown)
- `--output`, `-o`: Output file path (default: print to console)
- `--exclude`, `-e`: Directories to exclude (default: .venv)
- `--include-dotfiles`: Include files and directories starting with a dot
- `--section`, `-s`: Sections to include in order (title, toc, modules)

### serve

Run the Codebase Examiner as an MCP server over HTTP.

```bash
codebase-examiner serve [OPTIONS]
```

Options:
- `--port`, `-p`: Port to run the MCP server on (default: 8080)

### serve-stdio

Run the Codebase Examiner as an MCP server over standard input/output.

```bash
codebase-examiner serve-stdio
```

## License

Codebase Examiner is released under the MIT License.
