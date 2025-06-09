# Codebase Examiner Documentation

Welcome to the Codebase Examiner documentation! This site provides comprehensive information about the Codebase Examiner tool, its architecture, and how to use and extend it.

## What is Codebase Examiner?

Codebase Examiner is a powerful tool that analyzes Python codebases and generates comprehensive documentation about modules, classes, and functions. Designed to help both developers and AI agents understand large codebases despite context window limitations, it provides structured, information-dense summaries optimized for efficient navigation and comprehension.

### Overview

Codebase Examiner addresses a critical challenge in AI-powered coding: the inability of Large Language Models to process entire codebases due to context window limitations. By extracting essential structure and documentation from codebases and presenting it in an optimized format, the tool enables:

- **Efficient Navigation**: Quickly locate relevant code sections
- **Comprehensive Understanding**: Grasp system architecture and interdependencies
- **Optimized Token Usage**: Consume less context window space with structured summaries
- **Better Integration**: Understand how components interact within the system

The tool can be used as a standalone CLI application or integrated with AI systems through MCP (Machine Communication Protocol) over HTTP or STDIO.

### Key Features

- Find all Python files in a project directory tree (excluding .venv and other configurable directories)
- Extract documentation from modules, classes, and functions
- Parse Google-style docstrings for parameter and return value documentation
- Generate documentation in Markdown or JSON format
- Run as a CLI tool, MCP over HTTP, or MCP over STDIO

### Modular Architecture

Codebase Examiner has a modular, extensible architecture that includes:

- **Pluggable Extractors**: Specialized components for different types of code analysis
- **Extractor Registry**: Central system for managing and discovering extractors
- **Capability-Based Design**: Extractors declare their capabilities (CODE_STRUCTURE, DOCUMENTATION, etc.)
- **Unified Data Models**: Standardized structures for representing extracted information
- **Flexible Output**: Multiple renderer options for different documentation formats

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
- `--extractors`: Specify which extractors to use (e.g., python_extractor)
- `--capabilities`: Filter by capability type (e.g., CODE_STRUCTURE, DOCUMENTATION)

### list-extractors

List all available extractors and their capabilities.

```bash
codebase-examiner list-extractors
```

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
