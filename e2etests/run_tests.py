"""E2E Test Runner for PydanticAI Agent System.

Executes test scenarios and validates agent capabilities.
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


class E2ETestRunner:
    """Execute E2E tests and validate results."""
    
    def __init__(self, sandbox_dir: str = "sandbox"):
        self.sandbox = Path(sandbox_dir)
        self.sandbox.mkdir(exist_ok=True)
        self.results: List[Dict[str, Any]] = []
        self.passed = 0
        self.failed = 0
        
    async def run_test(self, test_num: int, command: str, success_criteria: str, retry_count: int = 0) -> Dict[str, Any]:
        """Run a single test scenario.
        
        Args:
            test_num: Test number
            command: Command to execute
            success_criteria: What defines success
            retry_count: Number of retries attempted
            
        Returns:
            Test result dictionary
        """
        print(f"\n{'='*80}")
        print(f"Test {test_num}: {command[:60]}...")
        print(f"{'='*80}")
        
        try:
            # Execute command via agent
            result = await delegate_task(command)
            
            # Basic validation
            passed = result.success
            
            test_result = {
                "test_num": test_num,
                "command": command,
                "success_criteria": success_criteria,
                "passed": passed,
                "output": result.result[:500],  # Truncate for logging
                "agents_used": result.agents_used,
                "retry_count": retry_count,
                "timestamp": datetime.now().isoformat()
            }
            
            if passed:
                print(f"✅ PASSED")
                self.passed += 1
            else:
                print(f"❌ FAILED")
                self.failed += 1
                
            return test_result
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.failed += 1
            return {
                "test_num": test_num,
                "command": command,
                "passed": False,
                "error": str(e),
                "retry_count": retry_count,
                "timestamp": datetime.now().isoformat()
            }
    
    async def run_all_tests(self):
        """Run all 30 test scenarios."""
        
        # Category 1: Code Analysis (Tests 1-8)
        tests = [
            # Test 1
            {
                "command": "how many python files are in the packages/core/agents directory?",
                "criteria": "Returns specific number and lists files"
            },
            # Test 2
            {
                "command": "which is the largest python file in packages/core/?",
                "criteria": "Identifies actual largest file with size"
            },
            # Test 3
            {
                "command": "analyze the structure of @packages/core/agents/delegation.py",
                "criteria": "Identifies DelegationResult class, delegate_task function"
            },
            # Test 4
            {
                "command": "what dependencies does @packages/core/config/config.py have?",
                "criteria": "Mentions pydantic, os, Path, etc."
            },
            # Test 5
            {
                "command": "assess code quality of @packages/cli/repl.py",
                "criteria": "Provides specific feedback"
            },
            # Test 6
            {
                "command": "find all async functions in packages/core/agents/",
                "criteria": "Lists actual async functions"
            },
            # Test 7
            {
                "command": "which file in packages/core/agents/ is most complex?",
                "criteria": "Provides complexity metrics or reasoning"
            },
            # Test 8
            {
                "command": "check if @packages/core/agents/factory.py has proper docstrings",
                "criteria": "Reports on docstring presence"
            },
            
            # Category 2: Code Generation (Tests 9-16)
            # Test 9
            {
                "command": "create a file sandbox/calculator.py with functions add, subtract, multiply, divide",
                "criteria": "File exists, all functions present with docstrings"
            },
            # Test 10
            {
                "command": "create sandbox/person.py with a Person class that has name, age attributes and a greet() method",
                "criteria": "Class definition correct, greet returns greeting"
            },
            # Test 11
            {
                "command": "create sandbox/user_model.py with a Pydantic model for User with email validation",
                "criteria": "Imports BaseModel, has EmailStr field"
            },
            # Test 12
            {
                "command": "generate sandbox/api.py with a simple FastAPI endpoint for GET /health",
                "criteria": "Imports FastAPI, defines app, has @app.get('/health')"
            },
            # Test 13
            {
                "command": "generate pytest tests for sandbox/calculator.py and save as sandbox/test_calculator.py",
                "criteria": "Has test functions for each calculator function"
            },
            # Test 14
            {
                "command": "create sandbox/string_utils.py with functions: capitalize_words, reverse_string, count_vowels",
                "criteria": "All functions implemented correctly"
            },
            # Test 15
            {
                "command": "create sandbox/app_config.py with a Config class using Pydantic Settings",
                "criteria": "Imports BaseSettings, has model_config"
            },
            # Test 16
            {
                "command": "generate sandbox/hello_cli.py with a click-based CLI that has a hello command",
                "criteria": "Imports click, has @click.command"
            },
        ]
        
        # Execute tests
        for i, test in enumerate(tests[:16], 1):  # Start with first 16 tests
            result = await self.run_test(i, test["command"], test["criteria"])
            self.results.append(result)
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate test execution report."""
        report_path = Path("e2etests/results.md")
        
        total = len(self.results)
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        report = f"""# E2E Test Execution Report

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
### Test {result['test_num']}: {status}

**Command**: `{result.get('command', 'N/A')[:100]}...`  
**Criteria**: {result.get('success_criteria', 'N/A')}  
**Agents Used**: {', '.join(result.get('agents_used', []))}  

"""
            if not result.get("passed"):
                report += f"**Error**: {result.get('error', 'Failed validation')}  \n"
            
            report += "---\n"
        
        # Summary
        report += f"""
## Summary

- **Pass Rate**: {pass_rate:.1f}%
- **Status**: {"✅ ALL TESTS PASSED" if self.failed == 0 else f"❌ {self.failed} TESTS FAILED"}

## Next Steps

"""
        if self.failed > 0:
            report += "- Review failed tests\n- Fix identified issues\n- Re-run failed tests\n"
        else:
            report += "- All tests passed successfully!\n- Agent system validated\n"
        
        report_path.write_text(report)
        print(f"\n📊 Report generated: {report_path}")


async def main():
    """Run E2E tests."""
    print("🚀 Starting E2E Test Suite")
    print("=" * 80)
    
    # Initialize config
    init_config()
    
    # Create runner
    runner = E2ETestRunner()
    
    # Run tests
    await runner.run_all_tests()
    
    print(f"\n{'='*80}")
    print(f"✅ Tests Passed: {runner.passed}")
    print(f"❌ Tests Failed: {runner.failed}")
    print(f"📊 Pass Rate: {runner.passed/(runner.passed+runner.failed)*100:.1f}%")
    print(f"{'='*80}")


if __name__ == "__main__":
    asyncio.run(main())
