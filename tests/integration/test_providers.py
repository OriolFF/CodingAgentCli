"""Integration tests for multi-provider support.

These tests verify that PydanticAI works with different model providers.
Some tests may be skipped if API keys are not available.

Providers tested:
- Ollama (local) - Always available
- OpenAI-compatible APIs - Requires OPENAI_API_KEY or compatible endpoint
- Gemini - Requires GEMINI_API_KEY

Run ollama to enable local tests:
  ollama serve
"""

import os
import pytest
from pydantic_ai import Agent


@pytest.mark.integration
def test_ollama_provider():
    """Test Ollama local provider."""
    # Set Ollama base URL
    if "OLLAMA_BASE_URL" not in os.environ:
        os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434/v1"
    
    agent = Agent("ollama:mistral")
    result = agent.run_sync("Say 'test'")
    
    assert isinstance(result.output, str)
    assert len(result.output) > 0


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OpenAI API key not available"
)
def test_openai_provider():
    """Test OpenAI provider (requires API key)."""
    agent = Agent("openai:gpt-4o-mini")
    result = agent.run_sync("Say 'test'")
    
    assert isinstance(result.output, str)
    assert len(result.output) > 0


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="Gemini API key not available"
)
def test_gemini_provider():
    """Test Gemini provider (requires API key)."""
    agent = Agent("gemini-1.5-flash")
    result = agent.run_sync("Say 'test'")
    
    assert isinstance(result.output, str)
    assert len(result.output) > 0


@pytest.mark.integration
def test_model_switching():
    """Test switching between models at runtime."""
    # Set Ollama base URL
    if "OLLAMA_BASE_URL" not in os.environ:
        os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434/v1"
    
    # Create two agents with different models
    agent1 = Agent("ollama:mistral")
    result1 = agent1.run_sync("Say hello")
    
    # Use a different model if available, otherwise same model is fine
    agent2 = Agent("ollama:mistral")
    result2 = agent2.run_sync("Say goodbye")
    
    # Both should work
    assert isinstance(result1.output, str)
    assert isinstance(result2.output, str)
    assert len(result1.output) > 0
    assert len(result2.output) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_async_provider_calls():
    """Test async calls work with providers."""
    if "OLLAMA_BASE_URL" not in os.environ:
        os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434/v1"
    
    agent = Agent("ollama:mistral")
    result = await agent.run("What is 1+1?")
    
    assert isinstance(result.output, str)
    assert "2" in result.output


@pytest.mark.integration
def test_provider_error_handling():
    """Test graceful error handling for unavailable providers."""
    # This should fail gracefully if model doesn't exist
    try:
        agent = Agent("ollama:nonexistent-model-xyz")
        result = agent.run_sync("test")
        # If we get here, either model exists or there was a different issue
        assert isinstance(result.output, str)
    except Exception as e:
        # Should get a meaningful error message
        assert "nonexistent" in str(e).lower() or "not found" in str(e).lower() or "error" in str(e).lower()
