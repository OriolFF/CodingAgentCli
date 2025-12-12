"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def sample_config():
    """Sample configuration for testing."""
    return {
        "models": {
            "local": {
                "mistral-7b": {
                    "provider": "ollama",
                    "model_name": "mistral",
                    "context_window": 8192,
                }
            }
        }
    }
