# Extending Codebase Examiner

This guide explains how to extend Codebase Examiner to support additional programming languages beyond Python. The modular architecture of Codebase Examiner makes it relatively straightforward to add support for new languages by implementing custom extractors.

## Understanding the Extractor System

Codebase Examiner uses a plugin-based architecture for language support. Each language is handled by an extractor that implements the `BaseExtractor` interface. The current implementation includes a `PythonExtractor` for Python files, but you can add extractors for other languages.

### The BaseExtractor Interface

All extractors must implement the `BaseExtractor` abstract base class, which defines the following methods and properties:

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

### Capabilities

Extractors can provide different capabilities, defined in the `Capability` enum:

```python
class Capability(enum.Enum):
    CODE_STRUCTURE = "code_structure"  # Classes, functions, modules
    DEPENDENCIES = "dependencies"      # Import analysis, dependency graphs
    METRICS = "metrics"               # Lines of code, complexity, coverage
    SECURITY = "security"             # Vulnerability scanning, code quality
    DOCUMENTATION = "documentation"   # Docstring analysis, comment extraction
    STYLE = "style"                   # Code formatting, linting issues
```

## Creating a New Language Extractor

To add support for a new programming language, follow these steps:

### 1. Create a New Extractor Class

Create a new Python file in the `src/codebase_examiner/core/extractors` directory for your language extractor. For example, `javascript_extractor.py` for JavaScript support.

```python
"""JavaScript code extractor implementation."""

from pathlib import Path
from typing import Any, Set, Optional

from codebase_examiner.core.extractors.base import BaseExtractor, Capability
from codebase_examiner.core.filesystem_gateway import FileSystemGateway
from codebase_examiner.core.models import ModuleDocumentation

class JavaScriptExtractor(BaseExtractor):
    """Extractor for JavaScript code files."""

    @property
    def name(self) -> str:
        """Return the name of the extractor."""
        return "javascript"

    @property
    def version(self) -> str:
        """Return the version of the extractor."""
        return "0.1.0"

    @property
    def supported_extensions(self) -> Set[str]:
        """Return the set of file extensions supported by this extractor."""
        return {".js", ".jsx"}

    def get_capabilities(self) -> Set[Capability]:
        """Return the set of capabilities supported by this extractor."""
        return {Capability.CODE_STRUCTURE}

    def can_extract(self, file_path: Path, fs_gateway: Optional[FileSystemGateway] = None) -> bool:
        """Check if this extractor can process the given file."""
        if fs_gateway is None:
            fs_gateway = FileSystemGateway()
        return fs_gateway.get_file_suffix(file_path) in self.supported_extensions

    def extract(self, file_path: Path, fs_gateway: Optional[FileSystemGateway] = None) -> ModuleDocumentation:
        """Extract information from the given JavaScript file."""
        # Implement JavaScript parsing logic here
        # ...
```

### 2. Implement the Extraction Logic

The most important method to implement is `extract()`, which should:

1. Parse the file to extract information about modules, classes, functions, etc.
2. Create and return a `ModuleDocumentation` object with the extracted information

For JavaScript, you might use a library like `esprima` or `acorn` to parse the JavaScript code. For other languages, you'll need to find appropriate parsing libraries or implement your own parser.

```python
def extract(self, file_path: Path, fs_gateway: Optional[FileSystemGateway] = None) -> ModuleDocumentation:
    """Extract information from the given JavaScript file."""
    if fs_gateway is None:
        fs_gateway = FileSystemGateway()
    
    # Read the file content
    content = fs_gateway.read_file(file_path)
    
    # Parse the JavaScript code (example using a hypothetical js_parser)
    import js_parser
    ast = js_parser.parse(content)
    
    # Extract module information
    module_name = fs_gateway.get_file_stem(file_path)
    docstring = self._extract_module_docstring(ast)
    
    # Extract functions and classes
    functions = self._extract_functions(ast, str(file_path))
    classes = self._extract_classes(ast, str(file_path))
    
    # Create and return the ModuleDocumentation
    return ModuleDocumentation(
        name=module_name,
        docstring=docstring,
        file_path=str(file_path),
        functions=functions,
        classes=classes,
        extractor_name=self.name,
        capability=Capability.CODE_STRUCTURE
    )
```

### 3. Register Your Extractor

To make your extractor available to the system, you need to register it in the `src/codebase_examiner/core/registry.py` file:

```python
def get_registry():
    """Get the default registry with all available extractors."""
    if not hasattr(get_registry, "_registry"):
        from codebase_examiner.core.extractors.python_extractor import PythonExtractor
        from codebase_examiner.core.extractors.javascript_extractor import JavaScriptExtractor
        
        registry = ExtractorRegistry()
        registry.register(PythonExtractor())
        registry.register(JavaScriptExtractor())  # Register your new extractor
        
        get_registry._registry = registry
    
    return get_registry._registry
```

### 4. Update the File Finder (Optional)

If your language has specific conventions for test files or other special files, you might need to update the `find_python_files` function in `src/codebase_examiner/core/file_finder.py` to handle these conventions. Consider renaming this function to something more generic like `find_code_files`.

## Example: Adding TypeScript Support

Here's a more concrete example of how you might implement a TypeScript extractor:

