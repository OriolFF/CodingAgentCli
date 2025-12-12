"""Tests for tool approval system."""

import pytest
from packages.core.tools.approval import (
    ToolApprovalSystem,
    ApprovalDecision,
    get_approval_system,
    tool_requires_approval,
)
from packages.core.tools.base import BaseTool, ToolResult


class DummyTool(BaseTool):
    """Dummy tool for testing approval."""
    
    async def execute(self, action: str = "test") -> ToolResult:
        """Execute dummy action."""
        return ToolResult(
            success=True,
            output=f"Executed: {action}",
            metadata={"action": action}
        )


@pytest.mark.asyncio
async def test_approval_system_default_approved():
    """Test that tools are approved by default when no callback set."""
    system = ToolApprovalSystem()
    tool = DummyTool(name="test_tool")
    
    result = await system.execute_with_approval(tool, action="test")
    
    assert result.success is True
    assert "Executed" in result.output


@pytest.mark.asyncio
async def test_approval_system_callback_approved():
    """Test approval with callback that approves."""
    system = ToolApprovalSystem()
    
    async def approve_callback(tool_name: str, params: dict) -> ApprovalDecision:
        return ApprovalDecision.APPROVED
    
    system.set_approval_callback(approve_callback)
    tool = DummyTool(name="test_tool")
    
    result = await system.execute_with_approval(tool, action="test")
    
    assert result.success is True


@pytest.mark.asyncio
async def test_approval_system_callback_rejected():
    """Test approval with callback that rejects."""
    system = ToolApprovalSystem()
    
    async def reject_callback(tool_name: str, params: dict) -> ApprovalDecision:
        return ApprovalDecision.REJECTED
    
    system.set_approval_callback(reject_callback)
    tool = DummyTool(name="test_tool")
    
    result = await system.execute_with_approval(tool, action="test")
    
    assert result.success is False
    assert "rejected" in result.error.lower()


@pytest.mark.asyncio
async def test_approval_system_always_approve():
    """Test always approve decision."""
    system = ToolApprovalSystem()
    call_count = 0
    
    async def always_approve_callback(tool_name: str, params: dict) -> ApprovalDecision:
        nonlocal call_count
        call_count += 1
        return ApprovalDecision.ALWAYS_APPROVE
    
    system.set_approval_callback(always_approve_callback)
    tool = DummyTool(name="test_tool")
    
    # First call should trigger callback
    await system.execute_with_approval(tool, action="test1")
    assert call_count == 1
    
    # Second call should not trigger callback (always approved)
    await system.execute_with_approval(tool, action="test2")
    assert call_count == 1  # Not incremented


@pytest.mark.asyncio
async def test_approval_system_clear_always_approved():
    """Test clearing always-approved tools."""
    system = ToolApprovalSystem()
    
    async def always_approve_callback(tool_name: str, params: dict) -> ApprovalDecision:
        return ApprovalDecision.ALWAYS_APPROVE
    
    system.set_approval_callback(always_approve_callback)
    tool = DummyTool(name="test_tool")
    
    # Approve once
    await system.execute_with_approval(tool, action="test")
    assert "test_tool" in system.always_approved_tools
    
    # Clear
    system.clear_always_approved()
    assert len(system.always_approved_tools) == 0


def test_tool_requires_approval():
    """Test tool approval requirements."""
    assert tool_requires_approval("write_file") is True
    assert tool_requires_approval("execute_shell") is True
    assert tool_requires_approval("read_file") is False
    assert tool_requires_approval("safe_tool") is False


def test_get_global_approval_system():
    """Test global approval system singleton."""
    system1 = get_approval_system()
    system2 = get_approval_system()
    
    assert system1 is system2  # Same instance
