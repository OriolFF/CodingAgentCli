"""Custom exceptions for the agent system."""

from typing import Optional


class AgentError(Exception):
    """Base exception for all agent-related errors."""
    pass


class ModelNotAvailableError(AgentError):
    """Raised when a requested model is not available."""
    
    def __init__(self, model_name: str, provider: str, message: Optional[str] = None):
        """Initialize error.
        
        Args:
            model_name: Name of the unavailable model
            provider: Provider name
            message: Optional custom message
        """
        self.model_name = model_name
        self.provider = provider
        if message is None:
            message = f"Model '{model_name}' not available from provider '{provider}'"
        super().__init__(message)


class ToolExecutionError(AgentError):
    """Raised when a tool execution fails."""
    
    def __init__(self, tool_name: str, message: Optional[str] = None):
        """Initialize error.
        
        Args:
            tool_name: Name of the tool that failed
            message: Optional custom message
        """
        self.tool_name = tool_name
        if message is None:
            message = f"Tool '{tool_name}' execution failed"
        super().__init__(message)


class ConfigurationError(AgentError):
    """Raised when there's a configuration error."""
    pass


class ValidationError(AgentError):
    """Raised when response validation fails."""
    pass
