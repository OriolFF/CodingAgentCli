"""Test code generation with OpenRouter models.

Usage:
1. Copy .env.openrouter to .env
2. Add your OPENROUTER_API_KEY
3. Run: uv run python test_openrouter_code_gen.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from packages.core.agents.delegation import delegate_task
from packages.core.config import init_config

async def test_openrouter():
    print('='*80)
    print('Test: OpenRouter Code Generation')
    print('='*80)
    
    config = init_config()
    print(f'\nConfiguration:')
    print(f'  CODE_GENERATOR_MODEL: {config.code_generator_model}')
    print(f'  COORDINATOR_MODEL: {config.coordinator_model}')
    print(f'  OpenRouter API Key: {"✅ Set" if config.openrouter_api_key else "❌ Not set"}')
    
    if not config.openrouter_api_key:
        print(f'\n❌ ERROR: OPENROUTER_API_KEY not set in .env')
        print(f'Solution: Add OPENROUTER_API_KEY=your-key-here to .env')
        return
    
    print(f'\n🚀 Generating code with OpenRouter...')
    
    command = """create tests/output/fibonacci.py with a function that calculates fibonacci numbers using memoization"""
    
    result = await delegate_task(command)
    
    print(f'\nSuccess: {result.success}')
    print(f'Result: {result.result[:200]}...')
    
    # Check if file was created
    fib_file = Path('tests/output/fibonacci.py')
    if fib_file.exists():
        content = fib_file.read_text()
        print(f'\n✅ File created: {fib_file} ({fib_file.stat().st_size} bytes)')
        print(f'\n📄 Content:\n{content}')
    else:
        print(f'\n❌ File NOT created: {fib_file}')

if __name__ == '__main__':
    asyncio.run(test_openrouter())
