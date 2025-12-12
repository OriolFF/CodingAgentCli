"""Complete E2E Test Suite - All 30 Scenarios
Hybrid file creation with code extraction and quality analysis.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.core.agents.delegation import delegate_task
from packages.core.config import init_config
from code_extractor import extract_and_create_files, verify_file_exists, analyze_code_quality

class CompletE2ETestRunner:
    """Execute all 30 E2E test scenarios."""
    
    def __init__(self):
        self.sandbox = Path("../sandbox")
        self.sandbox.mkdir(parents=True, exist_ok=True)
        self.passed = 0
        self.failed = 0
        self.results = []
        
    async def run_test(self, num, command, criteria, category):
        """Run single test with file creation and analysis."""
        print(f"\n{'='*80}")
        print(f"Test {num}/{30} ({category}): {command[:60]}...")
        print(f"{'='*80}")
        
        try:
            result = await delegate_task(command)
            is_creation = 'create' in command.lower() or 'generate' in command.lower()
            
            files_created = []
            if is_creation:
                files_created = extract_and_create_files(command, result.result)
                for f in files_created:
                    if verify_file_exists(f):
                        analysis = analyze_code_quality(f)
                        print(f"✅ {f}: {analysis.get('code_lines', 0)} lines, "
                              f"{analysis.get('function_count', 0)} funcs")
            
            passed = (len(files_created) > 0 if is_creation else True) and result.success
            
            if passed:
                print(f"✅ PASSED")
                self.passed += 1
            else:
                print(f"❌ FAILED")
                self.failed += 1
                
            return {"num": num, "category": category, "passed": passed, 
                    "files": files_created}
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.failed += 1
            return {"num": num, "category": category, "passed": False, "error": str(e)}
    
    async def run_all(self):
        """Execute all 30 tests."""
        tests = [
            # Category 1: Analysis (1-8)
            (1, "how many python files are in packages/core/agents?", "Count files", "analysis"),
            (2, "which is the largest python file in packages/core/?", "Find largest", "analysis"),
            (3, "analyze structure of packages/core/agents/delegation.py", "Analyze structure", "analysis"),
            (4, "what dependencies does packages/core/config/config.py have?", "List dependencies", "analysis"),
            (5, "assess code quality of packages/cli/repl.py", "Quality assessment", "analysis"),
            (6, "find all async functions in packages/core/agents/", "Find async", "analysis"),
            (7, "which file in packages/core/agents/ is most complex?", "Find complex", "analysis"),
            (8, "check if packages/core/agents/factory.py has docstrings", "Check docs", "analysis"),
            
            # Category 2: Generation (9-16)
            (9, "create sandbox/calc.py with add, subtract, multiply, divide functions", "Calculator", "generation"),
            (10, "create sandbox/models.py with Person class (name, age, greet method)", "Person class", "generation"),
            (11, "create sandbox/data.py with Pydantic User model with email", "Pydantic model", "generation"),
            (12, "create sandbox/server.py with FastAPI app and /health endpoint", "FastAPI", "generation"),
            (13, "create sandbox/utils.py with capitalize_words, reverse_string, count_vowels", "Utils", "generation"),
            (14, "create sandbox/cli.py with click command that says hello", "Click CLI", "generation"),
            (15, "create sandbox/config.py with Pydantic Settings Config class", "Config", "generation"),
            (16, "create a complete modern landing page sandbox/landing.html with CSS: hero section, features section (3 cards), testimonials, CTA button, responsive design, gradient backgrounds", "Landing page", "generation"),
            
            # Category 3: Manipulation (17-22)
            (17, "create sandbox/counter.py with Counter class and add reset method", "Counter", "manipulation"),
            (18, "add type hints to all functions in sandbox/calc.py", "Add types", "manipulation"),
            (19, "add docstrings to functions in sandbox/utils.py", "Add docs", "manipulation"),
            (20, "create sandbox/math.py and move add/subtract from calc.py", "Extract", "manipulation"),
            (21, "in sandbox/models.py rename age to years_old", "Rename", "manipulation"),
            (22, "add error handling to sandbox/calc.py divide function", "Error handling", "manipulation"),
            
            # Category 4: Workflows (23-27)
            (23, "analyze sandbox/calc.py and create comprehensive tests", "Analyze+test", "workflow"),
            (24, "review sandbox/models.py and suggest improvements", "Review", "workflow"),
            (25, "create README.md documenting all sandbox modules", "Document", "workflow"),
            (26, "find issues in sandbox/*.py files", "Find issues", "workflow"),
            (27, "analyze all sandbox files and create summary", "Summarize", "workflow"),
            
            # Category 5: Advanced (28-30)
            (28, "compare sandbox/calc.py and sandbox/math.py", "Compare", "advanced"),
            (29, "show dependency graph of sandbox modules", "Dependencies", "advanced"),
            (30, "create todo app: sandbox/todo.py, sandbox/todo_cli.py, sandbox/todo_test.py", "Full app", "advanced"),
        ]
        
        for test_data in tests:
            result = await self.run_test(*test_data)
            self.results.append(result)
            await asyncio.sleep(1)
        
        self.print_summary()
        
    def print_summary(self):
        """Print test summary."""
        print(f"\n{'='*80}")
        print(f"🎯 COMPLETE E2E TEST SUITE RESULTS")
        print(f"{'='*80}")
        print(f"✅ Passed: {self.passed}/30 ({self.passed/30*100:.1f}%)")
        print(f"❌ Failed: {self.failed}/30")
        
        # Category breakdown
        categories = {}
        for r in self.results:
            cat = r.get('category', 'unknown')
            if cat not in categories:
                categories[cat] = {'passed': 0, 'total': 0}
            categories[cat]['total'] += 1
            if r.get('passed'):
                categories[cat]['passed'] += 1
        
        print(f"\n📊 By Category:")
        for cat, stats in categories.items():
            rate = stats['passed']/stats['total']*100
            print(f"  {cat:15s}: {stats['passed']}/{stats['total']} ({rate:.0f}%)")
        
        print(f"{'='*80}")
        
        # List created files
        all_files = []
        for r in self.results:
            all_files.extend(r.get('files', []))
        
        if all_files:
            print(f"\n📁 Files Created ({len(all_files)}):")
            for f in sorted(set(all_files)):
                if Path(f).exists():
                    size = Path(f).stat().st_size
                    print(f"  ✅ {f} ({size} bytes)")

async def main():
    print("🚀 Complete E2E Test Suite - All 30 Scenarios")
    print("=" * 80)
    
    init_config()
    runner = CompletE2ETestRunner()
    await runner.run_all()

if __name__ == "__main__":
    asyncio.run(main())
