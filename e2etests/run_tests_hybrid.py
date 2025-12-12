"""Enhanced E2E Test Runner with file verification and code analysis.

Executes test scenarios, extracts code from responses, creates files,
and analyzes code quality.
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Import agent delegation
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.core.agents.delegation import delegate_task
from packages.core.config import init_config

# Import code extraction utilities
from code_extractor import (
    extract_and_create_files,
    verify_file_exists,
    analyze_code_quality,
    extract_filename_from_text
)


class E2ETestRunner:
    """Execute E2E tests with file verification and code analysis."""
    
    def __init__(self, sandbox_dir: str = "../sandbox"):
        self.sandbox = Path(sandbox_dir)
        self.sandbox.mkdir(parents=True, exist_ok=True)
        self.results: List[Dict[str, Any]] = []
        self.passed = 0
        self.failed = 0
        
    async def run_test(
        self, 
        test_num: int, 
        command: str, 
        success_criteria: str, 
        category: str = "general"
    ) -> Dict[str, Any]:
        """Run a single test scenario with file verification.
        
        Args:
            test_num: Test number
            command: Command to execute
            success_criteria: What defines success
            category: Test category
            
        Returns:
            Test result dictionary
        """
        print(f"\n{'='*80}")
        print(f"Test {test_num} ({category}): {command[:50]}...")
        print(f"{'='*80}")
        
        try:
            # Execute command via agent
            result = await delegate_task(command)
            
            # Check if this is a file creation command
            is_file_creation = 'create' in command.lower() or 'generate' in command.lower()
            files_created = []
            file_analyses = {}
            
            if is_file_creation:
                # Try to extract and create files from response
                files_created = extract_and_create_files(command, result.result)
                
                print(f"📝 Files extracted: {files_created}")
                
                # Verify and analyze each file
                for filepath in files_created:
                    if verify_file_exists(filepath):
                        print(f"✅ File created: {filepath}")
                        
                        # Analyze code quality
                        analysis = analyze_code_quality(filepath)
                        file_analyses[filepath] = analysis
                        
                        print(f"📊 Quality metrics: {analysis.get('code_lines', 0)} lines, "
                              f"{analysis.get('function_count', 0)} functions, "
                              f"{'✅' if analysis.get('has_docstrings') else '❌'} docstrings")
                    else:
                        print(f"❌ File not found: {filepath}")
            
            # Determine if test passed
            if is_file_creation:
                passed = len(files_created) > 0 and result.success
            else:
                passed = result.success
            
            test_result = {
                "test_num": test_num,
                "category": category,
                "command": command,
                "success_criteria": success_criteria,
                "passed": passed,
                "output": result.result[:300],
                "agents_used": result.agents_used,
                "files_created": files_created,
                "file_analyses": file_analyses,
                "timestamp": datetime.now().isoformat()
            }
            
            if passed:
                print(f"✅ PASSED")
                self.passed += 1
            else:
                print(f"❌ FAILED - No files created" if is_file_creation else "❌ FAILED")
                self.failed += 1
                
            return test_result
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.failed += 1
            return {
                "test_num": test_num,
                "category": category,
                "command": command,
                "passed": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_all_tests(self):
        """Run test suite."""
        
        tests = [
            # Category 1: Code Analysis (Tests 1-8) - These work fine
            (1, "how many python files are in the packages/core/agents directory?", "Returns specific number", "analysis"),
            (2, "which is the largest python file in packages/core/?", "Identifies largest file", "analysis"),
            
            # Category 2: Code Generation (Tests 3-10) - Need file creation
            (3, "create a file sandbox/calculator.py with functions add, subtract, multiply, divide", "File with 4 functions", "generation"),
            (4, "create sandbox/person.py with a Person class that has name, age attributes and a greet() method", "Person class file", "generation"),
            (5, "create sandbox/user_model.py with a Pydantic model for User with email validation", "Pydantic model file", "generation"),
            (6, "create sandbox/string_utils.py with functions: capitalize_words, reverse_string, count_vowels", "3 utility functions", "generation"),
            (7, "create sandbox/api.py with a simple FastAPI endpoint for GET /health", "FastAPI file", "generation"),
            (8, "generate sandbox/hello_cli.py with a click-based CLI that has a hello command", "Click CLI file", "generation"),
           (9, "create sandbox/test_calculator.py with pytest tests for calculator functions", "Test file", "generation"),
            (10, "create sandbox/app_config.py with a Config class using Pydantic Settings", "Config file", "generation"),
        ]
        
        for test_num, command, criteria, category in tests:
            result = await self.run_test(test_num, command, criteria, category)
            self.results.append(result)
            await asyncio.sleep(2)  # Small delay
        
        self.generate_report()
    
    def generate_report(self):
        """Generate detailed test report with file analysis."""
        report_path = Path("results.md")
        
        total = len(self.results)
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        report = f"""# E2E Test Execution Report (Hybrid File Creation)

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Tests Executed**: {total}  
**Passed**: {self.passed} ✅  
**Failed**: {self.failed} ❌  
**Pass Rate**: {pass_rate:.1f}%

