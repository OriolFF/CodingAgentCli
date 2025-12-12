"""Tests for configuration loading."""

import pytest
from pathlib import Path
from packages.core.config import Config, AgentConfig, load_config_from_yaml


def test_agent_config_defaults():
    """Test AgentConfig with default values."""
    config = AgentConfig(model="ollama:test")
    assert config.model == "ollama:test"
    assert config.temperature == 0.7
    assert config.max_tokens == 4096
    assert config.fallback_models == []


def test_agent_config_validation():
    """Test AgentConfig input validation."""
    # Temperature must be between 0 and 2
    with pytest.raises(ValueError):
        AgentConfig(model="test", temperature=3.0)

    # Max tokens must be positive
    with pytest.raises(ValueError):
        AgentConfig(model="test", max_tokens=-1)


def test_config_defaults():
    """Test Config with default values."""
    config = Config()
    assert config.debug is False
    assert config.log_level == "INFO"
    assert config.default_model == "ollama:mistral"
    # Should auto-create default agent
    assert "default" in config.agents


def test_load_config_from_yaml():
    """Test loading configuration from YAML file."""
    config = load_config_from_yaml("config/agents.yaml")

    # Check global settings
    assert config.debug is False
    assert config.log_level == "INFO"
    assert config.default_model == "ollama:mistral"

    # Check agents loaded
    assert "default" in config.agents
    assert "codebase_investigator" in config.agents
    assert "file_editor" in config.agents

    # Check default agent config
    default_agent = config.get_agent_config("default")
    assert default_agent is not None
    assert default_agent.model == "ollama:mistral"
    assert default_agent.temperature == 0.7
    assert len(default_agent.fallback_models) > 0

    # Check codebase_investigator agent
    investigator = config.get_agent_config("codebase_investigator")
    assert investigator is not None
    assert investigator.model == "ollama:llama2:13b"
    assert investigator.temperature == 0.3  # Lower for analysis
    assert investigator.max_tokens == 8192  # Larger context

    # Check file_editor agent
    editor = config.get_agent_config("file_editor")
    assert editor is not None
    assert editor.temperature == 0.1  # Very low for precision


def test_config_file_not_found():
    """Test error when config file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        load_config_from_yaml("nonexistent.yaml")


def test_environment_variable_override(monkeypatch):
    """Test that environment variables override config."""
    monkeypatch.setenv("GEMINI_AGENT_DEBUG", "true")
    monkeypatch.setenv("GEMINI_AGENT_DEFAULT_MODEL", "ollama:test")

    config = Config()
    assert config.debug is True
    assert config.default_model == "ollama:test"
