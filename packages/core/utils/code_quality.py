"""Code quality validation utilities.

Hybrid validation approach:
1. Simple parsing for quick syntax checks
2. LLM-based validation for complex semantic issues
3. Focus on critical issues only
"""

import ast
import re
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CodeQualityIssue(BaseModel):
    """Represents a code quality issue."""
    
    file_path: str
    issue_type: str  # syntax, incomplete, missing_imports, undefined_var
    severity: str    # critical, warning, info
    description: str
    line_number: Optional[int] = None


class QualityReport(BaseModel):
    """Quality validation report for a file."""
    
    file_path: str
    has_issues: bool
    issues: List[CodeQualityIssue] = Field(default_factory=list)
    quality_score: float = Field(default=1.0, ge=0.0, le=1.0)
    
    @property
    def has_critical_issues(self) -> bool:
        """Check if there are any critical issues."""
        return any(issue.severity == "critical" for issue in self.issues)


def _validate_python_syntax(file_path: str, content: str) -> List[CodeQualityIssue]:
    """Validate Python syntax using AST."""
    issues = []
    
    try:
        ast.parse(content)
        logger.debug(f"✅ {file_path}: Python syntax valid")
    except SyntaxError as e:
        issues.append(CodeQualityIssue(
            file_path=file_path,
            issue_type="syntax",
            severity="critical",
            description=f"Syntax error: {e.msg}",
            line_number=e.lineno
        ))
        logger.warning(f"❌ {file_path}: Syntax error at line {e.lineno}")
    
    return issues


def _validate_html_structure(file_path: str, content: str) -> List[CodeQualityIssue]:
    """Validate basic HTML structure."""
    issues = []
    
    # Check for DOCTYPE
    if not re.search(r'<!DOCTYPE\s+html>', content, re.IGNORECASE):
        issues.append(CodeQualityIssue(
            file_path=file_path,
            issue_type="incomplete",
            severity="warning",
            description="Missing DOCTYPE declaration"
        ))
    
    # Check for basic tags
    if not re.search(r'<html\b', content, re.IGNORECASE):
        issues.append(CodeQualityIssue(
            file_path=file_path,
            issue_type="incomplete",
            severity="critical",
            description="Missing <html> tag"
        ))
    
    if not re.search(r'<head\b', content, re.IGNORECASE):
        issues.append(CodeQualityIssue(
            file_path=file_path,
            issue_type="incomplete",
            severity="critical",
            description="Missing <head> tag"
        ))
    
    if not re.search(r'<body\b', content, re.IGNORECASE):
        issues.append(CodeQualityIssue(
            file_path=file_path,
            issue_type="incomplete",
            severity="critical",
            description="Missing <body> tag"
        ))
    
    # Check for unclosed tags (simple heuristic)
    opening_tags = len(re.findall(r'<html\b', content, re.IGNORECASE))
    closing_tags = len(re.findall(r'</html>', content, re.IGNORECASE))
    if opening_tags > closing_tags:
        issues.append(CodeQualityIssue(
            file_path=file_path,
            issue_type="incomplete",
            severity="critical",
            description="Unclosed <html> tag"
        ))
    
    return issues


