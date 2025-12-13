#!/usr/bin/env python3
"""Test code generator agent with coordinator delegation."""

import asyncio
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from packages.core.agents.delegation import delegate_task
from packages.core.config import init_config

# Enable detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s'
)

async def test_code_generator():
    init_config()
    
    print("=" * 80)
    print("TEST: Code Generator Agent via Coordinator")
    print("=" * 80)
    
    # Test 1: Create Python file
    print("\n📋 Test 1: Generate Python function")
    print("-" * 80)
    
    result1 = await delegate_task(
        "create sandbox/greet.py with a greet(name) function that returns a greeting"
    )
    
    print(f"Success: {result1.success}")
    print(f"Agents Used: {result1.agents_used}")
    print(f"Result: {result1.result[:200]}...")
    
    greet_file = Path("sandbox/greet.py")
    if greet_file.exists():
        print(f"✅ File created: {greet_file} ({greet_file.stat().st_size} bytes)")
        print(f"Content:\n{greet_file.read_text()}")
    else:
        print(f"❌ File NOT created: {greet_file}")
    
    # Test 2: Create HTML with Material 3 (original failing test)
    print("\n" + "=" * 80)
    print("📋 Test 2: Generate Material 3 HTML Landing Page")
    print("-" * 80)
    
    result2 = await delegate_task(
        "create sandbox/cv_m3.html - a Material 3 landing page for an Android engineer CV"
    )
    
    print(f"Success: {result2.success}")
    print(f"Agents Used: {result2.agents_used}")
    print(f"Result snippet: {result2.result[:300]}...")
    
    html_file = Path("sandbox/cv_m3.html")
    if html_file.exists():
        print(f"✅ File created: {html_file} ({html_file.stat().st_size} bytes)")
        
        # Check for key elements
        content = html_file.read_text()
        checks = {
            "Has DOCTYPE": "<!DOCTYPE" in content,
            "Has HTML tag": "<html" in content,
            "Has head section": "<head" in content,
            "Has body section": "<body" in content,
            "Has CSS": "<style" in content or "style=" in content,
            "Material 3 ref": "material" in content.lower() or "md-" in content.lower(),
        }
        
        print("\n📋 Content Checks:")
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")
    else:
        print(f"❌ File NOT created: {html_file}")
    
    # Test 3: CSS file
    print("\n" + "=" * 80)
    print("📋 Test 3: Generate CSS file")
    print("-" * 80)
    
    result3 = await delegate_task(
        "create sandbox/styles.css with Material 3 color tokens and basic styles"
    )
    
    print(f"Success: {result3.success}")
    css_file = Path("sandbox/styles.css")
    if css_file.exists():
        print(f"✅ File created: {css_file} ({css_file.stat().st_size} bytes)")
    else:
        print(f"❌ File NOT created: {css_file}")
    
    print("\n" + "=" * 80)
    print("🎯 SUMMARY")
    print("=" * 80)
    print(f"Total tests: 3")
    files_created = sum([
        greet_file.exists(),
        html_file.exists(),
        css_file.exists()
    ])
    print(f"Files created: {files_created}/3")
    
    if files_created == 3:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"⚠️ {3 - files_created} test(s) failed")

if __name__ == "__main__":
    asyncio.run(test_code_generator())
