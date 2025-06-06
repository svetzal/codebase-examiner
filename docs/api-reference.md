# API Reference

This document provides detailed API documentation for the Codebase Examiner's core components. It's intended for developers who want to use or extend the Codebase Examiner programmatically.

## Core Components

### CodebaseInspector

The `CodebaseInspector` class is the main orchestrator for the inspection process.

```python
class CodebaseInspector:
    def __init__(self, registry=None, fs_gateway=None):
        """Initialize the inspector with a registry.

        Args:
            registry: The extractor registry to use. If None, uses the default registry.
            fs_gateway (Optional[FileSystemGateway]): The filesystem gateway to use.
                If None, a new instance will be created.
        """
        
    def inspect_directory(
            self,
            directory: str = ".",
            exclude_dirs: Set[str] = None,
            exclude_dotfiles: bool = True
    ) -> ExtractionResult:
        """Inspect a directory and extract information from all relevant files.

        Args:
            directory (str): The directory to inspect. Defaults to the current directory.
            exclude_dirs (Set[str]): Set of directory names to exclude.
            exclude_dotfiles (bool): Whether to exclude dotfiles. Defaults to True.

        Returns:
            ExtractionResult: The combined results from all extractors
        """
        
    def inspect_files(self, files: List[Path]) -> ExtractionResult:
        """Inspect a list of files using appropriate extractors.

        Args:
            files (List[Path]): The files to inspect

        Returns:
            ExtractionResult: The combined results from all extractors
        """
```

#### Example Usage

```python
from codebase_examiner.core.code_inspector import CodebaseInspector

# Create an inspector
inspector = CodebaseInspector()

# Inspect a directory
result = inspector.inspect_directory(
    directory="/path/to/project",
    exclude_dirs={".venv", "tests"},
    exclude_dotfiles=True
)

# Get all modules
modules = result.get_modules()

# Print module names
for module in modules:
    print(f"Module: {module.name}")
    print(f"  Functions: {len(module.functions)}")
    print(f"  Classes: {len(module.classes)}")
```

### ExaminerTool

The `ExaminerTool` class is the main entry point for the MCP server interfaces.

```python
class ExaminerTool(LLMTool):
    def run(self, directory: str = ".", exclude_dirs: List[str] = None, format_type: str = "markdown", include_dotfiles: bool = False) -> Dict[str, Any]:
        """Examines a Python codebase and generates documentation.

        Parameters
        ----------
        directory : str, optional
            The directory to examine, by default "."
        exclude_dirs : List[str], optional
            Directories to exclude from examination, by default [".venv", ".git", "__pycache__", "tests", "build", "dist"]
        format_type : str, optional
            The format of the generated documentation, by default "markdown"
        include_dotfiles : bool, optional
            Whether to include dotfiles in the examination, by default False

        Returns
        -------
        dict
            A dictionary containing the generated documentation and metadata
        """
```

### FileFinder

The `FileFinder` module provides functions for finding Python files in a directory structure.

```python
def find_python_files(
        directory: str = ".",
        exclude_dirs: Set[str] = None,
        exclude_dotfiles: bool = True,
        fs_gateway: Optional[FileSystemGateway] = None,
) -> List[pathlib.Path]:
    """Find all Python files in the given directory and its subdirectories.

    Args:
        directory (str): The root directory to search in. Defaults to current directory.
        exclude_dirs (Set[str]): Set of directory names to exclude from the search.
            Defaults to {".venv", ".git", "__pycache__", "tests", "build", "dist"}.
        exclude_dotfiles (bool): Whether to exclude all files and directories starting with a dot.
            Defaults to True.
        fs_gateway (Optional[FileSystemGateway]): The filesystem gateway to use.
            If None, a new instance will be created.

    Returns:
        List[pathlib.Path]: A list of paths to Python files, excluding test files.
    """
```

### DocGenerator

The `DocGenerator` module provides functions for generating documentation from extraction results.

