"""Module for generating documentation from code inspection results."""

import json
from typing import List, Optional

from codebase_examiner.core.code_inspector import ModuleDocumentation
from codebase_examiner.core.section_generators import (
    SectionGenerator,
    TitleSection,
    TableOfContentsSection,
    ModulesSection,
)

def get_default_markdown_sections() -> List[SectionGenerator]:
    """Return the default list of markdown section generators."""
    return [TitleSection(), TableOfContentsSection(), ModulesSection()]

def generate_markdown_documentation(
    modules: List[ModuleDocumentation],
    sections: Optional[List[SectionGenerator]] = None,
) -> str:
    """Generate markdown documentation by combining configured sections.

    Args:
        modules (List[ModuleDocumentation]): List of module documentation objects.
        sections (Optional[List[SectionGenerator]]): Optional list of section generators.
            Defaults to the standard title, table of contents, and modules sections.

    Returns:
        str: Markdown formatted documentation.
    """
    if sections is None:
        sections = get_default_markdown_sections()
    markdown = ""
    for section in sections:
        markdown += section.generate(modules)
    return markdown

def generate_json_documentation(modules: List[ModuleDocumentation]) -> str:
    """Generate JSON documentation from module documentation.

    Args:
        modules (List[ModuleDocumentation]): List of module documentation objects.

    Returns:
        str: JSON formatted documentation.
    """
    # Convert Pydantic models to dictionaries
    json_data = [module.model_dump() for module in modules]
    return json.dumps(json_data, indent=2)


def generate_documentation(modules: List[ModuleDocumentation], format: str = "markdown") -> str:
    """Generate documentation in the specified format.

    Args:
        modules (List[ModuleDocumentation]): List of module documentation objects.
        format (str, optional): Output format - "markdown" or "json". Defaults to "markdown".

    Returns:
        str: Generated documentation.
    """
    if format.lower() == "json":
        return generate_json_documentation(modules)
    else:
        return generate_markdown_documentation(modules)
