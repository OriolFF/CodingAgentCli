"""Tests for CLI REPL."""

import pytest
from packages.cli.repl import AgentREPL


def test_repl_initialization():
    """Test REPL can be initialized."""
    repl = AgentREPL()
    
    assert repl.console is not None
    assert repl.session is not None
    assert repl.active_agent is None


def test_system_commands_defined():
    """Test system commands are defined."""
    assert "/help" in AgentREPL.COMMANDS
    assert "/agents" in AgentREPL.COMMANDS
    assert "/exit" in AgentREPL.COMMANDS
    assert "/config" in AgentREPL.COMMANDS


@pytest.mark.asyncio
async def test_help_command():
    """Test help command execution."""
    repl = AgentREPL()
    
    # Should not exit
    should_exit = await repl.handle_system_command("/help")
    assert should_exit is False


@pytest.mark.asyncio
async def test_exit_command():
    """Test exit command."""
    repl = AgentREPL()
    
    # Should exit
    should_exit = await repl.handle_system_command("/exit")
    assert should_exit is True


@pytest.mark.asyncio
async def test_unknown_command():
    """Test unknown command handling."""
    repl = AgentREPL()
    
    # Should not exit but should handle gracefully
    should_exit = await repl.handle_system_command("/unknown")
    assert should_exit is False


def test_config_display():
    """Test configuration display."""
    from packages.core.config import init_config
    init_config()
    
    repl = AgentREPL()
    # Should not raise
    repl.show_config()


def test_agents_list():
    """Test listing agents."""
    repl = AgentREPL()
    # Should not raise
    repl.list_agents()