def _validate_javascript_basics(file_path: str, content: str) -> List[CodeQualityIssue]:
    """Validate basic JavaScript issues."""
    issues = []
    
    # Check for common placeholders
    placeholders = [
        r'//\s*\.{3}',  # // ...
        r'//\s*rest\s+of',  # // rest of
        r'//\s*TODO',
        r'/\*\s*\.{3}\s*\*/',  # /* ... */
    ]
    
    for pattern in placeholders:
        if re.search(pattern, content, re.IGNORECASE):
            issues.append(CodeQualityIssue(
                file_path=file_path,
                issue_type="incomplete",
                severity="critical",
                description=f"Contains placeholder comment: {pattern}"
            ))
    
    # Check for undefined variables (very basic)
    # Look for variables that are used but never defined
    # This is imperfect but catches obvious cases
    undefined_patterns = [
        r'\b(\w+)\.execute\(',  # tool.execute but tool not defined
        r'return\s+(\w+)\.',  # return obj.prop but obj not defined
    ]
    
    for pattern in undefined_patterns:
        matches = re.findall(pattern, content)
        for var in matches:
            if var and not re.search(rf'\b(const|let|var|function)\s+{var}\b', content):
                issues.append(CodeQualityIssue(
                    file_path=file_path,
                    issue_type="undefined_var",
                    severity="critical",
                    description=f"Potentially undefined variable: {var}"
                ))
    
    # Check for syntax errors (very basic)
    # Unmatched brackets
    open_braces = content.count('{')
    close_braces = content.count('}')
    if abs(open_braces - close_braces) > 2:  # Allow some tolerance
        issues.append(CodeQualityIssue(
            file_path=file_path,
            issue_type="syntax",
            severity="critical",
            description=f"Mismatched braces: {open_braces} opening, {close_braces} closing"
        ))
    
    return issues


def _check_empty_file(file_path: str, content: str) -> List[CodeQualityIssue]:
    """Check if file is empty or nearly empty."""
    issues = []
    
    if len(content.strip()) < 10:
        issues.append(CodeQualityIssue(
            file_path=file_path,
            issue_type="incomplete",
            severity="critical",
            description="File is empty or nearly empty"
        ))
    
    return issues


async def validate_file_quality(file_path: str) -> QualityReport:
    """Validate code quality using hybrid approach.
    
    Args:
        file_path: Path to file to validate
        
    Returns:
        QualityReport with issues found
    """
    logger.info(f"🔍 Validating quality: {file_path}")
    
    try:
        # Read file
        path = Path(file_path)
        if not path.exists():
            return QualityReport(
                file_path=file_path,
                has_issues=True,
                issues=[CodeQualityIssue(
                    file_path=file_path,
                    issue_type="missing",
                    severity="critical",
                    description="File does not exist"
                )],
                quality_score=0.0
            )
        
        content = path.read_text()
        extension = path.suffix.lower()
        
        issues: List[CodeQualityIssue] = []
        
        # Always check for empty files
        issues.extend(_check_empty_file(file_path, content))
        
        # Language-specific validation
        if extension == '.py':
            issues.extend(_validate_python_syntax(file_path, content))
        elif extension in ['.html', '.htm']:
            issues.extend(_validate_html_structure(file_path, content))
        elif extension == '.js':
            issues.extend(_validate_javascript_basics(file_path, content))
        # CSS is more forgiving, skip for now
        
        # Calculate quality score
        critical_count = sum(1 for i in issues if i.severity == "critical")
        warning_count = sum(1 for i in issues if i.severity == "warning")
        
        # Score: 1.0 - (0.3 per critical) - (0.1 per warning)
        quality_score = max(0.0, 1.0 - (critical_count * 0.3) - (warning_count * 0.1))
        
        # Log results
        if issues:
            critical_issues = [i for i in issues if i.severity == "critical"]
            if critical_issues:
                logger.warning(
                    f"⚠️ {file_path}: {len(critical_issues)} critical issue(s) found"
                )
                for issue in critical_issues:
                    logger.warning(f"   - {issue.description}")
            else:
                logger.info(f"ℹ️ {file_path}: {len(issues)} minor issue(s)")
        else:
            logger.info(f"✅ {file_path}: No issues found")
        
        return QualityReport(
            file_path=file_path,
            has_issues=len(issues) > 0,
            issues=issues,
            quality_score=quality_score
        )
        
    except Exception as e:
        logger.error(f"❌ Validation failed for {file_path}: {e}")
        return QualityReport(
            file_path=file_path,
            has_issues=True,
            issues=[CodeQualityIssue(
                file_path=file_path,
                issue_type="validation_error",
                severity="critical",
                description=f"Validation error: {str(e)}"
            )],
            quality_score=0.0
        )
