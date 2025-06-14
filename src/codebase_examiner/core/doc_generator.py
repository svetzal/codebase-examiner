"""Module for generating documentation from code inspection results."""

import enum
import json
from typing import List, Optional, Union

from codebase_examiner.core.models import (
    ModuleDocumentation,
    ExtractionResult,
)
from codebase_examiner.core.section_generators import (
    SectionGenerator,
    TitleSection,
    TableOfContentsSection,
    ModulesSection,
)


class OutputFormat(str, enum.Enum):
    """Enum for supported documentation output formats."""
    MARKDOWN = "markdown"
    JSON = "json"


def get_default_markdown_sections() -> List[SectionGenerator]:
    """Return the default list of markdown section generators."""
    return [TitleSection(), TableOfContentsSection(), ModulesSection()]


def generate_markdown_documentation(
    modules_or_result: Union[List[ModuleDocumentation], ExtractionResult],
    sections: Optional[List[SectionGenerator]] = None,
) -> str:
    """Generate markdown documentation by combining configured sections.

    Args:
        modules_or_result (Union[List[ModuleDocumentation], ExtractionResult]): List of module
        documentation objects
            or an ExtractionResult containing them.
        sections (Optional[List[SectionGenerator]]): Optional list of section generators.
            Defaults to the standard title, table of contents, and modules sections.

    Returns:
        str: Markdown formatted documentation.
    """
    if sections is None:
        sections = get_default_markdown_sections()

    # Extract modules from ExtractionResult if needed
    if isinstance(modules_or_result, ExtractionResult):
        modules = modules_or_result.get_modules()
    else:
        modules = modules_or_result

    markdown = ""
    for section in sections:
        markdown += section.generate(modules)
    return markdown


def generate_json_documentation(
    modules_or_result: Union[List[ModuleDocumentation], ExtractionResult],
) -> str:
    """Generate JSON documentation from module documentation.

    Args:
        modules_or_result (Union[List[ModuleDocumentation], ExtractionResult]): List of module
        documentation objects
            or an ExtractionResult containing them.

    Returns:
        str: JSON formatted documentation.
    """
    # Extract modules from ExtractionResult if needed
    if isinstance(modules_or_result, ExtractionResult):
        modules = modules_or_result.get_modules()
    else:
        modules = modules_or_result

    # Convert Pydantic models to dictionaries with special handling for enums
    json_data = [module.model_dump() for module in modules]

    # Use a custom encoder class that handles our Capability enum
    class EnumEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, enum.Enum):
                return obj.value
            return super().default(obj)

    return json.dumps(json_data, indent=2, cls=EnumEncoder)


def generate_documentation(
    modules_or_result: Union[List[ModuleDocumentation], ExtractionResult],
    format: OutputFormat = OutputFormat.MARKDOWN,
) -> str:
    """Generate documentation in the specified format.

    Args:
        modules_or_result (Union[List[ModuleDocumentation], ExtractionResult]): List of module
        documentation objects
            or an ExtractionResult containing them.
        format (OutputFormat, optional): Output format - OutputFormat.MARKDOWN or 
            OutputFormat.JSON. Defaults to OutputFormat.MARKDOWN.

    Returns:
        str: Generated documentation.
    """
    if format == OutputFormat.JSON:
        return generate_json_documentation(modules_or_result)
    else:
        return generate_markdown_documentation(modules_or_result)
