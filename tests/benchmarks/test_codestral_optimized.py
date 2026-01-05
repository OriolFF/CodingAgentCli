"""Test Codestral with Optimized Adapter

Tests the optimized Codestral adapter that uses:
- Instruction following mode (not FIM)
- Aggressive prompting for complete code
- Temperature=0 for deterministic output
- Validation of output quality
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.core.agents.codestral_optimized import create_with_codestral_optimized
from packages.core.config import init_config


async def test_codestral_optimized():
    print('='*80)
    print('Test: Codestral OPTIMIZED Adapter')
    print('Based on Mistral AI documentation best practices')
    print('='*80)
    
    init_config()
    
    output_dir = Path('tests/output/codestral_optimized')
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f'📁 Output: {output_dir}')
    
    print('\n📋 Preparing enhanced prompt...')
    output_file = output_dir / 'tetris.html'
    
    prompt = f"""Create a COMPLETE, WORKING Tetris game.

MANDATORY FEATURES (all must be fully implemented):
1. All 7 tetromino shapes (I, O, T, S, Z, J, L) - fully defined with rotations
2. 10x20 game board with collision detection
3. Keyboard controls: arrows + space/up for rotate
4. Score tracking with level progression
5. Next piece preview
6. Game over detection and restart
7. Line clearing with animation
8. Speed increases with level
9. Pause functionality (P key)

TECHNICAL REQUIREMENTS:
- Single HTML file with embedded CSS and JavaScript
- Complete game loop implementation
- All event handlers fully coded
- Proper piece rotation logic
- Complete collision detection
- Full rendering system

FILE STRUCTURE:
Save as: {output_file}

CRITICAL: This must be production-ready code that runs immediately.
Generate the COMPLETE implementation with ALL logic, NO placeholders."""

    print('\n🚀 Generating with OPTIMIZED Codestral...')
    print('   - Using instruction-following mode')
    print('   - Temperature: 0.0 (deterministic)')
    print('   - Enforcing complete code generation')
    print('   - Expected: 200+ lines minimum')
    print('\n⏳ Generating (this may take 1-2 minutes)...\n')
    
    result = await create_with_codestral_optimized(
        prompt=prompt,
        output_path=str(output_file),
        expected_min_lines=200  # Tetris should be at least 200 lines
    )
    
    print('\n' + '='*80)
    print('📊 GENERATION RESULTS')
    print('='*80)
    
    print(f"\nSuccess: {result['success']}")
    print(f"Files created: {len(result['execution']['files_created'])}")
    print(f"Total bytes: {result['execution']['total_bytes']}")
    
    if result.get('quality_warning'):
        print("\n⚠️  WARNING: Output may be shorter than expected (possible skeleton code)")
    
    # Analyze created files
    if result['execution']['files_created']:
        print('\n📄 Created files:')
        for file_path in result['execution']['files_created']:
            path = Path(file_path)
            if path.exists():
                size = path.stat().st_size
                content = path.read_text()
                lines = [l for l in content.split('\n') if l.strip()]
                code_lines = [l for l in lines if not l.strip().startswith('//') and not l.strip().startswith('/*')]
                
                print(f'\n  ✅ {path.name} ({size} bytes, {len(code_lines)} code lines)')
                
                # Quality checks for HTML
                if path.suffix == '.html':
                    checks = {
                        'DOCTYPE': '<!DOCTYPE' in content,
                        'HTML structure': '<html' in content,
                        'Canvas/Grid': '<canvas' in content or 'grid' in content.lower(),
                        'JavaScript': '<script' in content,
                        'Game loop': 'setInterval' in content or 'requestAnimationFrame' in content,
                        'Tetrominoes': 'tetromino' in content.lower() or 'shapes' in content.lower(),
                        'Score': 'score' in content.lower(),
                        'Collision': 'collision' in content.lower(),
                        'Rotation': 'rotate' in content.lower(),
                        'Controls': 'keydown' in content.lower() or 'addEventListener' in content
                    }
                    
                    print('\n  Quality Checks:')
                    passed = 0
                    for check_name, passed_check in checks.items():
                        symbol = "✅" if passed_check else "❌"
                        print(f'    {symbol} {check_name}')
                        if passed_check:
                            passed += 1
                    
                    print(f'\n  Score: {passed}/{len(checks)} checks passed')
                    
                    # Check for placeholders (bad signs)
                    bad_patterns = [
                        '...rest of',
                        'rest of the code',
                        'TODO:',
                        '// Add',
                        '// Implement',
                        'out of scope',
                        'beyond the scope'
                    ]
                    
                    found_placeholders = []
                    for pattern in bad_patterns:
                        if pattern.lower() in content.lower():
                            found_placeholders.append(pattern)
                    
                    if found_placeholders:
                        print(f'\n  ⚠️  PLACEHOLDERS DETECTED:')
                        for placeholder in found_placeholders:
                            print(f'      - "{placeholder}"')
                    else:
                        print('\n  ✅ No placeholders detected')
    
    # Show response preview
    print(f'\n📝 Response preview (first 600 chars):')
    print('-'*80)
    print(result['response_text'][:600])
    print('-'*80)
    
    if result['success']:
        total_bytes = result['execution']['total_bytes']
        if total_bytes > 5000:  # Reasonable size for complete Tetris
            print(f'\n✅ SUCCESS! Generated {total_bytes} bytes of code')
            print(f'🎮 Open {output_file} in your browser to test!')
        elif total_bytes > 1000:
            print(f'\n⚠️  PARTIAL: Generated {total_bytes} bytes (better than before, but verify completeness)')
            print(f'🔍 Check {output_file} for any placeholders')
        else:
            print(f'\n❌ LIKELY SKELETON: Only {total_bytes} bytes generated')
            print('   Model still refusing to generate complete code')
    else:
        print('\n❌ Generation failed')
    
    return result


async def test_simple_function():
    """Test with a simpler task to see if Codestral works better with smaller scope."""
    print('\n' + '='*80)
    print('Test: Simple Function Generation (Codestral sweet spot)')
    print('='*80)
    
    init_config()
    
    output_dir = Path('tests/output/codestral_optimized')
    output_file = output_dir / 'calculator.html'
    
    prompt = f"""Create a COMPLETE HTML calculator.

FEATURES:
- Basic operations: +, -, *, /
- Clear button
- Number pad (0-9)
- Display for input/output
- Modern styling

REQUIREMENTS:
- Single HTML file
- Complete JavaScript implementation
- All button handlers
- Full calculation logic
- Clean CSS styling

Save as: {output_file}

Generate the COMPLETE, WORKING code."""
    
    print('\n🚀 Testing simpler task...\n')
    
    result = await create_with_codestral_optimized(
        prompt=prompt,
        output_path=str(output_file),
        expected_min_lines=80  # Calculator should be ~80-100 lines
    )
    
    print(f'\n📊 Simple task result:')
    print(f"  Files: {len(result['execution']['files_created'])}")
    print(f"  Bytes: {result['execution']['total_bytes']}")
    
    if result['execution']['total_bytes'] > 2000:
        print(f"  ✅ Good size - likely complete")
    else:
        print(f"  ⚠️  Small size - may be skeleton")
    
    return result


async def main():
    """Run all tests."""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'simple':
            # Test with simpler task
            await test_simple_function()
        elif sys.argv[1] == 'both':
            # Test both
            print('Testing simple task first...\n')
            await test_simple_function()
            print('\n\nNow testing complex task...\n')
            await test_codestral_optimized()
    else:
        # Default: test Tetris
        await test_codestral_optimized()


if __name__ == '__main__':
    asyncio.run(main())
