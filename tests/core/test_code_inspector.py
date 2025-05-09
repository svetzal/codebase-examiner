"""Tests for the code_inspector module."""

import inspect
import os
import tempfile
from pathlib import Path

import pytest

from codebase_examiner.core.code_inspector import (
    parse_google_docstring,
    inspect_module,
    ModuleDocumentation,
    ClassDocumentation,
    FunctionDocumentation
)


def test_parse_google_docstring():
    """Test parsing Google-style docstrings."""
    # Test docstring with args and returns
    docstring = """Test function.

    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter.

    Returns:
        bool: True if successful, False otherwise.
    """
    
    result = parse_google_docstring(docstring)
    
    assert "params" in result
    assert len(result["params"]) == 2
    assert "param1" in result["params"]
    assert result["params"]["param1"]["type"] == "int"
    assert result["params"]["param1"]["description"] == "The first parameter."
    assert "param2" in result["params"]
    assert result["params"]["param2"]["type"] == "str"
    assert result["params"]["param2"]["description"] == "The second parameter."
    
    assert "returns" in result
    assert result["returns"]["type"] == "bool"
    assert result["returns"]["description"] == "True if successful, False otherwise."
    
    # Test empty docstring
    assert parse_google_docstring(None) == {"params": {}, "returns": None}
    assert parse_google_docstring("") == {"params": {}, "returns": None}
    
    # Test docstring with no args or returns
    assert parse_google_docstring("Just a description.") == {"params": {}, "returns": None}


def test_inspect_module():
    """Test inspecting a Python module."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Create a test Python file
        module_content = """\"\"\"Test module docstring.\"\"\"

def test_function(param1: int, param2: str = "default") -> bool:
    \"\"\"Test function.
    
    Args:
        param1 (int): The first parameter.
        param2 (str): The second parameter. Defaults to "default".
        
    Returns:
        bool: True if successful, False otherwise.
    \"\"\"
    return True
    
class TestClass:
    \"\"\"Test class docstring.\"\"\"
    
    def __init__(self, value: int):
        \"\"\"Initialize the TestClass.
        
        Args:
            value (int): The initial value.
        \"\"\"
        self.value = value
        
    def test_method(self, factor: float) -> float:
        \"\"\"Test method.
        
        Args:
            factor (float): The factor to multiply by.
            
        Returns:
            float: The result of the calculation.
        \"\"\"
        return self.value * factor
"""
        module_path = Path(tmpdirname) / "test_module.py"
        module_path.write_text(module_content)
        
        # Inspect the module
        module_doc = inspect_module(module_path)
        
        # Verify module info
        assert isinstance(module_doc, ModuleDocumentation)
        assert module_doc.name == "test_module"
        assert module_doc.docstring == "Test module docstring."
        assert str(module_path) in module_doc.file_path
        
        # Verify function info
        assert len(module_doc.functions) == 1
        function = module_doc.functions[0]
        assert isinstance(function, FunctionDocumentation)
        assert function.name == "test_function"
        assert function.docstring == "Test function.\n    \n    Args:\n        param1 (int): The first parameter.\n        param2 (str): The second parameter. Defaults to \"default\".\n        \n    Returns:\n        bool: True if successful, False otherwise."
        assert "param1" in function.parameters
        assert function.parameters["param1"]["annotation"] == "<class 'int'>"
        assert "param2" in function.parameters
        assert function.parameters["param2"]["default"] == '"default"'
        assert function.return_type == "<class 'bool'>"
        
        # Verify class info
        assert len(module_doc.classes) == 1
        class_doc = module_doc.classes[0]
        assert isinstance(class_doc, ClassDocumentation)
        assert class_doc.name == "TestClass"
        assert class_doc.docstring == "Test class docstring."
        
        # Verify class methods
        assert len(class_doc.methods) == 2  # __init__ and test_method
        
        # Find the test_method
        test_method = next((m for m in class_doc.methods if m.name == "test_method"), None)
        assert test_method is not None
        assert test_method.docstring == "Test method.\n        \n        Args:\n            factor (float): The factor to multiply by.\n            \n        Returns:\n            float: The result of the calculation."
        assert "factor" in test_method.parameters
        assert test_method.parameters["factor"]["annotation"] == "<class 'float'>"
        assert test_method.return_type == "<class 'float'>"