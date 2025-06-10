"""Python-specific extraction and analysis functions for the Codebase Examiner.

This module contains all Python-specific code extraction and analysis functionality,
including parsing Python files, extracting documentation from docstrings, and
analyzing Python code structure.
"""

import warnings
from typing import Dict, Optional

from codebase_examiner.python.extractor import PythonExtractor


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
        DeprecationWarning,
        stacklevel=2,
    )
    extractor = PythonExtractor()
    return extractor.parse_google_docstring(docstring)


__all__ = ["PythonExtractor", "parse_google_docstring"]