---

## Test Results

"""
        
        for result in self.results:
            status = "✅ PASS" if result.get("passed") else "❌ FAIL"
            report += f"""
### Test {result['test_num']} ({result.get('category', 'general')}): {status}

**Command**: `{result.get('command', 'N/A')}`  
**Criteria**: {result.get('success_criteria', 'N/A')}  
**Agents Used**: {', '.join(result.get('agents_used', []))}  

"""
            files = result.get('files_created', [])
            if files:
                report += f"**Files Created**: {', '.join(files)}  \n\n"
                
                # Add code analysis
                analyses = result.get('file_analyses', {})
                for filepath, analysis in analyses.items():
                    report += f"**{filepath} Quality**:  \n"
                    report += f"- Lines: {analysis.get('code_lines', 0)}  \n"
                    report += f"- Functions: {analysis.get('function_count', 0)}  \n"
                    report += f"- Classes: {analysis.get('class_count', 0)}  \n"
                    report += f"- Docstrings: {'✅' if analysis.get('has_docstrings') else '❌'}  \n"
                    report += f"- Type hints: {'✅' if analysis.get('has_type_hints') else '❌'}  \n\n"
            
            if not result.get("passed"):
                report += f"**Error**: {result.get('error', 'Failed validation')}  \n"
            
            report += "---\n"
        
        # Summary
        report += f"""
## Summary

- **Pass Rate**: {pass_rate:.1f}%
- **Status**: {"✅ ALL TESTS PASSED" if self.failed == 0 else f"❌ {self.failed} TESTS FAILED"}
- **Total Files Created**: {sum(len(r.get('files_created', [])) for r in self.results)}

## Files in Sandbox

"""
        # List all files created
        sandbox_files = list(Path("../sandbox").glob("*.py"))
        if sandbox_files:
            for f in sorted(sandbox_files):
                report += f"- `{f.name}`\n"
        else:
            report += "- No files created\n"
        
        report_path.write_text(report)
        print(f"\n📊 Report generated: {report_path}")


async def main():
    """Run E2E tests with file extraction."""
    print("🚀 Starting E2E Test Suite (Hybrid Mode)")
    print("=" * 80)
    print("✨ File extraction and analysis enabled")
    print("=" * 80)
    
    init_config()
    runner = E2ETestRunner()
    await runner.run_all_tests()
    
    print(f"\n{'='*80}")
    print(f"✅ Tests Passed: {runner.passed}")
    print(f"❌ Tests Failed: {runner.failed}")
    print(f"📊 Pass Rate: {runner.passed/(runner.passed+runner.failed)*100:.1f}%")
    print(f"{'='*80}")


if __name__ == "__main__":
    asyncio.run(main())