```python
def generate_documentation(
    modules_or_result: Union[List[ModuleDocumentation], ExtractionResult], 
    format: str = "markdown"
) -> str:
    """Generate documentation in the specified format.

    Args:
        modules_or_result (Union[List[ModuleDocumentation], ExtractionResult]): List of module documentation objects
            or an ExtractionResult containing them.
        format (str, optional): Output format - "markdown" or "json". Defaults to "markdown".

    Returns:
        str: Generated documentation.
    """

def generate_markdown_documentation(
    modules_or_result: Union[List[ModuleDocumentation], ExtractionResult],
    sections: Optional[List[SectionGenerator]] = None,
) -> str:
    """Generate markdown documentation by combining configured sections.

    Args:
        modules_or_result (Union[List[ModuleDocumentation], ExtractionResult]): List of module documentation objects
            or an ExtractionResult containing them.
        sections (Optional[List[SectionGenerator]]): Optional list of section generators.
            Defaults to the standard title, table of contents, and modules sections.

    Returns:
        str: Markdown formatted documentation.
    """

def generate_json_documentation(modules_or_result: Union[List[ModuleDocumentation], ExtractionResult]) -> str:
    """Generate JSON documentation from module documentation.

    Args:
        modules_or_result (Union[List[ModuleDocumentation], ExtractionResult]): List of module documentation objects
            or an ExtractionResult containing them.

    Returns:
        str: JSON formatted documentation.
    """
```

## Data Models

### ModuleDocumentation

Represents documentation for a Python module.

```python
class ModuleDocumentation(BaseModel):
    name: str
    docstring: Optional[str] = None
    file_path: str
    functions: List[FunctionDocumentation] = []
    classes: List[ClassDocumentation] = []
    extractor_name: str
    capability: Capability
```

### ClassDocumentation

Represents documentation for a Python class.

```python
class ClassDocumentation(BaseModel):
    name: str
    docstring: Optional[str] = None
    methods: List[FunctionDocumentation] = []
    module_path: str
    file_path: str
    extractor_name: str
    capability: Capability
```

### FunctionDocumentation

Represents documentation for a Python function or method.

```python
class FunctionDocumentation(BaseModel):
    name: str
    docstring: Optional[str] = None
    signature: str
    parameters: Dict[str, Dict[str, Any]] = {}
    return_type: Optional[str] = None
    return_description: Optional[str] = None
    module_path: str
    file_path: str
    extractor_name: str
    capability: Capability
```

### ExtractionResult

Represents the combined results from all extractors.

```python
class ExtractionResult(BaseModel):
    file_count: int
    extractors_used: List[str] = []
    data: List[Union[ModuleDocumentation, Any]] = []

    def get_modules(self) -> List[ModuleDocumentation]:
        """Get all ModuleDocumentation objects from the data."""
```

## Extractor System

### BaseExtractor

The abstract base class that all extractors must implement.

```python
class BaseExtractor(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Return the name of the extractor."""
        pass

    @property
    @abc.abstractmethod
    def version(self) -> str:
        """Return the version of the extractor."""
        pass

    @property
    @abc.abstractmethod
    def supported_extensions(self) -> Set[str]:
        """Return the set of file extensions supported by this extractor."""
        pass

    @abc.abstractmethod
    def get_capabilities(self) -> Set[Capability]:
        """Return the set of capabilities supported by this extractor."""
        pass

    @abc.abstractmethod
    def can_extract(self, file_path: Path) -> bool:
        """Check if this extractor can process the given file."""
        pass

    @abc.abstractmethod
    def extract(self, file_path: Path) -> Any:
        """Extract information from the given file."""
        pass
```

### Capability

Enum defining the capabilities that extractors can provide.

