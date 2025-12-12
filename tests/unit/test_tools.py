"""Tests for tool base classes and file operations."""

import pytest
import tempfile
from pathlib import Path
from packages.core.tools.base import BaseTool, ToolResult, ToolError
from packages.core.tools.file_operations import ReadFileTool, WriteFileTool


class DummyTool(BaseTool):
    """Dummy tool for testing base class."""
    
    async def execute(self, value: int) -> ToolResult:
        """Execute dummy tool."""
        return ToolResult(
            success=True,
            output=value * 2,
            metadata={"operation": "double"}
        )


def test_tool_result_creation():
    """Test creating a ToolResult."""
    result = ToolResult(success=True, output="test")
    assert result.success is True
    assert result.output == "test"
    assert result.error is None
    assert result.metadata == {}


def test_tool_result_with_error():
    """Test ToolResult with error."""
    result = ToolResult(
        success=False,
        output=None,
        error="Something went wrong"
    )
    assert result.success is False
    assert result.error == "Something went wrong"


def test_tool_error():
    """Test ToolError exception."""
    error = ToolError("my_tool", "Failed to execute")
    assert error.tool_name == "my_tool"
    assert "my_tool" in str(error)
    assert "Failed to execute" in str(error)


def test_base_tool_initialization():
    """Test BaseTool initialization."""
    tool = DummyTool()
    assert tool.name == "DummyTool"
    assert tool.logger is not None


def test_base_tool_custom_name():
    """Test BaseTool with custom name."""
    tool = DummyTool(name="CustomTool")
    assert tool.name == "CustomTool"


@pytest.mark.asyncio
async def test_dummy_tool_execute():
    """Test executing dummy tool."""
    tool = DummyTool()
    result = await tool.execute(value=5)
    
    assert result.success is True
    assert result.output == 10
    assert result.metadata["operation"] == "double"


def test_tool_execute_sync():
    """Test synchronous tool execution."""
    tool = DummyTool()
    result = tool.execute_sync(value=3)
    
    assert result.success is True
    assert result.output == 6


@pytest.mark.asyncio
async def test_read_file_tool():
    """Test reading a file."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Line 1\nLine 2\nLine 3\n")
        temp_path = f.name
    
    try:
        tool = ReadFileTool()
        result = await tool.execute(file_path=temp_path)
        
        assert result.success is True
        assert "Line 1" in result.output
        assert "Line 2" in result.output
        assert result.metadata["size"] > 0
    finally:
        Path(temp_path).unlink()


@pytest.mark.asyncio
async def test_read_file_line_range():
    """Test reading specific line range."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Line 1\nLine 2\nLine 3\nLine 4\n")
        temp_path = f.name
    
    try:
        tool = ReadFileTool()
        result = await tool.execute(file_path=temp_path, start_line=2, end_line=3)
        
        assert result.success is True
        assert "Line 2" in result.output
        assert "Line 3" in result.output
        assert "Line 1" not in result.output
        assert "Line 4" not in result.output
    finally:
        Path(temp_path).unlink()


@pytest.mark.asyncio
async def test_read_nonexistent_file():
    """Test reading a file that doesn't exist."""
    tool = ReadFileTool()
    result = await tool.execute(file_path="/nonexistent/file.txt")
    
    assert result.success is False
    assert "not found" in result.error.lower()


@pytest.mark.asyncio
async def test_write_file_tool():
    """Test writing to a file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "test.txt"
        
        tool = WriteFileTool()
        result = await tool.execute(
            file_path=str(file_path),
            content="Hello, World!"
        )
        
        assert result.success is True
        assert file_path.exists()
        assert file_path.read_text() == "Hello, World!"


@pytest.mark.asyncio
async def test_write_file_creates_dirs():
    """Test that write creates parent directories."""
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "subdir" / "nested" / "test.txt"
        
        tool = WriteFileTool()
        result = await tool.execute(
            file_path=str(file_path),
            content="Nested content",
            create_dirs=True
        )
        
        assert result.success is True
        assert file_path.exists()
        assert file_path.read_text() == "Nested content"
