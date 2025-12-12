"""Tests for agent registry."""

import pytest
import os
from pydantic_ai import Agent
from pydantic_ai.providers.ollama import OllamaProvider
from packages.core.agents.registry import AgentRegistry, get_agent_registry
from packages.core.utils.errors import AgentError


@pytest.fixture(autouse=True)
def set_ollama_url():
    """Set OLLAMA_BASE_URL for tests."""
    os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434/v1"
    yield
    # Optionally clean up
    if "OLLAMA_BASE_URL" in os.environ:
        del os.environ["OLLAMA_BASE_URL"]


def test_register_agent():
    """Test registering an agent."""
    registry = AgentRegistry()
    agent = Agent("ollama:mistral")
    
    registry.register("test_agent", agent)
    
    assert registry.has_agent("test_agent")
    assert "test_agent" in registry.list_agents()


def test_register_duplicate_agent():
    """Test registering duplicate agent name raises error."""
    registry = AgentRegistry()
    agent1 = Agent("ollama:mistral")
    agent2 = Agent("ollama:llama2")
    
    registry.register("test_agent", agent1)
    
    with pytest.raises(AgentError, match="already registered"):
        registry.register("test_agent", agent2)


def test_get_agent():
    """Test retrieving an agent."""
    registry = AgentRegistry()
    agent = Agent("ollama:mistral")
    
    registry.register("test_agent", agent)
    retrieved = registry.get("test_agent")
    
    assert retrieved is agent


def test_get_nonexistent_agent():
    """Test getting non-existent agent raises error."""
    registry = AgentRegistry()
    
    with pytest.raises(AgentError, match="not found"):
        registry.get("nonexistent")


def test_list_agents():
    """Test listing all agents."""
    registry = AgentRegistry()
    agent1 = Agent("ollama:mistral")
    agent2 = Agent("ollama:llama2")
    
    registry.register("agent1", agent1)
    registry.register("agent2", agent2)
    
    agents = registry.list_agents()
    assert len(agents) == 2
    assert "agent1" in agents
    assert "agent2" in agents


def test_unregister_agent():
    """Test unregistering an agent."""
    registry = AgentRegistry()
    agent = Agent("ollama:mistral")
    
    registry.register("test_agent", agent)
    registry.unregister("test_agent")
    
    assert not registry.has_agent("test_agent")
    assert len(registry.list_agents()) == 0


def test_unregister_nonexistent_agent():
    """Test unregistering non-existent agent raises error."""
    registry = AgentRegistry()
    
    with pytest.raises(AgentError, match="not found"):
        registry.unregister("nonexistent")


def test_clear_registry():
    """Test clearing all agents."""
    registry = AgentRegistry()
    agent1 = Agent("ollama:mistral")
    agent2 = Agent("ollama:llama2")
    
    registry.register("agent1", agent1)
    registry.register("agent2", agent2)
    
   registry.clear()
    
    assert len(registry.list_agents()) == 0


def test_has_agent():
    """Test checking agent existence."""
    registry = AgentRegistry()
    agent = Agent("ollama:mistral")
    
    assert not registry.has_agent("test_agent")
    
    registry.register("test_agent", agent)
    assert registry.has_agent("test_agent")


def test_global_registry_singleton():
    """Test global registry is a singleton."""
    registry1 = get_agent_registry()
    registry2 = get_agent_registry()
    
    assert registry1 is registry2
