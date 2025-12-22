"""Demo script to showcase improved agent delegation logging."""

import asyncio
import sys
from packages.core.agents.delegation import delegate_task
from packages.core.config import get_config

async def demo_logging():
    """Demonstrate the improved logging system."""
    
    print("="*80)
    print("AGENT DELEGATION LOGGING DEMO")
    print("="*80)
    print()
    print("This demo shows the enhanced logging that tracks:")
    print("  • When the coordinator delegates to sub-agents")
    print("  • When sub-agents start processing")
    print("  • When sub-agents finish and return to coordinator")
    print("  • The complete flow from user → coordinator → sub-agents → coordinator → user")
    print()
    print("="*80)
    print()
    
    # Demo request: generate a simple HTML file
    request = "Create a simple HTML file at tests/output/demo.html with a hello world message"
    
    print(f"Sending test request: {request}")
    print()
    
    try:
        result = await delegate_task(request)
        
        print("\n" + "="*80)
        print("DELEGATION COMPLETE")
        print("="*80)
        print(f"Success: {result.success}")
        print(f"Agents used: {result.agents_used}")
        print(f"Task summary: {result.task_summary}")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Error during delegation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Load config
    config = get_config()
    print(f"🤖 Using coordinator model: {config.coordinator_model}")
    print(f"📁 Output directory: tests/output\n")
    
    # Run demo
    asyncio.run(demo_logging())
