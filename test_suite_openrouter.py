"""OpenRouter Test Suite - Landing Page & Tetris Game

Demonstrates hybrid configuration:
- Local Ollama for coordination (FREE)
- OpenRouter for code generation (PAID, high quality)
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from packages.core.agents.delegation import delegate_task
from packages.core.config import init_config


class OpenRouterTestSuite:
    """Test suite for OpenRouter code generation."""
    
    def __init__(self):
        self.results = []
        self.start_time = None
        self.config = None
    
    async def run_test(self, name: str, command: str, expected_file: Path, checks: dict):
        """Run a single test."""
        print(f'\n{"="*80}')
        print(f'Test: {name}')
        print(f'{"="*80}')
        
        test_start = datetime.now()
        
        # Run the command
        result = await delegate_task(command)
        
        duration = (datetime.now() - test_start).total_seconds()
        
        # Check results
        success = result.success and expected_file.exists()
        
        if expected_file.exists():
            size = expected_file.stat().st_size
            content = expected_file.read_text()
            
            print(f'\n✅ File created: {expected_file} ({size:,} bytes)')
            print(f'⏱️  Generation time: {duration:.1f}s')
            
            # Run checks
            print(f'\n📋 Content Checks:')
            for check_name, check_pattern in checks.items():
                passed = check_pattern.lower() in content.lower()
                print(f'  {"✅" if passed else "❌"} {check_name}')
            
            print(f'\n📄 Preview (first 200 chars):\n{content[:200]}...')
        else:
            print(f'\n❌ File NOT created: {expected_file}')
            success = False
        
        self.results.append({
            'name': name,
            'success': success,
            'duration': duration,
            'file': str(expected_file) if expected_file.exists() else None,
            'size': expected_file.stat().st_size if expected_file.exists() else 0
        })
        
        return success
    
    async def run_all(self):
        """Run all tests in the suite."""
        print('='*80)
        print('OpenRouter Test Suite - Code Generation Demos')
        print('='*80)
        
        self.config = init_config()
        self.start_time = datetime.now()
        
        print(f'\n📋 Configuration:')
        print(f'  Coordinator: {self.config.coordinator_model}')
        print(f'  Code Generator: {self.config.code_generator_model}')
        print(f'  OpenRouter: {"✅ Enabled" if self.config.openrouter_api_key else "❌ Disabled"}')
        
        if not self.config.openrouter_api_key:
            print(f'\n⚠️  WARNING: OPENROUTER_API_KEY not set - using local models')
        
        # Test 1: Material 3 CV Landing Page
        await self.run_test(
            name='Material 3 CV Landing Page',
            command="""create tests/output/cv_landing.html - a nice landing web page following Material 3 design guidelines to serve as a CV for an Android engineer. 
            Include experience at Google (Senior Android Engineer, 2020-2023, worked on Play Store), 
            Meta (Android Developer, 2018-2020, Instagram team), and Spotify (Junior Android Developer, 2016-2018, mobile player). 
            Add sections for: hero with name and title, work experience timeline, technical skills (Kotlin, Java, Jetpack Compose, MVVM, Coroutines), 
            side projects, and contact. Use Material 3 colors, typography, and elevation patterns.
            Use a parallax effect and a soft gradient background. Add a contact form with name, email, and message fields.""",
            expected_file=Path('tests/output/cv_landing.html'),
            checks={
                'DOCTYPE': '<!DOCTYPE',
                'Material 3 colors': '--md-primary',
                'Google experience': 'Google',
                'Meta experience': 'Meta',
                'Spotify experience': 'Spotify',
                'CSS styling': '<style',
            }
        )
        
        # Test 2: Tetris Game
        await self.run_test(
            name='Tetris Game',
            command="""create tests/output/tetris.html - a complete working Tetris game. 
            Requirements:
            - Single HTML file with embedded CSS and JavaScript
            - Classic Tetris gameplay with all 7 tetromino shapes (I, O, T, S, Z, J, L)
            - 10x20 game board grid
            - Keyboard controls: Arrow keys for move left/right/down, Up arrow or Space for rotate
            - Score tracking and level progression
            - Next piece preview
            - Game over detection and restart functionality
            - Line clearing animation
            - Increasing speed as level increases
            - Modern, clean UI with nice colors
            - Pause functionality (P key)
            - Mobile-friendly touch controls""",
            expected_file=Path('tests/output/tetris.html'),
            checks={
                'DOCTYPE': '<!DOCTYPE',
                'JavaScript': '<script',
                'Game board': 'grid',
                'Score tracking': 'score',
                'Tetromino pieces': 'piece',
                'Controls': 'key',
            }
        )
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        total_time = (datetime.now() - self.start_time).total_seconds()
        passed = sum(1 for r in self.results if r['success'])
        total = len(self.results)
        total_size = sum(r['size'] for r in self.results)
        
        print(f'\n{"="*80}')
        print(f'🎯 TEST SUITE SUMMARY')
        print(f'{"="*80}')
        print(f'✅ Passed: {passed}/{total}')
        print(f'⏱️  Total time: {total_time:.1f}s')
        print(f'📦 Total output: {total_size:,} bytes')
        
        print(f'\n📊 Individual Results:')
        for r in self.results:
            status = '✅' if r['success'] else '❌'
            print(f'  {status} {r["name"]}: {r["duration"]:.1f}s, {r["size"]:,} bytes')
        
        if self.config and self.config.openrouter_api_key:
            print(f'\n💰 Estimated cost: ~$0.001 - $0.01 (DeepSeek is very cheap)')
        
        print(f'\n🎮 To view results:')
        for r in self.results:
            if r['file']:
                print(f'  - {r["file"]}')


async def main():
    suite = OpenRouterTestSuite()
    await suite.run_all()


if __name__ == '__main__':
    asyncio.run(main())
