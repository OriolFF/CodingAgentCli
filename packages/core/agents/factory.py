"""Agent factory for creating PydanticAI agents with configuration."""

from typing import Optional
from pydantic_ai import Agent
from ..config import Config, get_config


class AgentFactory:
    """Factory for creating PydanticAI agents from configuration.
    
    This factory loads agent configurations from YAML files and creates
    properly configured PydanticAI Agent instances.
    """

    def __init__(self, config: Optional[Config] = None):
        """Initialize the agent factory.
        
        Args:
            config: Optional configuration. If not provided, uses get_config()
        """
        self.config = config or get_config()
    
    def create_agent(
        self,
        agent_name: str = "default",
        **overrides
    ) -> Agent:
        """Create a PydanticAI agent with specified configuration.
        
        Args:
            agent_name: Name of the agent configuration to use
            **overrides: Override specific configuration parameters
            
        Returns:
            Configured PydanticAI Agent instance
            
        Raises:
            ValueError: If agent configuration not found
        """
        # Get agent configuration
        agent_config = self.config.get_agent_config(agent_name)
        if not agent_config:
            raise ValueError(
                f"Agent '{agent_name}' not found in configuration. "
                f"Available agents: {list(self.config.agents.keys())}"
            )

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


def create_agent(
    agent_name: str = "default",
    config: Optional[Config] = None,
    **overrides
) -> Agent:
    """Convenience function to create an agent.
    
    Args:
        agent_name: Name of agent configuration
        config: Optional Config instance
        **overrides: Override configuration parameters
        
    Returns:
        Configured PydanticAI Agent
    """
    factory = AgentFactory(config=config)
    return factory.create_agent(agent_name, **overrides)