```python
"""TypeScript code extractor implementation."""

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from codebase_examiner.core.extractors.base import BaseExtractor, Capability
from codebase_examiner.core.filesystem_gateway import FileSystemGateway
from codebase_examiner.core.models import (
    ClassDocumentation,
    FunctionDocumentation,
    ModuleDocumentation,
)

class TypeScriptExtractor(BaseExtractor):
    """Extractor for TypeScript code files."""

    @property
    def name(self) -> str:
        """Return the name of the extractor."""
        return "typescript"

    @property
    def version(self) -> str:
        """Return the version of the extractor."""
        return "0.1.0"

    @property
    def supported_extensions(self) -> Set[str]:
        """Return the set of file extensions supported by this extractor."""
        return {".ts", ".tsx"}

    def get_capabilities(self) -> Set[Capability]:
        """Return the set of capabilities supported by this extractor."""
        return {Capability.CODE_STRUCTURE}

    def can_extract(self, file_path: Path, fs_gateway: Optional[FileSystemGateway] = None) -> bool:
        """Check if this extractor can process the given file."""
        if fs_gateway is None:
            fs_gateway = FileSystemGateway()
        return fs_gateway.get_file_suffix(file_path) in self.supported_extensions

    def extract(self, file_path: Path, fs_gateway: Optional[FileSystemGateway] = None) -> ModuleDocumentation:
        """Extract information from the given TypeScript file."""
        if fs_gateway is None:
            fs_gateway = FileSystemGateway()
        
        # Use TypeScript Compiler API via a Node.js script to parse the file
        # This is just an example approach - you might use a Python TypeScript parser instead
        result = subprocess.run(
            ["node", "ts_parser.js", str(file_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            # Handle error
            return ModuleDocumentation(
                name=file_path.stem,
                docstring=None,
                file_path=str(file_path),
                functions=[],
                classes=[],
                extractor_name=self.name,
                capability=Capability.CODE_STRUCTURE
            )
        
        # Parse the JSON output from the Node.js script
        parsed_data = json.loads(result.stdout)
        
        # Extract module information
        module_name = parsed_data.get("name", file_path.stem)
        docstring = parsed_data.get("docstring")
        
        # Extract functions
        functions = []
        for func_data in parsed_data.get("functions", []):
            functions.append(FunctionDocumentation(
                name=func_data["name"],
                docstring=func_data.get("docstring"),
                signature=func_data.get("signature", "()"),
                parameters=func_data.get("parameters", {}),
                return_type=func_data.get("returnType"),
                return_description=func_data.get("returnDescription"),
                module_path=str(file_path),
                file_path=str(file_path),
                extractor_name=self.name,
                capability=Capability.CODE_STRUCTURE
            ))
        
        # Extract classes
        classes = []
        for class_data in parsed_data.get("classes", []):
            # Extract methods
            methods = []
            for method_data in class_data.get("methods", []):
                methods.append(FunctionDocumentation(
                    name=method_data["name"],
                    docstring=method_data.get("docstring"),
                    signature=method_data.get("signature", "()"),
                    parameters=method_data.get("parameters", {}),
                    return_type=method_data.get("returnType"),
                    return_description=method_data.get("returnDescription"),
                    module_path=str(file_path),
                    file_path=str(file_path),
                    extractor_name=self.name,
                    capability=Capability.CODE_STRUCTURE
                ))
            
            classes.append(ClassDocumentation(
                name=class_data["name"],
                docstring=class_data.get("docstring"),
                methods=methods,
                module_path=str(file_path),
                file_path=str(file_path),
                extractor_name=self.name,
                capability=Capability.CODE_STRUCTURE
            ))
        
        # Create and return the ModuleDocumentation
        return ModuleDocumentation(
            name=module_name,
            docstring=docstring,
            file_path=str(file_path),
            functions=functions,
            classes=classes,
            extractor_name=self.name,
            capability=Capability.CODE_STRUCTURE
        )
```

## Best Practices for Implementing Extractors

1. **Handle errors gracefully**: Your extractor should handle parsing errors and return a valid ModuleDocumentation object even if parsing fails.

2. **Use appropriate parsing tools**: Choose parsing libraries that are well-maintained and accurate for the language you're supporting.

3. **Support both runtime and static analysis**: When possible, implement both runtime inspection (for loaded modules) and static analysis (for files that can't be loaded).

4. **Document your extractor**: Include clear documentation about how your extractor works and any dependencies it requires.

5. **Write tests**: Create comprehensive tests for your extractor to ensure it handles different code patterns correctly.

6. **Consider documentation conventions**: Different languages have different documentation conventions (like JSDoc for JavaScript). Make sure your extractor understands these conventions.

## Adding New Capabilities

Beyond adding support for new languages, you can also extend existing extractors with new capabilities:

1. **Dependency Analysis**: Extract and visualize import/require relationships between modules.

2. **Metrics Collection**: Calculate code metrics like cyclomatic complexity, lines of code, etc.

3. **Security Analysis**: Identify potential security issues in the code.

4. **Style Checking**: Analyze code style and formatting issues.

To add a new capability, you'll need to:

1. Update the extractor to implement the new capability
2. Update the `get_capabilities()` method to include the new capability
3. Extend the documentation generation to include the new information

## Conclusion

Extending Codebase Examiner to support new languages involves implementing a custom extractor that can parse and extract information from files in that language. By following the BaseExtractor interface and understanding the data model, you can add support for virtually any programming language.

Remember that the quality of the documentation generated depends on the quality of the extraction process, so invest time in creating a robust parser for your target language.