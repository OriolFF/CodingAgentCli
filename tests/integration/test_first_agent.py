"""Integration tests for the first PydanticAI agent.

These tests require Ollama to be running with the mistral model installed.
Run: ollama pull mistral

NOTE: Currently using text-only output mode due to Ollama compatibility issues
with structured JSON output through the OpenAI-compatible API.
"""

import pytest
from packages.core.agents.base import simple_agent, test_agent_sync, test_agent_async


@pytest.mark.integration
def test_agent_sync_call():
    """Test synchronous agent call."""
    result = test_agent_sync("What is 2+2?")

    # Check type (should be string in text mode)
    assert isinstance(result, str)
   
    # Check values
    assert len(result) > 0
    assert "4" in result.lower()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_async_call():
    """Test asynchronous agent call."""
    result = await test_agent_async("What is Python?")

    # Check type
    assert isinstance(result, str)

    # Check values
    assert len(result) > 10


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_text_output():
    """Test that text output works."""
    result = await test_agent_async("Say hello")

    # Should contain greeting
    assert any(word in result.lower() for word in ["hello", "hi", "greetings"])


@pytest.mark.integration
def test_agent_model_attribute():
    """Test that agent has correct model configured."""
    # Agent is configured with ollama mistral model
    # Check that the agent has a model
    assert simple_agent.model is not None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_multiple_calls():
    """Test that agent can handle multiple calls."""
    questions = [
        "What is 1+1?",
        "What is the capital of France?",
        "What color is the sky?",
    ]

    for question in questions:
        result = await test_agent_async(question)
        assert isinstance(result, str)
        assert len(result) > 0
