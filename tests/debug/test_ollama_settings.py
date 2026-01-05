"""Simple test to verify Ollama settings are passed correctly."""

import asyncio
from pydanticai_ollama.models.ollama import OllamaModel, OllamaModelSettings
from pydantic_ai import Agent

async def test_ollama_settings():
    print("Testing OllamaModel with custom settings...")
    
    # Create settings
    settings = OllamaModelSettings(
        num_predict=-1,
        num_ctx=32768,  # Increased to match ollama chat behavior
        temperature=0.7,
    )
    
    print(f"Settings created: {settings}")
    
    # Create model
    model = OllamaModel(
        model_name="cogito:14b",
        settings=settings,
    )
    
    print(f"Model created: {model}")
    
    # Create agent
    agent = Agent(
        model,
        output_type=str,
        system_prompt="You are a code generator. Generate ONLY code, no explanations."
    )
    
    # Test generation
    print("\nGenerating code...")
    result = await agent.run("Generate a complete HTML landing page with CSS")
    
    response = result.output if hasattr(result, 'output') else str(result.data)
    print(f"\nResponse length: {len(response)} chars")
    print(f"First 500 chars:\n{response[:500]}")
    print(f"\nLast 500 chars:\n{response[-500:]}")
    
    return response

if __name__ == "__main__":
    response = asyncio.run(test_ollama_settings())
    
    with open("test_ollama_output.html", "w") as f:
        f.write(response)
    
    print(f"\n✅ Saved to test_ollama_output.html ({len(response)} chars)")
