"""File operation tools for reading and writing files."""

from pathlib import Path
from typing import Optional
import aiofiles
from .base import BaseTool, ToolResult, ToolError


class ReadFileTool(BaseTool):
    """Tool for reading file contents.
    
    This tool reads text files and returns their contents.
    Supports reading specific line ranges.
    """
    
    def __init__(self):
        """Initialize the read file tool."""
        super().__init__(name="read_file")
    
    async def execute(
        self,
        file_path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
    ) -> ToolResult:
        """Read file contents.
        
        Args:
            file_path: Path to the file to read
            start_line: Optional starting line (1-indexed)
            end_line: Optional ending line (1-indexed, inclusive)
            
        Returns:
            ToolResult with file contents
            
        Raises:
            ToolError: If file cannot be read
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"File not found: {file_path}"
                )
            
            if not path.is_file():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Not a file: {file_path}"
                )
            
            # Read file
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                if start_line is None and end_line is None:
                    # Read entire file
                    content = await f.read()
                else:
                    # Read specific lines
                    lines = await f.readlines()
                    start_idx = (start_line - 1) if start_line else 0
                    end_idx = end_line if end_line else len(lines)
                    content = ''.join(lines[start_idx:end_idx])
            
            self.logger.debug(f"Read {len(content)} characters from {file_path}")
            
            return ToolResult(
                success=True,
                output=content,
                metadata={
                    "file_path": str(path.absolute()),
                    "size": len(content),
                    "start_line": start_line,
                    "end_line": end_line,
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to read file {file_path}: {e}")
            raise ToolError(self.name, str(e))


class WriteFileTool(BaseTool):
    """Tool for writing content to files.
    
    This tool creates or overwrites files with given content.
    """
    
    def __init__(self):
        """Initialize the write file tool."""
        super().__init__(name="write_file")
    
    async def execute(
        self,
        file_path: str,
        content: str,
        create_dirs: bool = True,
    ) -> ToolResult:
        """Write content to a file.
        
        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            create_dirs: Whether to create parent directories if they don't exist
            
        Returns:
            ToolResult with write operation results
            
        Raises:
            ToolError: If file cannot be written
        """
        try:
            path = Path(file_path)
            
            # Create parent directories if needed
            if create_dirs and not path.parent.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                self.logger.debug(f"Created directories for {file_path}")
            
            # Write file
            async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            self.logger.info(f"Wrote {len(content)} characters to {file_path}")
            
            return ToolResult(
                success=True,
                output=f"Successfully wrote {len(content)} characters",
                metadata={
                    "file_path": str(path.absolute()),
                    "size": len(content),
                    "created_dirs": create_dirs and not path.parent.exists(),
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to write file {file_path}: {e}")
            raise ToolError(self.name, str(e))
