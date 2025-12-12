"""File editing tool with diff-based modifications."""

from pathlib import Path
from typing import Optional
import difflib
import aiofiles
from .base import BaseTool, ToolResult, ToolError


class EditFileTool(BaseTool):
    """Tool for editing files with diff-based changes.
    
    This tool allows precise modifications to files using search-and-replace
    or diff-based edits.
    """
    
    def __init__(self):
        """Initialize the edit file tool."""
        super().__init__(name="edit_file")
    
    async def execute(
        self,
        file_path: str,
        search_text: str,
        replace_text: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
    ) -> ToolResult:
        """Edit file by replacing search text with replace text.
        
        Args:
            file_path: Path to the file to edit
            search_text: Text to search for (exact match)
            replace_text: Text to replace with
            start_line: Optional starting line to search from (1-indexed)
            end_line: Optional ending line to search to (1-indexed, inclusive)
            
        Returns:
            ToolResult with edit results
            
        Raises:
            ToolError: If file cannot be edited
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"File not found: {file_path}"
                )
            
            # Read file
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            original_content = content
            
            # If line range specified, only edit within that range
            if start_line is not None or end_line is not None:
                lines = content.split('\n')
                start_idx = (start_line - 1) if start_line else 0
                end_idx = end_line if end_line else len(lines)
                
                # Edit only the specified range
                range_content = '\n'.join(lines[start_idx:end_idx])
                if search_text not in range_content:
                    return ToolResult(
                        success=False,
                        output="",
                        error=f"Search text not found in lines {start_line}-{end_line}"
                    )
                
                edited_range = range_content.replace(search_text, replace_text, 1)
                lines[start_idx:end_idx] = edited_range.split('\n')
                content = '\n'.join(lines)
            else:
                # Edit entire file
                if search_text not in content:
                    return ToolResult(
                        success=False,
                        output="",
                        error="Search text not found in file"
                    )
                
                content = content.replace(search_text, replace_text, 1)
            
            # Generate diff
            diff = list(difflib.unified_diff(
                original_content.splitlines(keepends=True),
                content.splitlines(keepends=True),
                fromfile=f"{file_path} (original)",
                tofile=f"{file_path} (modified)",
                lineterm=''
            ))
            
            # Write modified content
            async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            self.logger.info(f"Edited {file_path}")
            
            return ToolResult(
                success=True,
                output=''.join(diff),
                metadata={
                    "file_path": str(path.absolute()),
                    "lines_changed": len([line for line in diff if line.startswith(('+', '-'))]),
                    "search_text_length": len(search_text),
                    "replace_text_length": len(replace_text),
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to edit file {file_path}: {e}")
            raise ToolError(self.name, str(e))
