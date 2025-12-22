"""Unified Test Suite Runner - Organizes outputs by model name."""

import asyncio
import sys
import re
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from packages.core.config import init_config, get_config


def get_model_folder_name() -> str:
    """Get sanitized model name for folder naming.
    
    Returns:
        Sanitized model name suitable for folder name
    """
    config = get_config()
    # Get the code generator model (used for code generation)
    model_name = config.get_agent_model("code_generator")
    
    # Sanitize: remove provider prefix, replace special chars with underscores
    sanitized = re.sub(r'^(ollama|openai|google-gla):', '', model_name)
    sanitized = re.sub(r'[:/\\s.<>"|?*]', '_', sanitized)
    
    return sanitized


async def run_test(test_name: str, test_func, output_dir: Path):
    """Run a single test and track results.
    
    Args:
        test_name: Display name for the test
        test_func: Async function to run
        output_dir: Output directory for this test
        
    Returns:
        dict with test results
    """
    print(f"\n{'='*80}")
    print(f"Running: {test_name}")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    success = False
    error = None
    
    try:
        await test_func(output_dir)
        success = True
    except Exception as e:
        error = str(e)
        print(f"\n❌ Test failed with error: {error}")
    
    duration = time.time() - start_time
    
    return {
        "name": test_name,
        "success": success,
        "duration": duration,
        "error": error
    }


async def test_landing_page_runner(output_dir: Path):
    """Test landing page generation."""
    from test_landing_page import test_landing_page
    
    # Monkey-patch the output directory
    import test_landing_page as tlp_module
    original_path = Path("tests/output")
    
    # Update to use model-specific directory
    tlp_module.Path = lambda p: output_dir if str(p) == "tests/output" else Path(p)
    
    await test_landing_page()


async def test_tetris_runner(output_dir: Path):
    """Test Tetris game generation."""
    from packages.core.agents.delegation import delegate_task
    
    print('📋 Preparing Tetris generation...')
    tetris_file = output_dir / 'tetris.html'
    
    command = f"""create {tetris_file} - a complete working Tetris game. 
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
    
    Generate complete, working implementations - no placeholder comments or incomplete code."""
    
    result = await delegate_task(command)
    
    if tetris_file.exists():
        size = tetris_file.stat().st_size
        content = tetris_file.read_text()
        print(f'✅ Tetris created: {tetris_file} ({size} bytes)')
        
        # Run checks
        checks = [
            ("Has DOCTYPE", "<!DOCTYPE" in content),
            ("Has HTML tag", "<html" in content),
            ("Has JavaScript", "<script" in content),
            ("Has game board", "<canvas" in content or "grid" in content.lower()),
            ("Has pieces", "tetromino" in content.lower() or "piece" in content.lower()),
            ("Has score tracking", "score" in content.lower()),
            ("Has game logic", "function" in content or "const" in content),
        ]
        
        print('\n📋 Content Checks:')
        for check_name, passed in checks:
            icon = "✅" if passed else "❌"
            print(f'  {icon} {check_name}')
    else:
        raise Exception(f"File not created: {tetris_file}")


async def test_cv_landing_runner(output_dir: Path):
    """Test CV landing page generation."""
    from packages.core.agents.delegation import delegate_task
    
    print('📋 Preparing CV landing page generation...')
    cv_file = output_dir / 'cv_landing.html'
    
    command = f"""Create {cv_file} - a professional CV/Resume landing page with Material 3 design.
    
Requirements:
- Modern Material 3 color scheme with gradients
- Professional header with photo placeholder
- About Me section
- Skills section with progress bars
- Work Experience timeline
- Education section
- Projects/Portfolio showcase
- Contact information and social links
- Responsive design
- Smooth scroll animations
- Print-friendly CSS

Generate complete, working code - no placeholders."""
    
    result = await delegate_task(command)
    
    if cv_file.exists():
        size = cv_file.stat().st_size
        content = cv_file.read_text()
        print(f'✅ CV Landing created: {cv_file} ({size} bytes)')
        
        checks = [
            ("Has DOCTYPE", "<!DOCTYPE" in content),
            ("Has HTML", "<html" in content),
            ("Has CSS", "<style>" in content or "stylesheet" in content),
            ("Has Skills", "skill" in content.lower()),
            ("Has Experience", "experience" in content.lower() or "work" in content.lower()),
            ("Has Contact", "contact" in content.lower()),
        ]
        
        print('\n📋 Content Checks:')
        for check_name, passed in checks:
            icon = "✅" if passed else "❌"
            print(f'  {icon} {check_name}')
    else:
        raise Exception(f"File not created: {cv_file}")


async def main():
    """Run all tests with model-specific output organization."""
    print("="*80)
    print("UNIFIED TEST SUITE RUNNER")
    print("="*80)
    
    # Initialize config
    print("\n📋 Initializing configuration...")
    init_config()
    config = get_config()
    
    # Get model info
    model_name = config.get_agent_model("code_generator")
    model_folder = get_model_folder_name()
    
    print(f"\n🤖 Testing with model: {model_name}")
    print(f"📁 Output folder: tests/output/{model_folder}")
    
    # Create output directory
    output_dir = Path(f"tests/output/{model_folder}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define tests to run
    tests = [
        ("Landing Page Generation", test_landing_page_runner),
        ("Tetris Game Generation", test_tetris_runner),
        ("CV Landing Page Generation", test_cv_landing_runner),
    ]
    
    # Run all tests
    results = []
    start_time = time.time()
    
    for test_name, test_func in tests:
        result = await run_test(test_name, test_func, output_dir)
        results.append(result)
    
    total_duration = time.time() - start_time
    
    # Print summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}\n")
    
    print(f"Model: {model_name}")
    print(f"Output Directory: {output_dir}")
    print(f"Total Duration: {total_duration:.1f}s\n")
    
    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed
    
    print(f"Results: {passed}/{len(results)} tests passed")
    
    if failed > 0:
        print(f"\n❌ Failed Tests:")
        for result in results:
            if not result["success"]:
                print(f"  - {result['name']}: {result['error']}")
    
    print(f"\n📊 Detailed Results:")
    for result in results:
        icon = "✅" if result["success"] else "❌"
        print(f"  {icon} {result['name']} ({result['duration']:.1f}s)")
    
    # Generate summary file
    summary_file = output_dir / "test_summary.md"
    with open(summary_file, "w") as f:
        f.write(f"# Test Summary - {model_name}\n\n")
        f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Model**: `{model_name}`\n")
        f.write(f"**Total Duration**: {total_duration:.1f}s\n")
        f.write(f"**Results**: {passed}/{len(results)} tests passed\n\n")
        
        f.write("## Test Results\n\n")
        for result in results:
            icon = "✅" if result["success"] else "❌"
            f.write(f"### {icon} {result['name']}\n")
            f.write(f"- Duration: {result['duration']:.1f}s\n")
            f.write(f"- Status: {'PASSED' if result['success'] else 'FAILED'}\n")
            if result["error"]:
                f.write(f"- Error: `{result['error']}`\n")
            f.write("\n")
        
        f.write("## Generated Files\n\n")
        for file in output_dir.iterdir():
            if file.is_file() and file.suffix in ['.html', '.css', '.js']:
                size = file.stat().st_size
                f.write(f"- `{file.name}` ({size} bytes)\n")
    
    print(f"\n📄 Summary saved to: {summary_file}")
    print(f"\n🎉 Test suite complete! Check {output_dir} for outputs.")


if __name__ == "__main__":
    asyncio.run(main())
