"""Tool approval system for human-in-the-loop workflows.

This module provides a simple approval system for dangerous or sensitive
tool operations that require user confirmation before execution.
"""

from typing import Optional, Callable, Awaitable
from enum import Enum
from .base import BaseTool, ToolResult


class ApprovalDecision(Enum):
    """Approval decision for tool execution."""
    APPROVED = "approved"
    REJECTED = "rejected"
    ALWAYS_APPROVE = "always_approve"  # For this session


class ToolApprovalSystem:
    """System for managing tool execution approvals.
    
    This provides a way to intercept tool calls that require user approval
    before they are executed.
    """
    
    def __init__(self):
        """Initialize the approval system."""
        self.always_approved_tools: set[str] = set()
        self.approval_callback: Optional[Callable[[str, dict], Awaitable[ApprovalDecision]]] = None
    
    def set_approval_callback(
        self,
        callback: Callable[[str, dict], Awaitable[ApprovalDecision]]
    ):
        """Set the callback function for requesting approvals.
        
        The callback should be an async function that takes:
        - tool_name: str - Name of the tool requiring approval
        - params: dict - Parameters being passed to the tool
        
        And returns an ApprovalDecision.
        """
        self.approval_callback = callback
    
    async def request_approval(
        self,
        tool: BaseTool,
        **params
    ) -> ApprovalDecision:
        """Request approval for tool execution.
        
        Args:
            tool: Tool instance requiring approval
            **params: Parameters to be passed to the tool
            
        Returns:
            ApprovalDecision indicating whether to proceed
        """
        # Check if tool is always approved
        if tool.name in self.always_approved_tools:
            return ApprovalDecision.APPROVED
        
        # If no callback set, default to approved (for testing)
        if self.approval_callback is None:
            return ApprovalDecision.APPROVED
        
        # Request approval via callback
        decision = await self.approval_callback(tool.name, params)
        
        # If always approve, add to set
        if decision == ApprovalDecision.ALWAYS_APPROVE:
            self.always_approved_tools.add(tool.name)
            return ApprovalDecision.APPROVED
        
        return decision
    
    async def execute_with_approval(
        self,
        tool: BaseTool,
        **params
    ) -> ToolResult:
        """Execute a tool with approval check.
        
        Args:
            tool: Tool to execute
            **params: Parameters for tool execution
            
        Returns:
            ToolResult from tool execution or rejection
        """
        # Request approval
        decision = await self.request_approval(tool, **params)
        
        # Check decision
        if decision == ApprovalDecision.REJECTED:
            return ToolResult(
                success=False,
                output="",
                error=f"Tool execution rejected by user: {tool.name}",
                metadata={"approval_decision": decision.value}
            )
        
        # Execute tool
        return await tool.execute(**params)
    
    def clear_always_approved(self):
        """Clear the always-approved tools set."""
        self.always_approved_tools.clear()


# Global approval system instance
_global_approval_system: Optional[ToolApprovalSystem] = None


def get_approval_system() -> ToolApprovalSystem:
    """Get or create the global approval system.
    
    Returns:
        Shared ToolApprovalSystem instance
    """
    global _global_approval_system
    if _global_approval_system is None:
        _global_approval_system = ToolApprovalSystem()
    return _global_approval_system


# List of tools that typically require approval
TOOLS_REQUIRING_APPROVAL = {
    "write_file",
    "edit_file",
    "execute_shell",
    "delete_file",
    "fetch_url",  # Could download malicious content
}


def tool_requires_approval(tool_name: str) -> bool:
    """Check if a tool typically requires user approval.
    
    Args:
        tool_name: Name of the tool
        
    Returns:
        True if tool should require approval
    """
    return tool_name in TOOLS_REQUIRING_APPROVAL
