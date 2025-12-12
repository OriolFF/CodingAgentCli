"""Tests for configuration system."""

import pytest
import os
from packages.core.config.config import Config, AgentConfigSpec


def test_config_defaults():
    """Test default configuration values."""
    config = Config()
    
    assert config.app_name == "pydantic-agent"
    assert config.debug is False
    assert config.log_level == "INFO"
    assert config.default_model == "ollama:mistral"
    assert config.ollama_base_url == "http://localhost:11434/v1"


def test_config_from_env(monkeypatch):
    """Test configuration from environment variables."""
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://custom:8080/v1")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    
    config = Config()
    
    assert config.ollama_base_url == "http://custom:8080/v1"
    assert config.debug is True
    assert config.log_level == "DEBUG"


def test_config_sets_environment():
    """Test that config sets environment variables."""
    # Clear any existing value
    if "OLLAMA_BASE_URL" in os.environ:
        del os.environ["OLLAMA_BASE_URL"]
    
    config = Config()
    
    # Should be set after init
    assert "OLLAMA_BASE_URL" in os.environ
    assert os.environ["OLLAMA_BASE_URL"] == config.ollama_base_url


def test_default_agent_created():
    """Test that default agent config is created."""
    config = Config()
    
    assert "default" in config.agents
    assert config.agents["default"].model == "ollama:mistral"


def test_get_agent_config():
    """Test getting agent configuration."""  
    config = Config()
    
    agent_config = config.get_agent_config("default")
    assert agent_config is not None
    assert agent_config.model == "ollama:mistral"
    
    # Non-existent agent
    assert config.get_agent_config("nonexistent") is None


def test_agent_config_spec():
    """Test AgentConfigSpec model."""
    spec = AgentConfigSpec(
        model="ollama:llama2",
        temperature=0.5,
        max_tokens=2048,
        system_prompt="Test prompt"
    )
    
    assert spec.model == "ollama:llama2"
    assert spec.temperature == 0.5
    assert spec.max_tokens == 2048
    assert spec.system_prompt == "Test prompt"
    assert spec.retries == 2  # default
