"""Complete E2E Test Suite - All 31 Scenarios"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.core.agents.delegation import delegate_task
from packages.core.config import init_config


def extract_filepath_from_command(command: str) -> str | None:
    """Extract expected filepath from command.
    
    Args:
        command: Test command
        
    Returns:
        Expected filepath or None
    """
    import re
    # Look for patterns like: tests/output/file.py, tests/output/file.html
    match = re.search(r'tests/output/([\w_\-]+\.\w+)', command)
    if match:
        return f"tests/output/{match.group(1)}"
    return None


def analyze_file(filepath: Path) -> dict:
    """Analyze created file.
    
    Args:
        filepath: Path to file
        
    Returns:
        Dictionary with basic metrics
    """
    try:
        content = filepath.read_text()
        lines = content.split('\n')
        return {
            'lines': len(lines),
            'size': filepath.stat().st_size,
            'functions': content.count('def '),
            'classes': content.count('class '),
        }
    except:
        return {'error': True}


class CompletE2ETestRunner:
    """Execute all 31 E2E test scenarios."""
    
    def __init__(self):
        self.output_dir = Path("../tests/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.passed = 0
        self.failed = 0
        self.results = []
        
    async def run_test(self, num, command, criteria, category):
        """Run single test and check if files were created."""
        print(f"\n{'='*80}")
        print(f"Test {num}/31 ({category}): {command[:60]}...")
        print(f"{'='*80}")
        
        try:
            result = await delegate_task(command)
            is_creation = 'create' in command.lower() or 'generate' in command.lower()
            
            # Check if expected file was created (for creation tests)
            file_created = False
            expected_file = None # Initialize expected_file
            if is_creation:
                expected_file = extract_filepath_from_command(command)
                if expected_file:
                    filepath = Path(expected_file)
                    if filepath.exists():
                        analysis = analyze_file(filepath)
                        print(f"✅ {expected_file}: {analysis.get('lines', 0)} lines, "
                              f"{analysis.get('functions', 0)} funcs")
                        file_created = True
            
            passed = (file_created if is_creation else True) and result.success
            
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
        """Execute all 31 tests."""
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
            (9, "create tests/output/calc.py with add, subtract, multiply, divide functions", "Calculator", "generation"),
            (10, "create tests/output/models.py with Person class (name, age, greet method)", "Person class", "generation"),
            (11, "create tests/output/data.py with Pydantic User model with email", "Pydantic model", "generation"),
            (12, "create tests/output/server.py with FastAPI app and /health endpoint", "FastAPI", "generation"),
            (13, "create tests/output/utils.py with capitalize_words, reverse_string, count_vowels", "Utils", "generation"),
            (14, "create tests/output/cli.py with click command that says hello", "Click CLI", "generation"),
            (15, "create tests/output/config.py with Pydantic Settings Config class", "Config", "generation"),
            (16, "create a complete modern landing page tests/output/landing.html with CSS: hero section, features section (3 cards), testimonials, CTA button, responsive design, gradient backgrounds", "Landing page", "generation"),
            (31, "create tests/output/cv_landing.html - a nice landing web page following Material 3 design guidelines to serve as a CV for an Android engineer. Include experience at Google (Senior Android Engineer, 2020-2023, worked on Play Store), Meta (Android Developer, 2018-2020, Instagram team), and Spotify (Junior Android Developer, 2016-2018, mobile player). Add sections for: hero with name and title, work experience timeline, technical skills (Kotlin, Java, Jetpack Compose, MVVM, Coroutines), side projects, and contact. Use Material 3 colors, typography, and elevation patterns.", "Material 3 CV", "generation"),
            
            # Category 3: Manipulation (17-22)
            (17, "create tests/output/counter.py with Counter class and add reset method", "Counter", "manipulation"),
            (18, "add type hints to all functions in tests/output/calc.py", "Add types", "manipulation"),
            (19, "add docstrings to functions in tests/output/utils.py", "Add docs", "manipulation"),
            (20, "create tests/output/math.py and move add/subtract from calc.py", "Extract", "manipulation"),
            (21, "in tests/output/models.py rename age to years_old", "Rename", "manipulation"),
            (22, "add error handling to tests/output/calc.py divide function", "Error handling", "manipulation"),
            
            # Category 4: Workflows (23-27)
            (23, "analyze tests/output/calc.py and create comprehensive tests", "Analyze+test", "workflow"),
            (24, "review tests/output/models.py and suggest improvements", "Review", "workflow"),
            (25, "create README.md documenting all tests/output modules", "Document", "workflow"),
            (26, "find issues in tests/output/*.py files", "Find issues", "workflow"),
            (27, "analyze all tests/output files and create summary", "Summarize", "workflow"),
            
            # Category 5: Advanced (28-30)
            (28, "compare tests/output/calc.py and tests/output/math.py", "Compare", "advanced"),
            (29, "show dependency graph of tests/output modules", "Dependencies", "advanced"),
            (30, "create todo app: tests/output/todo.py, tests/output/todo_cli.py, tests/output/todo_test.py", "Full app", "advanced"),
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
        print(f"✅ Passed: {self.passed}/31 ({self.passed/31*100:.1f}%)")
        print(f"❌ Failed: {self.failed}/31")
        
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
    print("🚀 Complete E2E Test Suite - All 31 Scenarios")
    print("=" * 80)
    
    init_config()
    runner = CompletE2ETestRunner()
    await runner.run_all()

if __name__ == "__main__":
    asyncio.run(main())
