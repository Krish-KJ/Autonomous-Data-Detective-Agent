import ast
import io
import contextlib
import pandas as pd
import numpy as np

def check_unsafe_code(code_str: str) -> bool:
    """
    Parses the code using the Abstract Syntax Tree (AST).
    Checks for illegal imports (os, sys, subprocess, etc) before execution.
    Returns True if SAFE, False if UNSAFE.
    """
    blocklist = {'os', 'sys', 'subprocess', 'pty', 'shlex', 'builtins', 'eval', 'exec', 'open'}
    
    try:
        tree = ast.parse(code_str)
    except SyntaxError:
        return True

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split('.')[0] in blocklist:
                    return False
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split('.')[0] in blocklist:
                return False
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in ['eval', 'exec', 'open', 'compile']:
                return False
                
    return True

def execute_pandas_code(code_str: str, df=None, dataframes: dict = None) -> dict:
    """
    Safely executes generated Python Pandas code against the user's dataframe(s).
    
    Args:
        code_str: The python code to run. Must assume `df` is the primary dataframe variable.
        df: The primary pandas DataFrame (backward compatible).
        dataframes: Optional dict of {"name": DataFrame} for multi-CSV support.
        
    Returns:
        dict: {
            "success": bool,
            "output": str (captured print output),
            "error": str (error message if failed)
        }
    """
    
    if not check_unsafe_code(code_str):
        return {
            "success": False,
            "output": "",
            "error": "SecurityViolation: Code contains unsafe imports or function calls (e.g., os, sys, eval)."
        }
        
    safe_builtins = {
        '__import__': __import__,  # Required for import statements (AST checker blocks dangerous ones)
        'print': print,
        'range': range,
        'len': len,
        'int': int,
        'float': float,
        'str': str,
        'bool': bool,
        'list': list,
        'dict': dict,
        'set': set,
        'tuple': tuple,
        'abs': abs,
        'max': max,
        'min': min,
        'sum': sum,
        'round': round,
        'sorted': sorted,
        'enumerate': enumerate,
        'zip': zip,
        'map': map,
        'filter': filter,
        'any': any,
        'all': all,
        'reversed': reversed,
        'hasattr': hasattr,
        'getattr': getattr,
        'setattr': setattr,
        'isinstance': isinstance,
        'issubclass': issubclass,
        'type': type,
        'id': id,
        'repr': repr,
        'hash': hash,
        'iter': iter,
        'next': next,
        'slice': slice,
        'super': super,
        'property': property,
        'staticmethod': staticmethod,
        'classmethod': classmethod,
        'object': object,
        'KeyError': KeyError,
        'ValueError': ValueError,
        'TypeError': TypeError,
        'IndexError': IndexError,
        'AttributeError': AttributeError,
        'StopIteration': StopIteration,
        'Exception': Exception,
        'None': None,
        'True': True,
        'False': False,
    }
    
    restricted_globals = {
        '__builtins__': safe_builtins,
        'pd': pd,
        'np': np,
        'df': df
    }
    
    # Inject all named dataframes for multi-CSV support
    if dataframes:
        for name, frame in dataframes.items():
            safe_name = name.replace('.csv', '').replace(' ', '_').replace('-', '_')
            restricted_globals[safe_name] = frame
            if restricted_globals['df'] is None:
                restricted_globals['df'] = frame
    
    restricted_locals = {}
    
    stdout_buffer = io.StringIO()
    
    try:
        with contextlib.redirect_stdout(stdout_buffer):
            exec(code_str, restricted_globals, restricted_locals)
            
        return {
            "success": True,
            "output": stdout_buffer.getvalue().strip(),
            "error": None
        }
        
    except SyntaxError as e:
        return {
            "success": False,
            "output": stdout_buffer.getvalue().strip(),
            "error": f"SyntaxError: {str(e)}\nLine: {e.lineno}, Offset: {e.offset}"
        }
    except NameError as e:
         return {
            "success": False,
            "output": stdout_buffer.getvalue().strip(),
            "error": f"NameError (Undefined variable/function): {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "output": stdout_buffer.getvalue().strip(),
            "error": f"{type(e).__name__}: {str(e)}"
        }
