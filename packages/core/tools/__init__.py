"""Tools package for PydanticAI agents.

This package contains all the tools that agents can use to interact with
the file system, execute commands, search the web, etc.
"""

from .base import BaseTool, ToolResult, ToolError
from .file_operations import ReadFileTool, WriteFileTool
from .file_edit import EditFileTool
from .search import ListDirectoryTool, GlobSearchTool, GrepSearchTool
from .shell import ShellExecutionTool
from .web import FetchUrlTool
from .memory import MemoryTool
from .approval import (
    ToolApprovalSystem,
    ApprovalDecision,
    get_approval_system,
    tool_requires_approval,
    TOOLS_REQUIRING_APPROVAL,
)

__all__ = [
    "BaseTool",
    "ToolResult",
    "ToolError",
    "ReadFileTool",
    "WriteFileTool",
    "EditFileTool",
    "ListDirectoryTool",
    "GlobSearchTool",
    "GrepSearchTool",
    "ShellExecutionTool",
    "FetchUrlTool",
    "MemoryTool",
    "ToolApprovalSystem",
    "ApprovalDecision",
    "get_approval_system",
    "tool_requires_approval",
    "TOOLS_REQUIRING_APPROVAL",
]
