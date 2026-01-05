"""Test Tetris Game Generation with OpenRouter"""

import asyncio
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.core.agents.delegation import delegate_task
from packages.core.config import init_config, get_config


def get_model_folder_name() -> str:
    """Get sanitized model name for folder naming.
    
    Returns:
        Sanitized model name suitable for folder name
    """
    config = get_config()
    # Get the code generator model (used for code generation)
    model_name = config.get_agent_model("code_generator")
    
    # Sanitize: remove 'ollama:' prefix, replace special chars with underscores
    sanitized = re.sub(r'^(ollama|openai|google-gla):', '', model_name)
    sanitized = re.sub(r'[:/\\\s.<>"|?*]', '_', sanitized)
    
    return sanitized

async def test_tetris():
    print('='*80)
    print('Test: Tetris Game Generation')
    print('='*80)
    
    print('\n📋 Step 1: Loading config...')
    init_config()
    print('✅ Config loaded')
    
    # Get model-specific output folder
    model_folder = get_model_folder_name()
    output_dir = Path(f'tests/output/{model_folder}')
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f'📁 Output directory: {output_dir}')
    
    print('\n📋 Step 2: Preparing command...')
    command = f"""Create a complete working Tetris game in {output_dir}/.

STRUCTURE: Use THREE separate files (HTML, CSS, JavaScript) with proper linking.

REQUIREMENTS:
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

IMPORTANT: 
- Generate complete, working code with NO placeholders
- Split into HTML, CSS, and JS files properly linked together"""
    print('✅ Command prepared')
    
    print('\n📋 Step 3: Delegating task...')
    result = await delegate_task(command)
    print('✅ Task delegated')
    
    print(f'\nSuccess: {result.success}')
    print(f'Result: {result.result[:200]}...')
    
    # Check if file was created
    tetris_file = output_dir / 'tetris.html'
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
