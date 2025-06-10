"""Data models for the Codebase Examiner."""

import datetime
from typing import Dict, List, Any, Optional

from pydantic import BaseModel, Field

from codebase_examiner.core.extractors.base import Capability


class ExtractedData(BaseModel):
    """Base class for all extracted data."""

    file_path: str
    extractor_name: str
    capability: Capability

    def model_dump(self):
        """Convert the model to a dictionary."""
        data = super().model_dump()
        # Convert capability enum to string for JSON serialization
        if "capability" in data and data["capability"] is not None:
            data["capability"] = data["capability"].value
        return data


class FunctionDocumentation(ExtractedData):
    """Model for function documentation."""

    name: str
    docstring: Optional[str] = None
    signature: str
    parameters: Dict[str, Dict[str, Any]] = {}
    return_type: Optional[str] = None
    return_description: Optional[str] = None
    module_path: str
    extractor_name: str = "python"
    capability: Capability = Capability.CODE_STRUCTURE


class ClassDocumentation(ExtractedData):
    """Model for class documentation."""

    name: str
    docstring: Optional[str] = None
    methods: List[FunctionDocumentation] = []
    module_path: str
    extractor_name: str = "python"
    capability: Capability = Capability.CODE_STRUCTURE


class ModuleDocumentation(ExtractedData):
    """Model for module documentation."""

    name: str
    docstring: Optional[str] = None
    file_path: str
    functions: List[FunctionDocumentation] = []
    classes: List[ClassDocumentation] = []
    extractor_name: str = "python"
    capability: Capability = Capability.CODE_STRUCTURE


class ExtractionResult(BaseModel):
    """Container for results from multiple extractors."""

    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    extractors_used: List[str] = []
    file_count: int = 0
    data: List[ExtractedData] = []

    def filter_by_capability(self, capability: Capability) -> List[ExtractedData]:
        """Filter results by capability type.

        Args:
            capability (Capability): The capability to filter by

        Returns:
            List[ExtractedData]: Data items matching the capability
        """
        return [item for item in self.data if item.capability == capability]

    def get_modules(self) -> List[ModuleDocumentation]:
        """Get all module documentation items.

        This is a convenience method for backward compatibility.

        Returns:
            List[ModuleDocumentation]: All module documentation items
        """
        return [item for item in self.data if isinstance(item, ModuleDocumentation)]
