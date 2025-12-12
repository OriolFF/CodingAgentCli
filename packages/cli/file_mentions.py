"""File mention support for CLI.

Enables @filename syntax for file references with auto-completion.
"""

import re
from pathlib import Path
from typing import List, Tuple, Optional
from ..core.utils.logger import get_logger

logger = get_logger(__name__)


class FileMentionParser:
    """Parse and resolve @file mentions in user input."""
    
    # Pattern to match @filename references
    MENTION_PATTERN = re.compile(r'@([\w\-./]+(?:\.\w+)?)')
    
    @classmethod
    def extract_mentions(cls, text: str) -> List[str]:
        """Extract all @file mentions from text.
        
        Args:
            text: Input text with potential @mentions
            
        Returns:
            List of file paths mentioned
            
        Example:
            >>> extract_mentions("analyze @config.py and @utils.py")
            ['config.py', 'utils.py']
        """
        matches = cls.MENTION_PATTERN.findall(text)
        return matches
    
    @classmethod
    def resolve_file_path(cls, mention: str, search_paths: Optional[List[str]] = None) -> Optional[Path]:
        """Resolve a file mention to an actual path.
        
        Args:
            mention: File mention (without @)
            search_paths: Optional list of directories to search
            
        Returns:
            Resolved Path or None if not found
        """
        if search_paths is None:
            search_paths = [
                ".",
                "packages",
                "packages/core",
                "packages/core/agents",
                "packages/core/tools",
                "packages/cli",
                "tests",
                "docs",
            ]
        
        # Try direct path first
        direct_path = Path(mention)
        if direct_path.exists():
            return direct_path
        
        # Search in common directories
        for search_dir in search_paths:
            full_path = Path(search_dir) / mention
            if full_path.exists():
                return full_path
        
        # Try finding by basename
        for search_dir in search_paths:
            search_path = Path(search_dir)
            if search_path.exists():
                # Look for files with matching basename
                for file in search_path.rglob(f"*{mention}"):
                    if file.is_file():
                        return file
        
        return None
    
    @classmethod
    def read_file_content(cls, file_path: Path, max_lines: int = 500) -> str:
        """Read file content with line limit.
        
        Args:
            file_path: Path to file
            max_lines: Maximum lines to read
            
        Returns:
            File content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if len(lines) > max_lines:
                    content = ''.join(lines[:max_lines])
                    content += f"\n... [truncated {len(lines) - max_lines} lines]"
                else:
                    content = ''.join(lines)
                return content
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return f"[Error reading file: {e}]"
    
    @classmethod
    def process_mentions(cls, text: str) -> Tuple[str, str]:
        """Process all @mentions in text and extract context.
        
        Args:
            text: Input text with @mentions
            
        Returns:
            Tuple of (cleaned_text, file_context)
            
        Example:
            >>> text = "analyze @config.py for issues"
            >>> clean, ctx = process_mentions(text)
            >>> print(clean)
            "analyze config.py for issues"
            >>> print(ctx)
            "Referenced files:\n=== config.py ===\n<content>"
        """
        mentions = cls.extract_mentions(text)
        
        if not mentions:
            return text, ""
        
        # Build file context
        context_parts = ["Referenced files:"]
        resolved_mentions = []
        
        for mention in mentions:
            file_path = cls.resolve_file_path(mention)
            if file_path:
                content = cls.read_file_content(file_path)
                context_parts.append(f"\n=== {file_path} ===")
                context_parts.append(content)
                resolved_mentions.append((mention, file_path))
                logger.info(f"Resolved @{mention} to {file_path}")
            else:
                context_parts.append(f"\n=== {mention} (NOT FOUND) ===")
                logger.warning(f"Could not resolve @{mention}")
        
        # Clean the text - replace @mentions with just the filename
        cleaned_text = text
        for mention, resolved_path in resolved_mentions:
            cleaned_text = cleaned_text.replace(f"@{mention}", str(resolved_path))
        
        file_context = "\n".join(context_parts) if len(context_parts) > 1 else ""
        
        return cleaned_text, file_context


def get_project_files(extensions: Optional[List[str]] = None) -> List[str]:
    """Get list of project files for completion.
    
    Args:
        extensions: Optional list of extensions to filter (e.g., ['.py', '.md'])
        
    Returns:
        List of file paths relative to project root
    """
    if extensions is None:
        extensions = ['.py', '.md', '.yaml', '.yml', '.toml', '.txt', '.json']
    
    files = []
    search_dirs = ['packages', 'tests', 'docs', 'config']
    
    for search_dir in search_dirs:
        search_path = Path(search_dir)
        if search_path.exists():
            for ext in extensions:
                for file_path in search_path.rglob(f"*{ext}"):
                    if file_path.is_file():
                        # Add relative path
                        rel_path = str(file_path)
                        files.append(rel_path)
                        # Also add just filename for convenience
                        files.append(file_path.name)
    
    return sorted(set(files))
