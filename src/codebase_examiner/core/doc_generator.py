"""Module for generating documentation from code inspection results."""

import json
from typing import List

from codebase_examiner.core.code_inspector import ModuleDocumentation


def generate_markdown_documentation(modules: List[ModuleDocumentation]) -> str:
    """Generate markdown documentation from module documentation.

    Args:
        modules (List[ModuleDocumentation]): List of module documentation objects.

    Returns:
        str: Markdown formatted documentation.
    """
    markdown = "# Codebase Documentation\n\n"

    # Table of contents
    markdown += "## Table of Contents\n\n"
    for module in sorted(modules, key=lambda m: m.name):
        markdown += f"- [Module: {module.name}](#{module.name.lower().replace('.', '')})\n"

    markdown += "\n"

    # Module documentation
    for module in sorted(modules, key=lambda m: m.name):
        markdown += f"## Module: {module.name} <a id='{module.name.lower().replace('.', '')}'></a>\n\n"
        markdown += f"File: `{module.file_path}`\n\n"

        if module.docstring:
            markdown += f"{module.docstring}\n\n"

        # Functions
        if module.functions:
            markdown += "### Functions\n\n"
            for func in sorted(module.functions, key=lambda f: f.name):
                markdown += f"#### `{func.name}{func.signature}`\n\n"

                if func.docstring:
                    markdown += f"{func.docstring}\n\n"

                if func.parameters:
                    markdown += "**Parameters:**\n\n"
                    for param_name, param_info in func.parameters.items():
                        param_type = param_info.get('annotation', '')
                        param_desc = param_info.get('description', '')
                        default = param_info.get('default')

                        type_str = f" ({param_type})" if param_type else ""
                        default_str = f", default: `{default}`" if default and default != "None" else ""

                        markdown += f"- `{param_name}`{type_str}{default_str}: {param_desc}\n"

                    markdown += "\n"

                if func.return_type or func.return_description:
                    markdown += "**Returns:**\n\n"
                    return_type = f"({func.return_type})" if func.return_type else ""
                    return_desc = func.return_description or ""
                    markdown += f"{return_type} {return_desc}\n\n"

        # Classes
        if module.classes:
            markdown += "### Classes\n\n"
            for cls in sorted(module.classes, key=lambda c: c.name):
                markdown += f"#### `{cls.name}`\n\n"

                if cls.docstring:
                    markdown += f"{cls.docstring}\n\n"

                # Class methods
                if cls.methods:
                    markdown += "**Methods:**\n\n"
                    for method in sorted(cls.methods, key=lambda m: m.name):
                        markdown += f"##### `{method.name}{method.signature}`\n\n"

                        if method.docstring:
                            markdown += f"{method.docstring}\n\n"

                        if method.parameters:
                            markdown += "**Parameters:**\n\n"
                            for param_name, param_info in method.parameters.items():
                                if param_name == 'self':
                                    continue

                                param_type = param_info.get('annotation', '')
                                param_desc = param_info.get('description', '')
                                default = param_info.get('default')

                                type_str = f" ({param_type})" if param_type else ""
                                default_str = f", default: `{default}`" if default and default != "None" else ""

                                markdown += f"- `{param_name}`{type_str}{default_str}: {param_desc}\n"

                            markdown += "\n"

                        if method.return_type or method.return_description:
                            markdown += "**Returns:**\n\n"
                            return_type = f"({method.return_type})" if method.return_type else ""
                            return_desc = method.return_description or ""
                            markdown += f"{return_type} {return_desc}\n\n"

        markdown += "---\n\n"

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
