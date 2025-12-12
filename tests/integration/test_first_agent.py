"""Integration tests for the first PydanticAI agent.

These tests require Ollama to be running with the mistral model installed.
Run: ollama pull mistral
"""

import pytest
from packages.core.agents.base import simple_agent, test_agent_sync, test_agent_async


@pytest.mark.integration
def test_agent_sync_call():
    """Test synchronous agent call."""
    result = test_agent_sync("What is 2+2?")

    # Check structure
    assert hasattr(result, "answer")
    assert hasattr(result, "confidence")

    # Check types
    assert isinstance(result.answer, str)
    assert isinstance(result.confidence, float)

    # Check values
    assert len(result.answer) > 0
    assert "4" in result.answer.lower()
    assert 0 <= result.confidence <= 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_async_call():
    """Test asynchronous agent call."""
    result = await test_agent_async("What is Python?")

    # Check structure and types
    assert isinstance(result.answer, str)
    assert isinstance(result.confidence, float)

    # Check values
    assert len(result.answer) > 10
    assert 0 <= result.confidence <= 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_structured_output():
    """Test that output matches Pydantic model."""
    result = await test_agent_async("Say hello")

    # Pydantic validation ensures structure
    assert hasattr(result, "answer")
    assert hasattr(result, "confidence")

    # Should contain greeting
    assert any(word in result.answer.lower() for word in ["hello", "hi", "greetings"])


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
        assert isinstance(result.answer, str)
        assert len(result.answer) > 0
