"""Module for inspecting Python code and extracting documentation."""

import ast
import importlib.util
import inspect
import re
import sys
import warnings
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Union

# For backward compatibility
from codebase_examiner.core.filesystem_gateway import FileSystemGateway
from codebase_examiner.core.models import (
    FunctionDocumentation,
    ClassDocumentation,
    ModuleDocumentation,
    ExtractionResult,
)
from codebase_examiner.core.registry import get_registry


# Deprecated functions - keeping for backward compatibility
def parse_google_docstring(docstring: Optional[str]) -> Dict[str, Dict[str, str]]:
    """Parse a Google-style docstring to extract parameter and return descriptions.

    Args:
        docstring (Optional[str]): The docstring to parse.

    Returns:
        Dict[str, Dict[str, str]]: A dictionary with 'params' and 'returns' keys.
    """
    warnings.warn(
        "parse_google_docstring is deprecated and will be removed in a future version. "
        "Use a PythonExtractor instance instead.",
        DeprecationWarning, stacklevel=2
    )
    from codebase_examiner.core.extractors.python_extractor import PythonExtractor
    extractor = PythonExtractor()
    return extractor.parse_google_docstring(docstring)


def get_signature_string(obj: Any) -> str:
    """Get the signature of a callable object as a string.

    Args:
        obj (Any): The callable object.

    Returns:
        str: The signature as a string.
    """
    warnings.warn(
        "get_signature_string is deprecated and will be removed in a future version. "
        "Use a PythonExtractor instance instead.",
        DeprecationWarning, stacklevel=2
    )
    from codebase_examiner.core.extractors.python_extractor import PythonExtractor
    extractor = PythonExtractor()
    return extractor.get_signature_string(obj)


def inspect_function(func: Any, module_path: str) -> FunctionDocumentation:
    """Inspect a function and extract its documentation.

    Args:
        func (Any): The function to inspect.
        module_path (str): The path to the module containing the function.

    Returns:
        FunctionDocumentation: The extracted documentation.
    """
    warnings.warn(
        "inspect_function is deprecated and will be removed in a future version. "
        "Use a PythonExtractor instance instead.",
        DeprecationWarning, stacklevel=2
    )
    from codebase_examiner.core.extractors.python_extractor import PythonExtractor
    extractor = PythonExtractor()
    return extractor.inspect_function(func, module_path)


def inspect_class(cls: Any, module_path: str) -> ClassDocumentation:
    """Inspect a class and extract its documentation.

    Args:
        cls (Any): The class to inspect.
        module_path (str): The path to the module containing the class.

    Returns:
        ClassDocumentation: The extracted documentation.
    """
    warnings.warn(
        "inspect_class is deprecated and will be removed in a future version. "
        "Use a PythonExtractor instance instead.",
        DeprecationWarning, stacklevel=2
    )
    from codebase_examiner.core.extractors.python_extractor import PythonExtractor
    extractor = PythonExtractor()
    return extractor.inspect_class(cls, module_path)


def load_module_from_file(file_path: Path) -> Tuple[Any, str]:
    """Load a Python module from a file path.

    Args:
        file_path (Path): The path to the Python file.

    Returns:
        Tuple[Any, str]: The loaded module and its name.
    """
    warnings.warn(
        "load_module_from_file is deprecated and will be removed in a future version. "
        "Use a PythonExtractor instance instead.",
        DeprecationWarning, stacklevel=2
    )
    from codebase_examiner.core.extractors.python_extractor import PythonExtractor
    extractor = PythonExtractor()
    return extractor.load_module_from_file(file_path)


def inspect_module(file_path: Path) -> ModuleDocumentation:
    """Inspect a Python module and extract its documentation.

    Args:
        file_path (Path): The path to the Python file.

    Returns:
        ModuleDocumentation: The extracted documentation.
    """
    warnings.warn(
        "inspect_module is deprecated and will be removed in a future version. "
        "Use a PythonExtractor instance instead.",
        DeprecationWarning, stacklevel=2
    )
    from codebase_examiner.core.extractors.python_extractor import PythonExtractor
    extractor = PythonExtractor()
    return extractor.inspect_module(file_path)


def parse_module_with_ast(file_path: Path) -> ModuleDocumentation:
    """Parse a Python module using AST when import is not possible.

    Args:
        file_path (Path): The path to the Python file.

    Returns:
        ModuleDocumentation: The extracted documentation.
    """
    warnings.warn(
        "parse_module_with_ast is deprecated and will be removed in a future version. "
        "Use a PythonExtractor instance instead.",
        DeprecationWarning, stacklevel=2
    )
    from codebase_examiner.core.extractors.python_extractor import PythonExtractor
    extractor = PythonExtractor()
    return extractor.parse_module_with_ast(file_path)


