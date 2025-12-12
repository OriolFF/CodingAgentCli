"""Interactive REPL for PydanticAI agents.

This module provides an interactive command-line interface for interacting
with specialized agents.
"""

import asyncio
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import WordCompleter
from pathlib import Path

from ..core.agents.delegation import delegate_task, DelegationResult
from ..core.config import init_config
from ..core.utils.logger import get_logger

logger = get_logger(__name__)


class AgentREPL:
    """Interactive REPL for agent interaction."""
    
    # System commands
    COMMANDS = {
        "/help": "Show help message",
        "/agents": "List available agents",
        "/use": "Switch active agent",
        "/clear": "Clear screen",
        "/history": "Show command history",
        "/config": "Show configuration",
        "/exit": "Exit CLI",
    }
    
    def __init__(self):
        """Initialize the REPL."""
        self.console = Console()
        self.active_agent = None
        self.history_file = Path.home() / ".pydantic_agent_history"
        
        # Create completer with comprehensive suggestions
        from prompt_toolkit.completion import WordCompleter, PathCompleter, merge_completers
        
        # System commands
        command_words = list(self.COMMANDS.keys())
        
        # Common agent action words
        action_words = [
            "analyze", "analyse", "check", "review", "examine",
            "generate", "create", "make", "build",
            "refactor", "improve", "optimize", "clean",
            "edit", "modify", "change", "update",
            "test", "verify", "validate",
            "explain", "describe", "what", "how", "why",
            "list", "show", "display", "find", "search",
            "document", "docs", "readme",
        ]
        
        # File and directory common patterns
        common_paths = [
            "packages/", "packages/core/", "packages/cli/",
            "packages/core/agents/", "packages/core/tools/",
            "packages/core/config/", "tests/", "docs/",
            ".py", ".md", ".yaml", ".toml",
        ]
        
        # Combine completers
        word_completer = WordCompleter(
            command_words + action_words + common_paths,
            ignore_case=True,
            sentence=True  # Allow multi-word completion
        )
        
        # Path completer for file paths
        path_completer = PathCompleter(
            expanduser=True,
            only_directories=False,
        )
        
        # Merge both completers
        self.completer = merge_completers([word_completer, path_completer])
        
        # Create prompt session with enhanced completion
        self.session = PromptSession(
            history=FileHistory(str(self.history_file)),
            completer=self.completer,
            complete_while_typing=True,  # Show suggestions while typing
        )
        
        logger.info("REPL initialized")
    
    def show_welcome(self):
        """Display welcome message."""
        welcome = """
# PydanticAI Agent CLI

Welcome to the interactive agent terminal!

Type `/help` for available commands or start chatting with agents directly.

**Quick start**:
- `analyze config.py` - Analyze code
- `generate tests for my_module.py` - Create tests
- `refactor main.py` - Improve code quality
- `/agents` - List all available agents
"""
        self.console.print(Panel(
            Markdown(welcome),
            title="✨ Agent CLI",
            border_style="blue"
        ))
    
    def show_help(self):
        """Show help information."""
        help_text = """
## System Commands

| Command | Description |
|---------|-------------|
| `/help` | Show this help message |
| `/agents` | List available specialized agents |
| `/use <agent>` | Switch to a specific agent |
| `/clear` | Clear the screen |
| `/history` | Show command history |
| `/config` | Display current configuration |
| `/exit` | Exit the CLI |

## Agent Commands (no prefix needed)

Just type natural language commands:

- `analyze <file>` - Analyze code structure
- `edit <instruction>` - Modify files
- `generate tests for <file>` - Create test cases
- `docs <target>` - Generate documentation
- `refactor <file>` - Improve code quality

## Examples

```
analyze packages/core/config/config.py
generate comprehensive tests for tools module
refactor delegation.py to improve readability
create README for this project
```

The coordinator agent will automatically route your request to the appropriate specialist!
"""
        self.console.print(Markdown(help_text))
    
    def list_agents(self):
        """List available agents."""
        from rich.table import Table
        
        table = Table(title="Available Specialized Agents")
        table.add_column("Agent", style="cyan")
        table.add_column("Purpose", style="green")
        table.add_column("Tools", style="yellow")
        
        agents_info = [
            ("Coordinator", "Routes tasks to specialists", "All agents as tools"),
            ("Codebase Investigator", "Analyze code structure", "ls, glob, grep, read"),
            ("File Editor", "Precise code modifications", "read, write, edit"),
            ("Testing Agent", "Generate and run tests", "read, write, pytest"),
            ("Documentation Agent", "Create docs and READMEs", "read, write, ls"),
            ("Refactoring Agent", "Improve code quality", "read, edit, grep"),
        ]
        
        for name, purpose, tools in agents_info:
            table.add_row(name, purpose, tools)
        
        self.console.print(table)
    
    def clear_screen(self):
        """Clear the terminal screen."""
        self.console.clear()
    
    def show_history(self):
        """Show command history."""
        if self.history_file.exists():
            with open(self.history_file) as f:
                history = f.readlines()
                for i, line in enumerate(history[-20:], 1):  # Last 20 commands
                    self.console.print(f"{i}. {line.strip()}")
        else:
            self.console.print("[yellow]No command history yet[/yellow]")
    
    def show_config(self):
        """Show current configuration."""
        from ..core.config import get_config
        
        config = get_config()
        
        from rich.table import Table
        table = Table(title="Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("App Name", config.app_name)
        table.add_row("Debug", str(config.debug))
        table.add_row("Log Level", config.log_level)
        table.add_row("Default Model", config.default_model)
        table.add_row("Ollama URL", config.ollama_base_url)
        
        self.console.print(table)
    
    async def handle_system_command(self, command: str) -> bool:
        """Handle system commands (those starting with /).
        
        Args:
            command: Command to handle
            
        Returns:
            True if should exit, False otherwise
        """
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == "/help":
            self.show_help()
        elif cmd == "/agents":
            self.list_agents()
        elif cmd == "/clear":
            self.clear_screen()
        elif cmd == "/history":
            self.show_history()
        elif cmd == "/config":
            self.show_config()
        elif cmd == "/exit":
            self.console.print("[yellow]Goodbye![/yellow]")
            return True
        elif cmd == "/use":
            if len(parts) > 1:
                agent_name = parts[1]
                self.console.print(f"[yellow]Switching to {agent_name} agent (not yet implemented)[/yellow]")
            else:
                self.console.print("[red]Usage: /use <agent_name>[/red]")
        else:
            self.console.print(f"[red]Unknown command: {cmd}[/red]")
            self.console.print("[yellow]Type /help for available commands[/yellow]")
        
        return False
    
    async def delegate_to_agent(self, command: str):
        """Delegate command to appropriate agent.
        
        Args:
            command: User command to execute
        """
        from rich.spinner import Spinner
        from rich.live import Live
        
        # Show thinking indicator
        with Live(Spinner("dots", text="Processing..."), console=self.console):
            try:
                result = await delegate_task(command)
                
                # Display result
                self.display_result(result)
                
            except Exception as e:
                logger.error(f"Error executing command: {e}")
                self.console.print(f"[red]Error: {str(e)}[/red]")
    
    def display_result(self, result: DelegationResult):
        """Display delegation result with rich formatting.
        
        Args:
            result: Result to display
        """
        from rich.syntax import Syntax
        from rich.table import Table
        
        # Show which agents were used
        if result.agents_used:
            agents_str = ", ".join(result.agents_used)
            self.console.print(f"[dim]🤖 Agents: {agents_str}[/dim]\n")
        
        # Check if result contains code blocks
        if "```" in result.result:
            # Extract and syntax highlight code blocks
            parts = result.result.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    # Regular text
                    if part.strip():
                        self.console.print(part)
                else:
                    # Code block
                    lines = part.split("\n")
                    lang = lines[0].strip() if lines else "python"
                    code = "\n".join(lines[1:]) if len(lines) > 1 else part
                    
                    syntax = Syntax(code, lang, theme="monokai", line_numbers=True)
                    self.console.print(syntax)
        else:
            # Show result in panel
            panel = Panel(
                result.result,
                title="✅ Success" if result.success else "❌ Error",
                border_style="green" if result.success else "red",
                padding=(1, 2)
            )
            self.console.print(panel)
        
        # Show summary if different from result
        if result.task_summary and result.task_summary != result.result[:200]:
            self.console.print(f"\n[dim italic]Summary: {result.task_summary}[/dim italic]")

    
    async def process_input(self, user_input: str) -> bool:
        """Process user input.
        
        Args:
            user_input: User's input command
            
        Returns:
            True if should exit, False otherwise
        """
        user_input = user_input.strip()
        
        if not user_input:
            return False
        
        # Handle system commands
        if user_input.startswith("/"):
            return await self.handle_system_command(user_input)
        
        # Delegate to agents
        await self.delegate_to_agent(user_input)
        
        return False
    
    async def run(self):
        """Run the REPL loop."""
        self.show_welcome()
        
        while True:
            try:
                # Get user input
                user_input = await asyncio.wait_for(
                    asyncio.to_thread(self.session.prompt, "agent> "),
                    timeout=None
                )
                
                # Process input
                should_exit = await self.process_input(user_input)
                if should_exit:
                    break
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use /exit to quit[/yellow]")
                continue
            except EOFError:
                break
            except Exception as e:
                logger.error(f"REPL error: {e}")
                self.console.print(f"[red]Error: {str(e)}[/red]")


async def main():
    """Main entry point for CLI."""
    # Initialize configuration
    init_config()
    
    # Create and run REPL
    repl = AgentREPL()
    await repl.run()


def cli_main():
    """Synchronous entry point for CLI."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
