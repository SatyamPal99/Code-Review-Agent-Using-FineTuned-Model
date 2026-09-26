from app.ast_checker import validate_python_syntax

def test_valid_python_syntax():
    code = "def add(a, b):\n    return a + b"
    result = validate_python_syntax(code)
    assert result["valid"] is True
    assert result["error"] is None

def test_invalid_python_syntax():
    code = "def add(a, b\n    return a + b"
    result = validate_python_syntax(code)
    assert result["valid"] is False
    assert "SyntaxError" in result["error"]