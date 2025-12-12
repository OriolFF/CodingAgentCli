"""Integration tests for PydanticAI agents.

These tests require Ollama to be running with the mistral model installed.
Run: ollama pull mistral
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
    
    # Verify we got a response (AgentRunResult has 'output', not 'data' for text mode)
    assert result is not None
    assert hasattr(result, 'output')
    assert isinstance(result.output, str)
    assert len(result.output) > 0


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
    assert hasattr(result, 'output')
    assert isinstance(result.output, str)
    assert len(result.output) > 0
