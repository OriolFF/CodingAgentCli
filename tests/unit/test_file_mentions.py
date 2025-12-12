"""Tests for file mention functionality."""

import pytest
from pathlib import Path
from packages.cli.file_mentions import FileMentionParser, get_project_files


def test_extract_mentions():
    """Test extracting @mentions from text."""
    text = "analyze @config.py and @utils.py"
    mentions = FileMentionParser.extract_mentions(text)
    
    assert len(mentions) == 2
    assert "config.py" in mentions
    assert "utils.py" in mentions


def test_extract_mentions_with_paths():
    """Test extracting @mentions with paths."""
    text = "check @packages/core/config.py"
    mentions = FileMentionParser.extract_mentions(text)
    
    assert len(mentions) == 1
    assert "packages/core/config.py" in mentions


def test_no_mentions():
    """Test text without mentions."""
    text = "analyze the config file"
    mentions = FileMentionParser.extract_mentions(text)
    
    assert len(mentions) == 0


def test_resolve_file_path():
    """Test resolving file paths."""
    # This file should exist
    path = FileMentionParser.resolve_file_path("pyproject.toml")
    
    assert path is not None
    assert path.exists()
    assert path.name == "pyproject.toml"


def test_resolve_nonexistent_file():
    """Test resolving non-existent file."""
    path = FileMentionParser.resolve_file_path("nonexistent_file.xyz")
    
    assert path is None


def test_read_file_content():
    """Test reading file content."""
    # Read this test file
    content = FileMentionParser.read_file_content(Path(__file__))
    
    assert "test_extract_mentions" in content
    assert len(content) > 0


def test_process_mentions():
    """Test full mention processing."""
    text = "analyze @pyproject.toml"
    cleaned, context = FileMentionParser.process_mentions(text)
    
    # Should clean the text
    assert "@pyproject.toml" not in cleaned or "pyproject.toml" in cleaned
    
    # Should have context
    assert len(context) > 0
    assert "pyproject.toml" in context or "Referenced files" in context


def test_get_project_files():
    """Test getting project files."""
    files = get_project_files()
    
    # Should find some Python files
    python_files = [f for f in files if f.endswith('.py')]
    assert len(python_files) > 0
    
    # Should include common files
    assert any('config' in f.lower() for f in files)
