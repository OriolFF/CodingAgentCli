"""Code extraction and file creation utilities for E2E tests.

Extracts code blocks from agent responses and creates actual files.
"""

import re
from pathlib import Path
from typing import Optional, Tuple


def extract_code_blocks(text: str) -> list[tuple[str, str]]:
    """Extract code blocks from markdown text.
    
    Args:
        text: Text containing markdown code blocks
        
    Returns:
        List of (language, code) tuples
    """
    # Pattern: ```language\ncode\n```
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    return [(lang or 'python', code.strip()) for lang, code in matches]


def extract_filename_from_text(text: str) -> Optional[str]:
    """Extract filename from text like 'create sandbox/file.py'.
    
    Args:
        text: Command or response text
        
    Returns:
        Filename if found, None otherwise
    """
    # Look for patterns like: sandbox/filename.py, "sandbox/file.py", etc.
    patterns = [
        r'sandbox/([\w_]+\.py)',
        r'`sandbox/([\w_]+\.py)`',
        r'"sandbox/([\w_]+\.py)"',
        r"'sandbox/([\w_]+\.py)'",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return f"sandbox/{match.group(1)}"
    
    return None


def create_file_from_code(filepath: str, code: str) -> bool:
    """Create a file with the given code.
    
    Args:
        filepath: Path to file
        code: Code content
        
    Returns:
        True if file created successfully
    """
    try:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(code)
        return True
    except Exception as e:
        print(f"Error creating file {filepath}: {e}")
        return False


def extract_and_create_files(command: str, response: str) -> list[str]:
    """Extract code from response and create files.
    
    Args:
        command: Original command
        response: Agent response text
        
    Returns:
        List of files created
    """
    created_files = []
    
    # Extract filename from command
    filename = extract_filename_from_text(command)
    if not filename:
        # Try to extract from response
        filename = extract_filename_from_text(response)
    
    # Also check for HTML files
    if not filename and '.html' in command.lower():
        html_match = re.search(r'sandbox/([\w_]+\.html)', command)
        if html_match:
            filename = f"sandbox/{html_match.group(1)}"
    
    # Extract code blocks
    code_blocks = extract_code_blocks(response)
    
    if not code_blocks:
        return created_files
    
    # If we have a filename and code, create the file
    if filename and code_blocks:
        # Use the first appropriate code block
        target_ext = Path(filename).suffix.lower()
        
        if target_ext == '.html':
            # For HTML, use first html block or any block
            html_blocks = [code for lang, code in code_blocks if lang.lower() in ['html', 'xml', '']]
            if html_blocks:
                if create_file_from_code(filename, html_blocks[0]):
                    created_files.append(filename)
        else:
            # For Python files
            python_blocks = [code for lang, code in code_blocks if lang.lower() in ['python', 'py', '']]
            if python_blocks:
                if create_file_from_code(filename, python_blocks[0]):
                    created_files.append(filename)
    
    # Handle multiple files in one command
    elif len(code_blocks) > 1:
        # Try to match code blocks to filenames mentioned in the command
        filenames = re.findall(r'sandbox/([\w_]+\.\w+)', command)
        for i, (fname, (lang, code)) in enumerate(zip(filenames, code_blocks)):
            filepath = f"sandbox/{fname}"
            if create_file_from_code(filepath, code):
                created_files.append(filepath)
    
    return created_files


def verify_file_exists(filepath: str) -> bool:
    """Verify file was created.
    
    Args:
        filepath: Path to file
        
    Returns:
        True if file exists
    """
    return Path(filepath).exists()


def analyze_code_quality(filepath: str) -> dict:
    """Analyze code quality of a file.
    
    Args:
        filepath: Path to file
        
    Returns:
        Dictionary with quality metrics
    """
    try:
        code = Path(filepath).read_text()
        
        lines = code.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        
        # Basic metrics
        metrics = {
            'total_lines': len(lines),
            'code_lines': len(non_empty_lines),
            'has_docstrings': '"""' in code or "'''" in code,
            'has_type_hints': ': ' in code and '->' in code,
            'has_imports': 'import ' in code or 'from ' in code,
            'has_functions': 'def ' in code,
            'has_classes': 'class ' in code,
            'has_error_handling': 'try:' in code or 'except' in code,
        }
        
        # Count specific elements
        metrics['function_count'] = code.count('def ')
        metrics['class_count'] = code.count('class ')
        
        return metrics
    except Exception as e:
        return {'error': str(e)}
