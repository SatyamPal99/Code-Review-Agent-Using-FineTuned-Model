import ast

def validate_python_syntax(code_str: str) -> dict:
    try:
        ast.parse(code_str)
        return {"valid": True, "error": None}
    except SyntaxError as e:
        return {
            "valid": False,
            "error": f"SyntaxError on line {e.lineno}: {e.msg}"
        }