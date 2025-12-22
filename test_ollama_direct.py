"""Test cogito:14b directly with unlimited num_predict parameter."""

import requests
import json

# Test Tetris generation with unlimited tokens
url = "http://localhost:11434/api/generate"

prompt = """Create a complete working Tetris game. Requirements:
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

Generate complete, working code - no placeholder comments or incomplete code."""

payload = {
    "model": "cogito:14b",
    "prompt": prompt,
    "stream": False,
    "options": {
        "num_predict": -1,  # Unlimited tokens
        "num_ctx": 8192,    # Large context window
        "temperature": 0.7,
    }
}

print("Sending request to Ollama...")
print(f"Model: cogito:14b")
print(f"num_predict: -1 (unlimited)")
print(f"num_ctx: 8192")
print("\nWaiting for response...\n")

response = requests.post(url, json=payload)
result = response.json()

if "response" in result:
    output = result["response"]
    print(f"Response length: {len(output)} characters")
    print(f"\nFirst 500 chars:")
    print(output[:500])
    print(f"\nLast 500 chars:")
    print(output[-500:])
    
    # Save to file
    with open("/tmp/cogito_test_tetris.html", "w") as f:
        f.write(output)
    print(f"\nSaved to: /tmp/cogito_test_tetris.html")
else:
    print(f"Error: {result}")
