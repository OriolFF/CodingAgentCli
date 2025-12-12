#!/usr/bin/env python3
"""Direct test of file editor agent with logging."""

import asyncio
import logging
from packages.core.agents.file_editor import edit_files
from packages.core.config import init_config

# Enable debug logging
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s'
)

async def test():
    init_config()
    
    print("=" * 80)
    print("Testing file editor directly")
    print("=" * 80)
    
    result = await edit_files('create sandbox/test_calc.py with a simple add function')
    
    print(f"\nSUCCESS: {result.success}")
    print(f"\nRESULT:\n{result.changes_summary}")
    print("=" * 80)
    
    # Check if file was created
    from pathlib import Path
    test_file = Path("sandbox/test_calc.py")
    if test_file.exists():
        print("\n✅ FILE CREATED!")
        print(f"Content:\n{test_file.read_text()}")
    else:
        print("\n❌ FILE NOT CREATED")

if __name__ == "__main__":
    asyncio.run(test())
