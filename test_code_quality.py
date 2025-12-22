"""Test code quality validation on cogito:14b output."""

import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from packages.core.utils.code_quality import validate_file_quality


async def test_validation():
    """Test validation on broken cogito:14b files."""
    
    print("="*80)
    print("Testing Code Quality Validation")
    print("="*80)
    
    test_files = [
        "tests/output/cogito_14b/tetris.html",
        "tests/output/cogito_14b/tetris.js",
        "tests/output/cogito_14b/tetris.css",
    ]
    
    for file_path in test_files:
        print(f"\n{'='*80}")
        print(f"Validating: {file_path}")
        print(f"{'='*80}\n")
        
        report = await validate_file_quality(file_path)
        
        print(f"Has Issues: {report.has_issues}")
        print(f"Has Critical Issues: {report.has_critical_issues}")
        print(f"Quality Score: {report.quality_score:.2f}")
        print(f"\nIssues Found: {len(report.issues)}")
        
        for issue in report.issues:
            severity_icon = "🔴" if issue.severity == "critical" else "🟡"
            print(f"{severity_icon} [{issue.severity.upper()}] {issue.issue_type}: {issue.description}")
            if issue.line_number:
                print(f"   Line: {issue.line_number}")


if __name__ == "__main__":
    asyncio.run(test_validation())
