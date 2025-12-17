"""Test Tetris Game Generation with OpenRouter"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from packages.core.agents.delegation import delegate_task
from packages.core.config import init_config

async def test_tetris():
    print('='*80)
    print('Test: Tetris Game Generation')
    print('='*80)
    
    print('\n📋 Step 1: Loading config...')
    init_config()
    print('✅ Config loaded')
    
    print('\n📋 Step 2: Preparing command...')
    command = """create tests/output/tetris.html - a complete working Tetris game. 
    Requirements:
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
    - Mobile-friendly touch controls
    
    You can organize the code however you prefer (single file or multiple files like HTML + CSS + JS).
    Generate complete, working implementations - no placeholder comments or incomplete code."""
    print('✅ Command prepared')
    
    print('\n📋 Step 3: Delegating task...')
    result = await delegate_task(command)
    print('✅ Task delegated')
    
    print(f'\nSuccess: {result.success}')
    print(f'Result: {result.result[:200]}...')
    
    # Check if file was created
    tetris_file = Path('tests/output/tetris.html')
    if tetris_file.exists():
        size = tetris_file.stat().st_size
        content = tetris_file.read_text()
        print(f'\n✅ File created: {tetris_file} ({size} bytes)')
        print(f'\n📋 Content Checks:')
        print(f'  {"✅" if "<!DOCTYPE" in content else "❌"} Has DOCTYPE')
        print(f'  {"✅" if "<html" in content else "❌"} Has HTML tag')
        print(f'  {"✅" if "<script" in content else "❌"} Has JavaScript')
        print(f'  {"✅" if "<canvas" in content or "grid" in content.lower() else "❌"} Has game board')
        print(f'  {"✅" if "tetromino" in content.lower() or "piece" in content.lower() else "❌"} Has pieces')
        print(f'  {"✅" if "score" in content.lower() else "❌"} Has score tracking')
        print(f'  {"✅" if "function" in content or "const" in content else "❌"} Has game logic')
        print(f'\n📄 First 300 chars:\n{content[:300]}')
        
        print(f'\n🎮 To play: Open {tetris_file} in your browser!')
    else:
        print(f'\n❌ File NOT created: {tetris_file}')

if __name__ == '__main__':
    asyncio.run(test_tetris())
