"""Sample test to verify pytest is working."""

import pytest


def test_example():
    """Simple test to verify pytest works."""
    assert 1 + 1 == 2


def test_sample_config(sample_config):
    """Test sample config fixture."""
    assert "models" in sample_config
    assert "local" in sample_config["models"]


@pytest.mark.asyncio
async def test_async_example():
    """Test async functionality."""
    assert True
