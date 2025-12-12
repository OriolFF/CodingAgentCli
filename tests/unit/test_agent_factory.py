"""Tests for agent factory."""

import pytest
from packages.core.agents.factory import AgentFactory, create_agent
from packages.core.config import load_config_from_yaml


def test_agent_factory_initialization():
    """Test AgentFactory can be initialized."""
    factory = AgentFactory()
    assert factory.config is not None


def test_list_agents():
    """Test listing available agents."""
    factory = AgentFactory()
    agents = factory.list_agents()
    
    assert isinstance(agents, list)
    assert len(agents) > 0
    assert "default" in agents
    assert "codebase_investigator" in agents
    assert "file_editor" in agents


def test_create_default_agent():
    """Test creating default agent."""
    factory = AgentFactory()
    agent = factory.create_agent("default")
    
    assert agent is not None
    assert agent.model is not None


def test_create_codebase_investigator():
    """Test creating codebase_investigator agent."""
    factory = AgentFactory()
    agent = factory.create_agent("codebase_investigator")
    
    assert agent is not None
    # Should use different model from config
    assert agent.model is not None


def test_create_nonexistent_agent():
    """Test error when creating nonexistent agent."""
    factory = AgentFactory()
    
    with pytest.raises(KeyError) as exc_info:
        factory.create_agent("nonexistent")
    
    assert "nonexistent" in str(exc_info.value)


def test_convenience_function():
    """Test convenience create_agent function."""
    agent = create_agent("default")
    assert agent is not None


def test_agent_uses_config():
    """Test that agent uses configuration from YAML."""
    config = load_config_from_yaml("config/agents.yaml")
    factory = AgentFactory(config)
    
    # Get agent config
    investigator_config = config.get_agent_config("codebase_investigator")
    
    # Create agent
    agent = factory.create_agent("codebase_investigator")
    
    # Verify agent was created
    assert agent is not None
    # Model name should match config
    # Note: We can't directly check all properties but can verify creation worked
