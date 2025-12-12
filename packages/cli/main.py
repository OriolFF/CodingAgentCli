"""CLI entry point for PydanticAI agents."""

import click
from .repl import cli_main


@click.group()
@click.version_option(version="0.1.0", prog_name="pydantic-agent")
def cli():
    """PydanticAI Agent CLI - Interact with specialized AI agents."""
    pass


@cli.command()
def repl():
    """Start interactive REPL."""
    cli_main()


@cli.command()
@click.argument("command", nargs=-1)
def run(command):
    """Run a single command."""
    import asyncio
    from .repl import AgentREPL
    from ..core.config import init_config
    
    init_config()
    
    command_str = " ".join(command)
    
    async def execute():
        repl = AgentREPL()
        await repl.delegate_to_agent(command_str)
    
    asyncio.run(execute())


@cli.command()
def agents():
    """List available agents."""
    from .repl import AgentREPL
    
    repl = AgentREPL()
    repl.list_agents()


if __name__ == "__main__":
    cli()
