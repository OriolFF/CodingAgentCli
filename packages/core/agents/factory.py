"""Agent factory for creating agents from configuration."""

from typing import Optional
from pydantic_ai import Agent
from ..config import Config, load_config_from_yaml


class AgentFactory:
    """Factory for creating PydanticAI agents from configuration.
    
    This factory loads agent configurations from YAML files and creates
    properly configured PydanticAI Agent instances.
    """

    def __init__(self, config: Optional[Config] = None):
        """Initialize the factory.
        
        Args:
            config: Configuration object. If None, loads from default location.
        """
        self.config = config or load_config_from_yaml("config/agents.yaml")

    def create_agent(self, name: str = "default") -> Agent:
        """Create an agent from configuration.
        
        Args:
            name: Name of the agent configuration to use
            
        Returns:
            Configured PydanticAI Agent instance
            
        Raises:
            KeyError: If agent configuration not found
        """
        agent_config = self.config.get_agent_config(name)
        if agent_config is None:
            raise KeyError(f"Agent configuration '{name}' not found")

        # Create agent with primary model
        # Note: Currently using text-only mode due to Ollama structured output issues
        agent = Agent(
            agent_config.model,
            system_prompt=agent_config.system_prompt,
            retries=agent_config.retries,
        )

        return agent

    def list_agents(self) -> list[str]:
        """List all available agent configurations.
        
        Returns:
            List of agent names
        """
        return list(self.config.agents.keys())


# Global factory instance
_global_factory: Optional[AgentFactory] = None


def get_agent_factory() -> AgentFactory:
    """Get or create the global agent factory instance.
    
    Returns:
        Shared AgentFactory instance
    """
    global _global_factory
    if _global_factory is None:
        _global_factory = AgentFactory()
    return _global_factory


def create_agent(name: str = "default") -> Agent:
    """Convenience function to create an agent.
    
    Args:
        name: Name of the agent configuration
        
    Returns:
        Configured agent instance
    """
    return get_agent_factory().create_agent(name)