```python
class Capability(enum.Enum):
    CODE_STRUCTURE = "code_structure"  # Classes, functions, modules
    DEPENDENCIES = "dependencies"      # Import analysis, dependency graphs
    METRICS = "metrics"               # Lines of code, complexity, coverage
    SECURITY = "security"             # Vulnerability scanning, code quality
    DOCUMENTATION = "documentation"   # Docstring analysis, comment extraction
    STYLE = "style"                   # Code formatting, linting issues
```

### ExtractorRegistry

Registry for managing extractors.

```python
class ExtractorRegistry:
    def __init__(self):
        """Initialize an empty registry."""
        
    def register(self, extractor: BaseExtractor) -> None:
        """Register an extractor.

        Args:
            extractor (BaseExtractor): The extractor to register.
        """
        
    def get_extractors_for_file(self, file_path: Path) -> List[BaseExtractor]:
        """Get all extractors that can process the given file.

        Args:
            file_path (Path): The file path to check.

        Returns:
            List[BaseExtractor]: List of extractors that can process the file.
        """
```

## Section Generators

### SectionGenerator

The abstract base class for documentation section generators.

```python
class SectionGenerator(abc.ABC):
    @abc.abstractmethod
    def generate(self, modules: List[ModuleDocumentation]) -> str:
        """Generate the section content."""
        pass
```

### Built-in Section Generators

```python
class TitleSection(SectionGenerator):
    """Generate the title section."""
    def generate(self, modules: List[ModuleDocumentation]) -> str:
        """Generate the section content."""

class TableOfContentsSection(SectionGenerator):
    """Generate the table of contents section."""
    def generate(self, modules: List[ModuleDocumentation]) -> str:
        """Generate the section content."""

class ModulesSection(SectionGenerator):
    """Generate the full modules documentation section, including functions and classes."""
    def generate(self, modules: List[ModuleDocumentation]) -> str:
        """Generate the section content."""
```

## FileSystemGateway

The `FileSystemGateway` provides an abstraction layer for file system operations.

```python
class FileSystemGateway:
    def path_exists(self, path: Path) -> bool:
        """Check if a path exists."""
        
    def read_file(self, path: Path) -> str:
        """Read a file and return its contents as a string."""
        
    def read_config(self, path: Path) -> configparser.ConfigParser:
        """Read a configuration file."""
        
    def resolve_path(self, path: Path) -> Path:
        """Resolve a path to its absolute form."""
        
    def join_paths(self, *paths) -> Path:
        """Join path components."""
        
    def get_file_suffix(self, path: Path) -> str:
        """Get the file suffix (extension)."""
        
    def get_file_stem(self, path: Path) -> str:
        """Get the file stem (name without extension)."""
        
    def walk_directory(self, directory: Path, exclude_dirs: Set[str] = None) -> Iterator[Tuple[Path, List[str], List[str]]]:
        """Walk a directory tree, similar to os.walk."""
        
    def load_module(self, module_name: str, file_path: Path) -> Any:
        """Load a Python module from a file path."""
```

## Command-Line Interface

The CLI module provides the command-line interface for the Codebase Examiner.

```python
@app.command()
def examine(
        directory: str = typer.Option(".", "--directory", "-d", help="The directory to examine"),
        output_format: str = typer.Option("markdown", "--format", "-f", help="Output format (markdown or json)"),
        output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path"),
        exclude: List[str] = typer.Option([".venv"], "--exclude", "-e", help="Directories to exclude"),
        include_dotfiles: bool = typer.Option(False, "--include-dotfiles",
                                              help="Include files and directories starting with a dot"),
        sections: Optional[List[str]] = typer.Option(
            None,
            "--section",
            "-s",
            help="Sections to include in order (title, toc, modules)",
        ),
):
    """Examine a Python codebase and generate documentation."""

@app.command()
def serve(
        port: int = typer.Option(8080, "--port", "-p", help="Port to run the MCP server on"),
):
    """Run the Codebase Examiner as an MCP server over HTTP."""

@app.command()
def serve_stdio():
    """Run the Codebase Examiner as an MCP server over standard input/output."""
```

## MCP Server Integration

