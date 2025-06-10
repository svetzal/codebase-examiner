"""Base extractor interface for the Codebase Examiner."""

import abc
import enum
from pathlib import Path
from typing import Any, Set


class Capability(enum.Enum):
    """Capabilities provided by extractors."""

    CODE_STRUCTURE = "code_structure"  # Classes, functions, modules
    DEPENDENCIES = "dependencies"  # Import analysis, dependency graphs
    METRICS = "metrics"  # Lines of code, complexity, coverage
    SECURITY = "security"  # Vulnerability scanning, code quality
    DOCUMENTATION = "documentation"  # Docstring analysis, comment extraction
    STYLE = "style"  # Code formatting, linting issues


class BaseExtractor(abc.ABC):
    """Abstract base class defining the extractor interface.

    Extractors are responsible for analyzing files of specific types and
    extracting structured information from them.
    """

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
        """Check if this extractor can process the given file.

        Args:
            file_path (Path): Path to the file to check

        Returns:
            bool: True if the extractor can process the file, False otherwise
        """
        pass

    @abc.abstractmethod
    def extract(self, file_path: Path) -> Any:
        """Extract information from the given file.

        Args:
            file_path (Path): Path to the file to process

        Returns:
            Any: Extracted data from the file
        """
        pass
