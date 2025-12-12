"""Tests for shell, web, and memory tools."""

import pytest
import tempfile
import os
from pathlib import Path
from packages.core.tools.shell import ShellExecutionTool
from packages.core.tools.web import FetchUrlTool
from packages.core.tools.memory import MemoryTool


# ShellExecutionTool Tests

@pytest.mark.asyncio
async def test_shell_execute_simple_command():
    """Test executing a simple safe command."""
    tool = ShellExecutionTool()
    result = await tool.execute(command="echo 'Hello World'")
    
    assert result.success is True
    assert "Hello World" in result.output
    assert result.metadata["exit_code"] == 0


@pytest.mark.asyncio
async def test_shell_dangerous_command_blocked():
    """Test that dangerous commands are blocked."""
    tool = ShellExecutionTool(allow_dangerous=False)
    result = await tool.execute(command="rm -rf /tmp/test")
    
    assert result.success is False
    assert "dangerous" in result.error.lower()


@pytest.mark.asyncio
async def test_shell_command_timeout():
    """Test command timeout."""
    tool = ShellExecutionTool()
    result = await tool.execute(command="sleep 10", timeout=1)
    
    assert result.success is False
    assert "timed out" in result.error.lower()


@pytest.mark.asyncio
async def test_shell_working_directory():
    """Test command execution in specific directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        tool = ShellExecutionTool()
        result = await tool.execute(command="pwd", working_dir=temp_dir)
        
        assert result.success is True
        assert temp_dir in result.output


# FetchUrlTool Tests

@pytest.mark.asyncio
async def test_fetch_url_success():
    """Test fetching a URL successfully."""
    tool = FetchUrlTool()
    # Using example.com which is a reliable test domain
    result = await tool.execute(url="http://example.com")
    
    assert result.success is True
    assert len(result.output) > 0
    assert result.metadata["status_code"] == 200


@pytest.mark.asyncio
async def test_fetch_url_not_found():
    """Test handling 404 errors."""
    tool = FetchUrlTool()
    result = await tool.execute(url="http://example.com/nonexistent-page-xyz")
    
    assert result.success is False
    assert result.metadata["status_code"] == 404


@pytest.mark.asyncio
async def test_fetch_url_timeout():
    """Test URL fetch timeout."""
    tool = FetchUrlTool(timeout=1)
    # Using a slow endpoint
    result = await tool.execute(
        url="http://httpbin.org/delay/10",
        timeout=1
    )
    
    assert result.success is False
    assert "timed out" in result.error.lower()


# MemoryTool Tests

@pytest.mark.asyncio
async def test_memory_store_and_retrieve():
    """Test storing and retrieving a memory."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        tool = MemoryTool(db_path=db_path)
        
        # Store
        result = await tool.execute(
            operation="store",
            key="test_key",
            value={"data": "test value"}
        )
        assert result.success is True
        
        # Retrieve
        result = await tool.execute(
            operation="retrieve",
            key="test_key"
        )
        assert result.success is True
        assert "test value" in result.output
        assert result.metadata["value"]["data"] == "test value"
    finally:
        Path(db_path).unlink()


@pytest.mark.asyncio
async def test_memory_list():
    """Test listing memories."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        tool = MemoryTool(db_path=db_path)
        
        # Store multiple
        await tool.execute(operation="store", key="key1", value="value1")
        await tool.execute(operation="store", key="key2", value="value2")
        
        # List
        result = await tool.execute(operation="list")
        assert result.success is True
        assert "key1" in result.output
        assert "key2" in result.output
        assert result.metadata["count"] == 2
    finally:
        Path(db_path).unlink()


@pytest.mark.asyncio
async def test_memory_delete():
    """Test deleting a memory."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        tool = MemoryTool(db_path=db_path)
        
        # Store
        await tool.execute(operation="store", key="to_delete", value="data")
        
        # Delete
        result = await tool.execute(operation="delete", key="to_delete")
        assert result.success is True
        
        # Verify deleted
        result = await tool.execute(operation="retrieve", key="to_delete")
        assert result.success is False
    finally:
        Path(db_path).unlink()


@pytest.mark.asyncio
async def test_memory_update():
    """Test updating an existing memory."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        tool = MemoryTool(db_path=db_path)
        
        # Store initial
        await tool.execute(operation="store", key="update_key", value="old")
        
        # Update
        await tool.execute(operation="store", key="update_key", value="new")
        
        # Retrieve
        result = await tool.execute(operation="retrieve", key="update_key")
        assert result.success is True
        assert result.metadata["value"] == "new"
    finally:
        Path(db_path).unlink()


@pytest.mark.asyncio
async def test_memory_retrieve_nonexistent():
    """Test retrieving non-existent memory."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        tool = MemoryTool(db_path=db_path)
        result = await tool.execute(operation="retrieve", key="does_not_exist")
        
        assert result.success is False
        assert "not found" in result.error.lower()
    finally:
        Path(db_path).unlink()
