"""Search and discovery tools for files and content."""

from pathlib import Path
from typing import Optional, List
import os
import fnmatch
import re
from .base import BaseTool, ToolResult, ToolError


class ListDirectoryTool(BaseTool):
    """Tool for listing directory contents."""
    
    def __init__(self):
        """Initialize the list directory tool."""
        super().__init__(name="list_directory")
    
    async def execute(
        self,
        directory: str = ".",
        show_hidden: bool = False,
        max_depth: int = 1,
    ) -> ToolResult:
        """List directory contents.
        
        Args:
            directory: Directory path to list
            show_hidden: Whether to show hidden files (starting with .)
            max_depth: Maximum depth to recurse (1 = current dir only)
            
        Returns:
            ToolResult with directory listing
            
        Raises:
            ToolError: If directory cannot be listed
        """
        try:
            path = Path(directory)
            
            if not path.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Directory not found: {directory}"
                )
            
            if not path.is_dir():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Not a directory: {directory}"
                )
            
            items = []
            
            def scan_dir(dir_path: Path, current_depth: int):
                """Recursively scan directory."""
                if current_depth > max_depth:
                    return
                
                try:
                    for item in sorted(dir_path.iterdir()):
                        # Skip hidden files if requested
                        if not show_hidden and item.name.startswith('.'):
                            continue
                        
                        # Calculate relative path
                        rel_path = item.relative_to(path)
                        
                        if item.is_dir():
                            items.append({
                                "path": str(rel_path),
                                "type": "directory",
                                "size": None,
                            })
                            if current_depth < max_depth:
                                scan_dir(item, current_depth + 1)
                        else:
                            items.append({
                                "path": str(rel_path),
                                "type": "file",
                                "size": item.stat().st_size,
                            })
                except PermissionError:
                    self.logger.warning(f"Permission denied: {dir_path}")
            
            scan_dir(path, 1)
            
            # Format output
            output_lines = []
            for item in items:
                if item["type"] == "directory":
                    output_lines.append(f"📁 {item['path']}/")
                else:
                    size_kb = item['size'] / 1024 if item['size'] else 0
                    output_lines.append(f"📄 {item['path']} ({size_kb:.1f} KB)")
            
            output = '\n'.join(output_lines)
            
            self.logger.debug(f"Listed {len(items)} items in {directory}")
            
            return ToolResult(
                success=True,
                output=output,
                metadata={
                    "directory": str(path.absolute()),
                    "item_count": len(items),
                    "items": items,
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to list directory {directory}: {e}")
            raise ToolError(self.name, str(e))


class GlobSearchTool(BaseTool):
    """Tool for finding files using glob patterns."""
    
    def __init__(self):
        """Initialize the glob search tool."""
        super().__init__(name="glob_search")
    
    async def execute(
        self,
        pattern: str,
        directory: str = ".",
        recursive: bool = True,
        max_results: int = 100,
    ) -> ToolResult:
        """Search for files matching glob pattern.
        
        Args:
            pattern: Glob pattern (e.g., "*.py", "**/*.md")
            directory: Directory to search in
            recursive: Whether to search recursively
            max_results: Maximum number of results to return
            
        Returns:
            ToolResult with matching file paths
            
        Raises:
            ToolError: If search fails
        """
        try:
            path = Path(directory)
            
            if not path.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Directory not found: {directory}"
                )
            
            # Perform glob search
            if recursive:
                matches = list(path.rglob(pattern))
            else:
                matches = list(path.glob(pattern))
            
            # Limit results
            matches = matches[:max_results]
            
            # Sort by path
            matches.sort()
            
            # Format output
            output_lines = [str(p.relative_to(path)) for p in matches]
            output = '\n'.join(output_lines)
            
            self.logger.debug(f"Found {len(matches)} files matching '{pattern}'")
            
            return ToolResult(
                success=True,
                output=output,
                metadata={
                    "pattern": pattern,
                    "directory": str(path.absolute()),
                    "match_count": len(matches),
                    "matches": [str(p) for p in matches],
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to search with pattern '{pattern}': {e}")
            raise ToolError(self.name, str(e))


class GrepSearchTool(BaseTool):
    """Tool for searching file contents using regex patterns."""
    
    def __init__(self):
        """Initialize the grep search tool."""
        super().__init__(name="grep_search")
    
    async def execute(
        self,
        pattern: str,
        directory: str = ".",
        file_pattern: str = "*",
        case_sensitive: bool = True,
        max_results: int = 50,
    ) -> ToolResult:
        """Search file contents for pattern.
        
        Args:
            pattern: Regex pattern to search for
            directory: Directory to search in
            file_pattern: Glob pattern for files to search (e.g., "*.py")
            case_sensitive: Whether search is case-sensitive
            max_results: Maximum number of matches to return
            
        Returns:
            ToolResult with matching lines and file locations
            
        Raises:
            ToolError: If search fails
        """
        try:
            path = Path(directory)
            
            if not path.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Directory not found: {directory}"
                )
            
            # Compile regex
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                regex = re.compile(pattern, flags)
            except re.error as e:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Invalid regex pattern: {e}"
                )
            
            # Find files to search
            files = list(path.rglob(file_pattern))
            
            matches = []
            
            for file_path in files:
                if not file_path.is_file():
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if regex.search(line):
                                matches.append({
                                    "file": str(file_path.relative_to(path)),
                                    "line_number": line_num,
                                    "line": line.rstrip(),
                                })
                                
                                if len(matches) >= max_results:
                                    break
                except (PermissionError, UnicodeDecodeError):
                    continue
                
                if len(matches) >= max_results:
                    break
            
            # Format output
            output_lines = []
            for match in matches:
                output_lines.append(
                    f"{match['file']}:{match['line_number']}: {match['line']}"
                )
            
            output = '\n'.join(output_lines)
            
            self.logger.debug(f"Found {len(matches)} matches for pattern '{pattern}'")
            
            return ToolResult(
                success=True,
                output=output,
                metadata={
                    "pattern": pattern,
                    "directory": str(path.absolute()),
                    "match_count": len(matches),
                    "matches": matches,
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to grep search for '{pattern}': {e}")
            raise ToolError(self.name, str(e))
