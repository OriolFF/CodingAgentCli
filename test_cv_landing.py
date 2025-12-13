#!/usr/bin/env python3
"""Test specifically for Material 3 CV landing page - with detailed logging."""

import asyncio
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.core.agents.delegation import delegate_task
from packages.core.config import init_config

# Enable detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(levelname)s - %(message)s'
)

async def test_cv_landing():
    init_config()
    
    print("=" * 80)
    print("Test 31: Material 3 CV Landing Page")
    print("=" * 80)
    
    command = """create sandbox/cv_landing.html - a nice landing web page following Material 3 design guidelines to serve as a CV for an Android engineer. Include experience at Google (Senior Android Engineer, 2020-2023, worked on Play Store), Meta (Android Developer, 2018-2020, Instagram team), and Spotify (Junior Android Developer, 2016-2018, mobile player). Add sections for: hero with name and title, work experience timeline, technical skills (Kotlin, Java, Jetpack Compose, MVVM, Coroutines), side projects, and contact. Use Material 3 colors, typography, and elevation patterns."""
    
    print(f"\nCommand: {command[:100]}...")
    print("\nExecuting...\n")
    
    result = await delegate_task(command)
    
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"Success: {result.success}")
    print(f"Agents Used: {result.agents_used}")
    print(f"\nResult Preview:\n{result.result[:500]}...")
    
    # Check if file was created
    cv_file = Path("sandbox/cv_landing.html")
    if cv_file.exists():
        print(f"\n✅ FILE CREATED: {cv_file}")
        print(f"Size: {cv_file.stat().st_size} bytes")
        
        # Check for Material 3 elements
        content = cv_file.read_text()
        checks = {
            "Material 3 reference": any(m in content.lower() for m in ["material", "material 3", "material design"]),
            "Google experience": "google" in content.lower() and "play store" in content.lower(),
            "Meta experience": "meta" in content.lower() and "instagram" in content.lower(),
            "Spotify experience": "spotify" in content.lower(),
            "Skills section": any(s in content.lower() for s in ["kotlin", "jetpack compose", "mvvm"]),
            "Hero section": any(h in content.lower() for h in ["hero", "header", "h1"]),
            "Timeline/Experience": any(t in content.lower() for t in ["timeline", "experience", "work"]),
        }
        
        print("\n📋 Content Checks:")
        for check, passed in checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")
            
    else:
        print(f"\n❌ FILE NOT CREATED: {cv_file}")
    
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_cv_landing())
