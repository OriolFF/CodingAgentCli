"""Tests for agent delegation system."""

import pytest
from packages.core.agents.delegation import (
    get_coordinator_agent,
    delegate_task,
    DelegationResult
)


@pytest.fixture(autouse=True)
def set_ollama_url():
    """Set OLLAMA_BASE_URL for tests."""
    import os
    os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434/v1"
    yield


def test_coordinator_agent_creation():
    """Test creating coordinator agent."""
    coordinator = get_coordinator_agent()
    
    assert coordinator is not None
    assert hasattr(coordinator, 'run')
    assert hasattr(coordinator, 'run_sync')


def test_coordinator_singleton():
    """Test coordinator is a singleton."""
    coordinator1 = get_coordinator_agent()
    coordinator2 = get_coordinator_agent()
    
    assert coordinator1 is coordinator2


@pytest.mark.asyncio
async def test_delegate_task_analysis():
    """Test delegating a code analysis task."""
    # This would normally call the LLM, but we're just testing structure
    # In a real scenario, we'd mock the LLM calls
    
    result = await delegate_task("Explain what a coordinator agent does")
    
    assert isinstance(result, DelegationResult)
    assert result.success is not None
    assert isinstance(result.result, str)
    assert isinstance(result.agents_used, list)
    assert isinstance(result.task_summary, str)


@pytest.mark.asyncio  
async def test_delegate_task_with_context():
    """Test delegating with additional context."""
    result = await delegate_task(
        request="Analyze the file structure",
        context="Focus on the agents package"
    )
    
    assert isinstance(result, DelegationResult)


def test_delegation_result_model():
    """Test DelegationResult Pydantic model."""
    result = DelegationResult(
        success=True,
        result="Task completed successfully",
        agents_used=["codebase_investigator"],
        task_summary="Analyzed code structure"
    )
    
    assert result.success is True
    assert "successfully" in result.result
    assert len(result.agents_used) == 1
    assert result.agents_used[0] == "codebase_investigator"