def extract_function_info_from_ast(node: ast.FunctionDef, module_path: str) -> FunctionDocumentation:
    """Extract function information from an AST node.

    Args:
        node (ast.FunctionDef): The function definition node.
        module_path (str): The path to the module containing the function.

    Returns:
        FunctionDocumentation: The extracted function documentation.
    """
    warnings.warn(
        "extract_function_info_from_ast is deprecated and will be removed in a future version. "
        "Use a PythonExtractor instance instead.",
        DeprecationWarning, stacklevel=2
    )
    from codebase_examiner.core.extractors.python_extractor import PythonExtractor
    extractor = PythonExtractor()
    return extractor.extract_function_info_from_ast(node, module_path)


def extract_class_info_from_ast(node: ast.ClassDef, module_path: str) -> ClassDocumentation:
    """Extract class information from an AST node.

    Args:
        node (ast.ClassDef): The class definition node.
        module_path (str): The path to the module containing the class.

    Returns:
        ClassDocumentation: The extracted class documentation.
    """
    warnings.warn(
        "extract_class_info_from_ast is deprecated and will be removed in a future version. "
        "Use a PythonExtractor instance instead.",
        DeprecationWarning, stacklevel=2
    )
    from codebase_examiner.core.extractors.python_extractor import PythonExtractor
    extractor = PythonExtractor()
    return extractor.extract_class_info_from_ast(node, module_path)


class CodebaseInspector:
    """Class to orchestrate the inspection process.

    This class coordinates the analysis of files in a codebase using
    registered extractors to generate comprehensive documentation.
    """

    def __init__(self, registry=None, fs_gateway=None):
        """Initialize the inspector with a registry.

        Args:
            registry: The extractor registry to use. If None, uses the default registry.
            fs_gateway (Optional[FileSystemGateway]): The filesystem gateway to use.
                If None, a new instance will be created.
        """
        self._registry = registry or get_registry()
        self._fs_gateway = fs_gateway or FileSystemGateway()

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
        from codebase_examiner.core.file_finder import find_python_files

        # For now, we only handle Python files
        files = find_python_files(directory, exclude_dirs, exclude_dotfiles, self._fs_gateway)
        return self.inspect_files(files)

    def inspect_files(self, files: List[Path]) -> ExtractionResult:
        """Inspect a list of files using appropriate extractors.

        Args:
            files (List[Path]): The files to inspect

        Returns:
            ExtractionResult: The combined results from all extractors
        """
        result = ExtractionResult(
            file_count=len(files),
            extractors_used=[]
        )

        for file_path in files:
            extractors = self._registry.get_extractors_for_file(file_path)

            # Track which extractors were used
            for extractor in extractors:
                if extractor.name not in result.extractors_used:
                    result.extractors_used.append(extractor.name)

            # Process the file with each compatible extractor
            for extractor in extractors:
                try:
                    extracted_data = extractor.extract(file_path, self._fs_gateway)
                    if isinstance(extracted_data, list):
                        result.data.extend(extracted_data)
                    else:
                        result.data.append(extracted_data)
                except Exception as e:
                    print(f"Error using {extractor.name} on {file_path}: {e}")

        return result


def inspect_codebase(
        directory: str = ".",
        exclude_dirs: Set[str] = None,
        exclude_dotfiles: bool = True,
        fs_gateway: Optional[FileSystemGateway] = None
) -> Union[List[ModuleDocumentation], ExtractionResult]:
    """Inspect a Python codebase and extract documentation.

    This function is maintained for backward compatibility. It now uses the
    new CodebaseInspector class internally to leverage the modular architecture.

    Args:
        directory (str): The root directory of the codebase. Defaults to current directory.
        exclude_dirs (Set[str], optional): Set of directory names to exclude from the search.
        exclude_dotfiles (bool): Whether to exclude all files and directories starting with a dot.
            Defaults to True.
        fs_gateway (Optional[FileSystemGateway]): The filesystem gateway to use.
            If None, a new instance will be created.

    Returns:
        List[ModuleDocumentation]: Documentation for all modules in the codebase.
    """
    inspector = CodebaseInspector(fs_gateway=fs_gateway)
    result = inspector.inspect_directory(directory, exclude_dirs, exclude_dotfiles)

    # For backward compatibility, return a list of module documentation
    modules = result.get_modules()
    return modules
