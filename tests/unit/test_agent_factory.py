"""Tests for AgentFactory."""

import pytest
from packages.core.agents.factory import AgentFactory
from packages.core.config import Config, AgentConfigSpec


def test_factory_initialization():
    """Test factory can be initialized."""
    factory = AgentFactory()
    assert factory.config is not None


def test_create_default_agent():
    """Test creating default agent."""
    factory = AgentFactory()
    agent = factory.create_agent("default")
    
    assert agent is not None
    assert hasattr(agent, 'run')
    assert hasattr(agent, 'run_sync')


def test_create_agent_not_found():
    """Test error when agent config not found."""
    factory = AgentFactory()
    
    with pytest.raises(ValueError, match="not found"):
        factory.create_agent("nonexistent_agent")


def test_list_agents():
    """Test listing available agents."""
    factory = AgentFactory()
    agents = factory.list_agents()
    
    assert isinstance(agents, list)
    assert "default" in agents


def test_factory_with_custom_config():
    """Test factory with custom configuration."""
    config = Config()
    factory = AgentFactory(config=config)
    
    assert factory.config is config
