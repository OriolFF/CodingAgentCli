"""Tests for file edit and search tools."""

import pytest
import tempfile
from pathlib import Path
from packages.core.tools.file_edit import EditFileTool
from packages.core.tools.search import ListDirectoryTool, GlobSearchTool, GrepSearchTool


# EditFileTool Tests

@pytest.mark.asyncio
async def test_edit_file_simple():
    """Test simple file edit."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Hello World\nThis is a test\nGoodbye World")
        temp_path = f.name
    
    try:
        tool = EditFileTool()
        result = await tool.execute(
            file_path=temp_path,
            search_text="test",
            replace_text="example"
        )
        
        assert result.success is True
        assert "example" in Path(temp_path).read_text()
        assert "test" not in Path(temp_path).read_text()
        assert result.metadata["lines_changed"] > 0
    finally:
        Path(temp_path).unlink()


@pytest.mark.asyncio
async def test_edit_file_line_range():
    """Test editing within specific line range."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Line 1\nLine 2\nLine 3\nLine 4")
        temp_path = f.name
    
    try:
        tool = EditFileTool()
        result = await tool.execute(
            file_path=temp_path,
            search_text="Line 2",
            replace_text="Modified Line 2",
            start_line=2,
            end_line=3
        )
        
        assert result.success is True
        content = Path(temp_path).read_text()
        assert "Modified Line 2" in content
    finally:
        Path(temp_path).unlink()


@pytest.mark.asyncio
async def test_edit_file_not_found():
    """Test editing non-existent file."""
    tool = EditFileTool()
    result = await tool.execute(
        file_path="/nonexistent/file.txt",
        search_text="test",
        replace_text="example"
    )
    
    assert result.success is False
    assert "not found" in result.error.lower()


# ListDirectoryTool Tests

@pytest.mark.asyncio
async def test_list_directory():
    """Test listing directory contents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some test files
        Path(temp_dir, "file1.txt").write_text("test")
        Path(temp_dir, "file2.py").write_text("test")
        Path(temp_dir, "subdir").mkdir()
        
        tool = ListDirectoryTool()
        result = await tool.execute(directory=temp_dir)
        
        assert result.success is True
        assert "file1.txt" in result.output
        assert "file2.py" in result.output
        assert "subdir" in result.output
        assert result.metadata["item_count"] == 3


@pytest.mark.asyncio
async def test_list_directory_hidden_files():
    """Test listing with hidden files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        Path(temp_dir, "visible.txt").write_text("test")
        Path(temp_dir, ".hidden").write_text("test")
        
        tool = ListDirectoryTool()
        
        # Without hidden files
        result = await tool.execute(directory=temp_dir, show_hidden=False)
        assert ".hidden" not in result.output
        
        # With hidden files
        result = await tool.execute(directory=temp_dir, show_hidden=True)
        assert ".hidden" in result.output


# GlobSearchTool Tests

@pytest.mark.asyncio
async def test_glob_search():
    """Test glob pattern search."""
    with tempfile.TemporaryDirectory() as temp_dir:
        Path(temp_dir, "file1.py").write_text("test")
        Path(temp_dir, "file2.py").write_text("test")
        Path(temp_dir, "file3.txt").write_text("test")
        
        tool = GlobSearchTool()
        result = await tool.execute(pattern="*.py", directory=temp_dir, recursive=False)
        
        assert result.success is True
        assert "file1.py" in result.output
        assert "file2.py" in result.output
        assert "file3.txt" not in result.output
        assert result.metadata["match_count"] == 2


@pytest.mark.asyncio
async def test_glob_search_recursive():
    """Test recursive glob search."""
    with tempfile.TemporaryDirectory() as temp_dir:
        subdir = Path(temp_dir, "subdir")
        subdir.mkdir()
        Path(temp_dir, "root.py").write_text("test")
        Path(subdir, "nested.py").write_text("test")
        
        tool = GlobSearchTool()
        result = await tool.execute(pattern="*.py", directory=temp_dir, recursive=True)
        
        assert result.success is True
        assert "root.py" in result.output
        assert "nested.py" in result.output


# GrepSearchTool Tests

@pytest.mark.asyncio
async def test_grep_search():
    """Test content search with grep."""
    with tempfile.TemporaryDirectory() as temp_dir:
        Path(temp_dir, "file1.txt").write_text("Hello World\nTest content\nGoodbye")
        Path(temp_dir, "file2.txt").write_text("Another file\nWith Test\nContent")
        
        tool = GrepSearchTool()
        result = await tool.execute(
            pattern="Test",
            directory=temp_dir,
            file_pattern="*.txt"
        )
        
        assert result.success is True
        assert "Test" in result.output
        assert result.metadata["match_count"] >= 2


@pytest.mark.asyncio
async def test_grep_search_case_insensitive():
    """Test case-insensitive grep search."""
    with tempfile.TemporaryDirectory() as temp_dir:
        Path(temp_dir, "file.txt").write_text("hello WORLD\ntest TEST\n")
        
        tool = GrepSearchTool()
        result = await tool.execute(
            pattern="world",
            directory=temp_dir,
            case_sensitive=False
        )
        
        assert result.success is True
        assert result.metadata["match_count"] >= 1


@pytest.mark.asyncio
async def test_grep_search_regex():
    """Test regex pattern in grep."""
    with tempfile.TemporaryDirectory() as temp_dir:
        Path(temp_dir, "file.txt").write_text("test123\ntest456\nabc789")
        
        tool = GrepSearchTool()
        result = await tool.execute(
            pattern=r"test\d+",
            directory=temp_dir
        )
        
        assert result.success is True
        assert result.metadata["match_count"] == 2
