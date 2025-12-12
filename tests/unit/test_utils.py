"""Tests for logging and error handling."""

import pytest
import logging
from packages.core.utils import (
    get_logger,
    configure_logging,
    AgentError,
    ModelNotAvailableError,
    ToolExecutionError,
    ConfigurationError,
)
from packages.core.utils.logger import get_model_logger


def test_get_logger():
    """Test getting a logger instance."""
    logger = get_logger("test")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test"


def test_configure_logging():
    """Test configuring logging."""
    configure_logging(level="DEBUG")
    logger = get_logger("test.configure")
    
    # Should be able to log at DEBUG level
    logger.debug("Test debug message")
    assert logger.level == logging.NOTSET  # Root logger handles level


def test_model_logger():
    """Test model-aware logger."""
    logger = get_model_logger("test", "mistral", "ollama")
    
    # Should have context
    assert logger.model_name == "mistral"
    assert logger.provider == "ollama"
    assert logger.prefix == "[ollama:mistral]"


def test_agent_error():
    """Test base AgentError."""
    error = AgentError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_model_not_available_error():
    """Test ModelNotAvailableError."""
    error = ModelNotAvailableError("gpt-4", "openai")
    
    assert error.model_name == "gpt-4"
    assert error.provider == "openai"
    assert "gpt-4" in str(error)
    assert "openai" in str(error)
    assert isinstance(error, AgentError)


def test_tool_execution_error():
    """Test ToolExecutionError."""
    error = ToolExecutionError("read_file")
    
    assert error.tool_name == "read_file"
    assert "read_file" in str(error)
    assert isinstance(error, AgentError)


def test_configuration_error():
    """Test ConfigurationError."""
    error = ConfigurationError("Invalid config")
    assert str(error) == "Invalid config"
    assert isinstance(error, AgentError)


def test_error_hierarchy():
    """Test exception hierarchy."""
    # All custom errors should be AgentErrors
    assert issubclass(ModelNotAvailableError, AgentError)
    assert issubclass(ToolExecutionError, AgentError)
    assert issubclass(ConfigurationError, AgentError)
