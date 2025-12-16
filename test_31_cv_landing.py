"""Test 31: Material 3 CV Landing Page"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.core.agents.delegation import delegate_task
from packages.core.config import init_config

async def test_31():
    print('='*80)
    print('Test 31: Material 3 CV Landing Page')
    print('='*80)
    
    init_config()
    
    command = """create tests/output/cv_landing.html - a nice landing web page following Material 3 design guidelines to serve as a CV for an Android engineer. 
    Include experience at Google (Senior Android Engineer, 2020-2023, worked on Play Store), 
    Meta (Android Developer, 2018-2020, Instagram team), and Spotify (Junior Android Developer, 2016-2018, mobile player). 
    Add sections for: hero with name and title, work experience timeline, technical skills (Kotlin, Java, Jetpack Compose, MVVM, Coroutines), 
    side projects, and contact. Use Material 3 colors, typography, and elevation patterns.
    Use a parallax effect and a soft gradient background. Add a contact form with name, email, and message fields."""
    
    result = await delegate_task(command)
    
    print(f'\nSuccess: {result.success}')
    print(f'Result: {result.result[:200]}...')
    
    # Check if file was created
    cv_file = Path('tests/output/cv_landing.html')
    if cv_file.exists():
        size = cv_file.stat().st_size
        content = cv_file.read_text()
        print(f'\n✅ File created: {cv_file} ({size} bytes)')
        print(f'\n📋 Content Checks:')
        print(f'  {"✅" if "<!DOCTYPE" in content else "❌"} Has DOCTYPE')
        print(f'  {"✅" if "<html" in content else "❌"} Has HTML tag')
        print(f'  {"✅" if "<head>" in content or "<head " in content else "❌"} Has head section')
        print(f'  {"✅" if "<body" in content else "❌"} Has body section')
        print(f'  {"✅" if "<style" in content or ".css" in content else "❌"} Has CSS')
        print(f'  {"✅" if "Material" in content or "--md-" in content else "❌"} Material 3 ref')
        print(f'  {"✅" if "Google" in content else "❌"} Has Google experience')
        print(f'  {"✅" if "Meta" in content else "❌"} Has Meta experience')
        print(f'  {"✅" if "Spotify" in content else "❌"} Has Spotify experience')
        print(f'\n📄 First 500 chars:\n{content[:500]}')
    else:
        print(f'\n❌ File NOT created: {cv_file}')

if __name__ == '__main__':
    asyncio.run(test_31())
