"""Test landing page generation with Material 3 design."""

import asyncio
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.core.config.config import init_config, get_config
from packages.core.agents.delegation import delegate_task


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
    sanitized = re.sub(r'[:/\\s.<>"|?*]', '_', sanitized)
    
    return sanitized


async def test_landing_page():
    """Test landing page generation."""
    
    print("="*80)
    print("Test: Landing Page Generation (Material 3 Design)")
    print("="*80)
    
    # Initialize config
    print("\n📋 Step 1: Loading config...")
    init_config()
    config = get_config()
    print("✅ Config loaded")
    
    # Get model info
    model_name = config.get_agent_model("code_generator")
    print(f"🤖 Using model: {model_name}")
    
    # Create model-specific output directory
    model_folder = get_model_folder_name()
    output_dir = Path(f"tests/output/{model_folder}")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {output_dir}")
    
    # Prepare command
    print("\n📋 Step 2: Preparing command...")
    command = f"""Create {output_dir}/landing.html - a modern landing page with Material 3 design.
    
Requirements:
- Beautiful Material 3 color scheme
- Hero section with CTA button
- Features section (3-4 features)
- Testimonials section
- Contact form
- Responsive design
- Smooth animations
- Modern typography"""
    
    print("✅ Command prepared")
    
    # Delegate task
    print("\n📋 Step 3: Delegating task...")
    result = await delegate_task(command)
    print("✅ Task delegated")
    
    print(f"\nSuccess: {result.success}")
    print(f"Result: {result.result[:200]}...")
    
    # Check if file was created
    output_file = output_dir / "landing.html"
    if output_file.exists():
        file_size = output_file.stat().st_size
        print(f"\n✅ File created: {output_file} ({file_size} bytes)")
        
        # Read and check content
        content = output_file.read_text()
        
        print("\n📋 Content Checks:")
        checks = [
            ("Has DOCTYPE", "<!DOCTYPE html>" in content),
            ("Has HTML tag", "<html" in content),
            ("Has CSS/Style", "<style>" in content or "stylesheet" in content),
            ("Has Hero section", any(x in content.lower() for x in ["hero", "banner", "jumbotron"])),
            ("Has CTA button", any(x in content.lower() for x in ["button", "cta", "call-to-action"])),
            ("Has Features", "feature" in content.lower()),
            ("Has Form", "<form" in content.lower() or "contact" in content.lower()),
        ]
        
        for check_name, passed in checks:
            icon = "✅" if passed else "❌"
            print(f"  {icon} {check_name}")
        
        print(f"\n📄 First 300 chars:")
        print(content[:300])
        
        print(f"\n🌐 Open {output_file} in your browser to view!")
    else:
        print(f"\n❌ File NOT created: {output_file}")


if __name__ == "__main__":
    asyncio.run(test_landing_page())
