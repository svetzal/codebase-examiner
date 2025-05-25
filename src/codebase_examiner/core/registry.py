"""Registry for code extractors."""

import os
import threading
from pathlib import Path
from typing import Dict, List, Optional, Set, Type

from codebase_examiner.core.extractors.base import BaseExtractor, Capability
from codebase_examiner.core.extractors.python_extractor import PythonExtractor


class ExtractorRegistry:
    """Registry for code extractors.
    
    This class provides a central registry for all extractors in the system.
    It manages extractor registration and discovery, and provides methods to
    find appropriate extractors for specific files or capabilities.
    
    The registry is implemented as a singleton to ensure consistent access
    across the application.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Create or return the singleton instance."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._extractors = {}
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        """Initialize the registry if not already initialized."""
        # Only initialize once
        if self._initialized:
            return
            
        self._extractors: Dict[str, BaseExtractor] = {}
        self._initialized = True
        
        # Register default extractors if environment variable is set or unspecified
        if os.environ.get("CODEBASE_EXAMINER_AUTO_REGISTER", "1") == "1":
            self.register_defaults()
    
    def register_extractor(self, extractor: BaseExtractor) -> None:
        """Register a new extractor.
        
        Args:
            extractor (BaseExtractor): The extractor instance to register
        """
        self._extractors[extractor.name] = extractor
    
    def register_defaults(self) -> None:
        """Register the default set of extractors."""
        self.register_extractor(PythonExtractor())
    
    def get_extractors_for_file(self, file_path: Path) -> List[BaseExtractor]:
        """Get all extractors that can process the given file.
        
        Args:
            file_path (Path): Path to the file
            
        Returns:
            List[BaseExtractor]: List of compatible extractors
        """
        return [
            extractor for extractor in self._extractors.values()
            if extractor.can_extract(file_path)
        ]
    
    def get_extractors_by_capability(self, capability: Capability) -> List[BaseExtractor]:
        """Get all extractors that support the given capability.
        
        Args:
            capability (Capability): The capability to filter by
            
        Returns:
            List[BaseExtractor]: List of extractors supporting the capability
        """
        return [
            extractor for extractor in self._extractors.values()
            if capability in extractor.get_capabilities()
        ]
    
    def list_extractors(self) -> List[BaseExtractor]:
        """Get all registered extractors.
        
        Returns:
            List[BaseExtractor]: List of all registered extractors
        """
        return list(self._extractors.values())
    
    def get_extractor(self, name: str) -> Optional[BaseExtractor]:
        """Get an extractor by name.
        
        Args:
            name (str): The name of the extractor
            
        Returns:
            Optional[BaseExtractor]: The extractor if found, None otherwise
        """
        return self._extractors.get(name)


# Create a default registry instance
default_registry = ExtractorRegistry()

# Factory functions for common configurations
def get_registry() -> ExtractorRegistry:
    """Get the default registry instance.
    
    Returns:
        ExtractorRegistry: The default registry instance
    """
    return default_registry

def create_registry() -> ExtractorRegistry:
    """Create a new empty registry instance.
    
    This is useful for testing or when complete control over the
    registered extractors is needed.
    
    Returns:
        ExtractorRegistry: A new registry instance
    """
    registry = ExtractorRegistry()
    registry._extractors.clear()  # Clear any defaults
    return registry