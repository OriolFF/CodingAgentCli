"""Integration tests for the first PydanticAI agent.

These tests require Ollama to be running with the mistral model installed.
Run: ollama pull mistral

NOTE: Currently using text-only output mode due to Ollama compatibility issues
with structured JSON output through the OpenAI-compatible API.
"""

import pytest
import os
from packages.core.agents.factory import AgentFactory


@pytest.fixture(autouse=True)
def set_ollama_url():
    """Set OLLAMA_BASE_URL for tests."""
    os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434/v1"
    yield


@pytest.mark.integration
def test_agent_creation():
    """Test creating an agent via factory."""
    factory = AgentFactory()
    agent = factory.create_agent("default")
    
    # Verify agent was created
    assert agent is not None
    assert hasattr(agent, 'run')
    assert hasattr(agent, 'run_sync')


@pytest.mark.integration  
def test_agent_sync_call():
    """Test synchronous agent call."""
    factory = AgentFactory()
    agent = factory.create_agent("default")
    
    # Make a simple sync call
    result = agent.run_sync("Say hello in one word")
    
    # Verify we got a response
    assert result is not None
    assert hasattr(result, 'data')


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_async_call():
    """Test asynchronous agent call."""
    factory = AgentFactory()
    agent = factory.create_agent("default")
    
    # Make a simple async call
    result = await agent.run("Say hello in one word")
    
    # Verify we got a response
    assert result is not None
    assert hasattr(result, 'data') for word in ["hello", "hi", "greetings"])


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
