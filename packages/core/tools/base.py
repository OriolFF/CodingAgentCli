"""Base classes for tool implementation.

This module provides the foundation for building tools that can be used
by PydanticAI agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from pydantic import BaseModel, Field
from ..utils import get_logger

logger = get_logger(__name__)


class ToolResult(BaseModel):
    """Result from a tool execution.
    
    This standardizes tool outputs and makes them easy to validate.
    """
    
    success: bool = Field(description="Whether the tool executed successfully")
    output: Any = Field(description="Tool output data")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ToolError(Exception):
    """Exception raised when a tool fails to execute."""
    
    def __init__(self, tool_name: str, message: str):
        """Initialize tool error.
        
        Args:
            tool_name: Name of the tool that failed
            message: Error message
        """
        self.tool_name = tool_name
        super().__init__(f"Tool '{tool_name}' failed: {message}")


class BaseTool(ABC):
    """Base class for all tools.
    
    Tools should inherit from this class and implement the execute method.
    This provides a consistent interface for tool execution and error handling.
    """
    
    def __init__(self, name: Optional[str] = None):
        """Initialize the tool.
        
        Args:
            name: Optional custom name for the tool
        """
        self.name = name or self.__class__.__name__
        self.logger = get_logger(f"{__name__}.{self.name}")
    
    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with the given arguments.
        
        This method must be implemented by all tool subclasses.
        
        Args:
            **kwargs: Tool-specific arguments
            
        Returns:
            ToolResult with execution results
            
        Raises:
            ToolError: If the tool execution fails
        """
        pass
    
    def execute_sync(self, **kwargs: Any) -> ToolResult:
        """Synchronous wrapper for execute.
        
        Args:
            **kwargs: Tool-specific arguments
            
        Returns:
            ToolResult with execution results
        """
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.execute(**kwargs))
    
    def __str__(self) -> str:
        """String representation of the tool."""
        return f"{self.name}"
    
    def __repr__(self) -> str:
        """Detailed representation of the tool."""
        return f"<{self.__class__.__name__}(name='{self.name}')>"
