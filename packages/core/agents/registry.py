"""Agent registry for managing multiple PydanticAI agents.

This module provides a centralized registry for creating, storing, and
retrieving specialized agents.
"""

from typing import Dict, Optional, List
from pydantic_ai import Agent
from ..utils.logger import get_logger
from ..utils.errors import AgentError

logger = get_logger(__name__)


class AgentRegistry:
    """Registry for managing PydanticAI agents.
    
    This provides a centralized location for creating and accessing
    specialized agents throughout the application.
    """
    
    def __init__(self):
        """Initialize the agent registry."""
        self._agents: Dict[str, Agent] = {}
        logger.debug("Initialized agent registry")
    
    def register(self, name: str, agent: Agent) -> None:
        """Register an agent in the registry.
        
        Args:
            name: Unique name for the agent
            agent: PydanticAI Agent instance
            
        Raises:
            AgentError: If agent name already registered
        """
        if name in self._agents:
            raise AgentError(f"Agent '{name}' is already registered")
        
        self._agents[name] = agent
        logger.info(f"Registered agent: {name}")
    
    def get(self, name: str) -> Agent:
        """Get an agent by name.
        
        Args:
            name: Name of the agent to retrieve
            
        Returns:
            Agent instance
            
        Raises:
            AgentError: If agent not found
        """
        if name not in self._agents:
            raise AgentError(
                f"Agent '{name}' not found. "
                f"Available agents: {', '.join(self.list_agents())}"
            )
        
        return self._agents[name]
    
    def list_agents(self) -> List[str]:
        """List all registered agent names.
        
        Returns:
            List of agent names
        """
        return list(self._agents.keys())
    
    def unregister(self, name: str) -> None:
        """Remove an agent from the registry.
        
        Args:
            name: Name of the agent to remove
            
        Raises:
            AgentError: If agent not found
        """
        if name not in self._agents:
            raise AgentError(f"Agent '{name}' not found")
        
        del self._agents[name]
        logger.info(f"Unregistered agent: {name}")
    
    def clear(self) -> None:
        """Clear all agents from the registry."""
        count = len(self._agents)
        self._agents.clear()
        logger.info(f"Cleared {count} agents from registry")
    
    def has_agent(self, name: str) -> bool:
        """Check if an agent is registered.
        
        Args:
            name: Name of the agent to check
            
        Returns:
            True if agent is registered
        """
        return name in self._agents


# Global agent registry instance
_global_registry: Optional[AgentRegistry] = None


def get_agent_registry() -> AgentRegistry:
    """Get or create the global agent registry.
    
    Returns:
        Shared AgentRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = AgentRegistry()
    return _global_registry