The Codebase Examiner can be used as an MCP server, providing tools for LLMs to analyze codebases.

### MCP Tool Descriptor

```python
{
    "type": "function",
    "function": {
        "name": "examine_codebase",
        "description": "Examine a Python codebase and generate documentation. This tool analyzes Python files to extract information about modules, classes, functions, and their documentation.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "The directory to examine. Default is the current directory."
                },
                "exclude_dirs": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Directories to exclude from examination. Default is ['.venv', '.git', '__pycache__', 'tests', 'build', 'dist']."
                },
                "format_type": {
                    "type": "string",
                    "enum": ["markdown", "json"],
                    "description": "The format of the generated documentation. Default is 'markdown'."
                },
                "include_dotfiles": {
                    "type": "boolean",
                    "description": "Whether to include dotfiles in the examination. Default is false."
                }
            },
            "required": []
        }
    }
}
```

## Programmatic Usage Examples

### Basic Usage

```python
from codebase_examiner.core.code_inspector import CodebaseInspector
from codebase_examiner.core.doc_generator import generate_documentation

# Create an inspector
inspector = CodebaseInspector()

# Inspect a directory
result = inspector.inspect_directory(
    directory="/path/to/project",
    exclude_dirs={".venv", "tests"},
    exclude_dotfiles=True
)

# Generate markdown documentation
markdown_doc = generate_documentation(result, format="markdown")

# Save to a file
with open("documentation.md", "w") as f:
    f.write(markdown_doc)
```

### Custom Section Generators

```python
from codebase_examiner.core.code_inspector import CodebaseInspector
from codebase_examiner.core.doc_generator import generate_markdown_documentation
from codebase_examiner.core.section_generators import SectionGenerator, TitleSection
from typing import List
from codebase_examiner.core.models import ModuleDocumentation

# Create a custom section generator
class CustomSection(SectionGenerator):
    def generate(self, modules: List[ModuleDocumentation]) -> str:
        content = "## Custom Section\n\n"
        content += "This is a custom section with some statistics:\n\n"
        content += f"- Total modules: {len(modules)}\n"
        content += f"- Total functions: {sum(len(m.functions) for m in modules)}\n"
        content += f"- Total classes: {sum(len(m.classes) for m in modules)}\n\n"
        return content

# Create an inspector
inspector = CodebaseInspector()

# Inspect a directory
result = inspector.inspect_directory("/path/to/project")

# Generate markdown with custom sections
markdown_doc = generate_markdown_documentation(
    result,
    sections=[
        TitleSection(),
        CustomSection()
    ]
)

# Print the documentation
print(markdown_doc)
```

### Creating a Custom Extractor

```python
from pathlib import Path
from typing import Any, Set
from codebase_examiner.core.extractors.base import BaseExtractor, Capability
from codebase_examiner.core.models import ModuleDocumentation

class CustomExtractor(BaseExtractor):
    @property
    def name(self) -> str:
        return "custom"

    @property
    def version(self) -> str:
        return "0.1.0"

    @property
    def supported_extensions(self) -> Set[str]:
        return {".custom"}

    def get_capabilities(self) -> Set[Capability]:
        return {Capability.CODE_STRUCTURE}

    def can_extract(self, file_path: Path) -> bool:
        return file_path.suffix in self.supported_extensions

    def extract(self, file_path: Path) -> ModuleDocumentation:
        # Custom extraction logic here
        return ModuleDocumentation(
            name=file_path.stem,
            docstring="Custom module",
            file_path=str(file_path),
            functions=[],
            classes=[],
            extractor_name=self.name,
            capability=Capability.CODE_STRUCTURE
        )

# Register the extractor
from codebase_examiner.core.registry import ExtractorRegistry
registry = ExtractorRegistry()
registry.register(CustomExtractor())

# Use the registry with an inspector
from codebase_examiner.core.code_inspector import CodebaseInspector
inspector = CodebaseInspector(registry=registry)
```