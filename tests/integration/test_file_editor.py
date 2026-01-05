#!/usr/bin/env python3
"""Test script for file editor agent."""

import asyncio
from packages.core.agents.delegation import delegate_task
from packages.core.config import init_config

async def test():
    init_config()
    
    print("=" * 80)
    print("Testing file creation via delegation")
    print("=" * 80)
    
    result = await delegate_task('create a file sandbox/calculator.py with functions add, subtract, multiply, divide')
    
    print(f"\nSUCCESS: {result.success}")
    print(f"AGENTS USED: {result.agents_used}")
    print(f"\nRESULT:\n{result.result[:500]}")
    print("=" * 80)
    
    # Check if file was created
    from pathlib import Path
    calc_file = Path("sandbox/calculator.py")
    if calc_file.exists():
        print("\n✅ FILE CREATED!")
        print(f"Content:\n{calc_file.read_text()}")
    else:
        print("\n❌ FILE NOT CREATED")

if __name__ == "__main__":
    asyncio.run(test())
