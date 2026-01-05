"""Test Codestral with Non-Tooling Adapter

This tests Codestral (and other non-tooling models) by using a text-only wrapper
that parses responses and executes file operations manually.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.core.agents.non_tooling_adapter import create_with_non_tooling_model
from packages.core.config import init_config


async def test_codestral():
    print('='*80)
    print('Test: Codestral with Non-Tooling Adapter')
    print('='*80)
    
    print('\n📋 Step 1: Loading config...')
    init_config()
    print('✅ Config loaded')
    
    # Output directory
    output_dir = Path('tests/output/codestral_adapter')
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f'📁 Output directory: {output_dir}')
    
    print('\n📋 Step 2: Preparing prompt...')
    output_file = output_dir / 'tetris.html'
    
    prompt = f"""Create a complete working Tetris game and save it to {output_file}.

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

IMPORTANT:
- Generate COMPLETE code - no placeholders or "rest of code" comments
- You can use one file (single HTML with inline CSS/JS) or multiple files
- If using multiple files, mark them like this:

FILE: {output_file}
<html code>

FILE: {output_dir}/styles.css
<css code>

FILE: {output_dir}/app.js
<js code>

Generate complete, working implementations only."""
    
    print('✅ Prompt prepared')
    
    print('\n📋 Step 3: Generating with Codestral (text-only)...')
    print('⏳ This may take 1-2 minutes for complete code generation...\n')
    
    result = await create_with_non_tooling_model(
        model="ollama:codestral",
        prompt=prompt,
        output_path=str(output_file),
        temperature=0.1  # Low temp for more deterministic code
    )
    
    print('\n📊 RESULTS:')
    print(f"Success: {result['success']}")
    print(f"Files created: {len(result['execution']['files_created'])}")
    print(f"Total bytes: {result['execution']['total_bytes']}")
    
    # Show created files
    if result['execution']['files_created']:
        print('\n📄 Created files:')
        for file_path in result['execution']['files_created']:
            path = Path(file_path)
            if path.exists():
                size = path.stat().st_size
                content = path.read_text()
                
                print(f'\n  ✅ {file_path} ({size} bytes)')
                
                # Content checks
                if path.suffix == '.html':
                    check_doctype = "✅" if "<!DOCTYPE" in content else "❌"
                    check_html = "✅" if "<html" in content else "❌"
                    check_logic = "✅" if "<script" in content or "<canvas" in content else "❌"
                    check_pieces = "✅" if "tetromino" in content.lower() or "piece" in content.lower() else "❌"
                    check_score = "✅" if "score" in content.lower() else "❌"
                    
                    print(f'    {check_doctype} Has DOCTYPE')
                    print(f'    {check_html} Has HTML tag')
                    print(f'    {check_logic} Has game logic')
                    print(f'    {check_pieces} Has pieces')
                    print(f'    {check_score} Has score tracking')
    
    # Show failures
    if result['execution']['files_failed']:
        print('\n❌ Failed files:')
        for failed in result['execution']['files_failed']:
            print(f"  - {failed['path']}: {failed['error']}")
    
    # Show first 500 chars of response
    print(f'\n📝 Response preview (first 500 chars):')
    print('-'*80)
    print(result['response_text'][:500])
    print('-'*80)
    
    if result['success']:
        print(f'\n🎮 SUCCESS! Open {output_file} in your browser to play!')
    else:
        print('\n❌ Generation failed. Check logs above.')
    
    return result


async def compare_models():
    """Compare Codestral vs Qwen for code quality."""
    print('='*80)
    print('COMPARISON: Codestral vs Qwen2.5-Coder')
    print('='*80)
    
    init_config()
    
    # Simple test prompt
    prompt = """Create a complete HTML5 calculator with these features:
- Basic operations: +, -, *, /
- Clear and equals buttons
- Display for input/output
- Modern styling with CSS
- All JavaScript logic included

Save as a single HTML file with inline CSS and JavaScript.
Generate COMPLETE code - no placeholders."""
    
    models_to_test = [
        ("ollama:codestral", "codestral_adapter/calculator.html"),
        ("ollama:qwen2.5-coder:14b", "qwen_adapter/calculator.html"),
    ]
    
    results = {}
    
    for model, output_path in models_to_test:
        print(f'\n{"="*60}')
        print(f'Testing: {model}')
        print(f'{"="*60}')
        
        full_output = Path(f'tests/output/{output_path}')
        full_output.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            result = await create_with_non_tooling_model(
                model=model,
                prompt=prompt,
                output_path=str(full_output),
                temperature=0.1
            )
            results[model] = result
        except Exception as e:
            print(f'❌ {model} failed: {e}')
            results[model] = {'success': False, 'error': str(e)}
    
    # Summary comparison
    print('\n' + '='*80)
    print('COMPARISON RESULTS')
    print('='*80)
    
    for model, result in results.items():
        if isinstance(result, dict) and result.get('success'):
            print(f'\n{model}:')
            print(f"  ✅ Files: {len(result['execution']['files_created'])}")
            print(f"  📦 Bytes: {result['execution']['total_bytes']}")
            print(f"  📄 Files: {result['execution']['files_created']}")
        else:
            print(f'\n{model}:')
            print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'compare':
        asyncio.run(compare_models())
    else:
        asyncio.run(test_codestral())
