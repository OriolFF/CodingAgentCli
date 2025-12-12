"""Configuration system using Pydantic Settings."""

import os
from typing import Optional, Union
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProviderConfig(BaseModel):
    """Provider-specific configuration."""
    
    ollama_base_url: str = Field(
        default="http://localhost:11434/v1",
        description="Base URL for Ollama provider"
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )


class AgentConfigSpec(BaseModel):
    """Configuration for a single agent."""
    
    model: str = Field(
        description="Model identifier (e.g., 'ollama:mistral', 'gemini-1.5-pro')"
    )
    fallback_models: list[str] = Field(
        default_factory=list,
        description="Fallback models if primary fails"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Model temperature"
    )
    system_prompt: str = Field(
        default="",
        description="System prompt for the agent"
    )
    retries: int = Field(
        default=2,
        ge=0,
        description="Number of retries on failure"
    )


class Config(BaseSettings):
    """Main configuration class."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )
    
    # Application settings
    app_name: str = Field(default="PydanticAI Agent")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    
    # Provider settings
    ollama_base_url: str = Field(default="http://localhost:11434/v1")
    openai_api_key: Optional[str] = Field(default=None)
    
    # Default model settings
    default_model: str = Field(
        default="ollama:mistral",
        description="Default model to use"
    )
    default_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Default temperature for generation"
    )
    default_retries: int = Field(default=2)
    
    # Agent-specific model settings (loaded from .env)
    coordinator_model: Optional[str] = Field(default=None)
    coordinator_temperature: Optional[float] = Field(default=None)
    
    codebase_model: Optional[str] = Field(default=None)
    codebase_temperature: Optional[float] = Field(default=None)
    
    file_editor_model: Optional[str] = Field(default=None)
    file_editor_temperature: Optional[float] = Field(default=None)
    
    testing_model: Optional[str] = Field(default=None)
    testing_temperature: Optional[float] = Field(default=None)
    
    documentation_model: Optional[str] = Field(default=None)
    documentation_temperature: Optional[float] = Field(default=None)
    
    refactoring_model: Optional[str] = Field(default=None)
    refactoring_temperature: Optional[float] = Field(default=None)
    
    # Agent configurations
    agents: dict[str, AgentConfigSpec] = Field(
        default_factory=dict,
        description="Agent configurations by name"
    )
    
    def get_agent_model(self, agent_type: str) -> str:
        """Get model for specific agent type, falling back to default."""
        model_map = {
            "coordinator": self.coordinator_model,
            "codebase": self.codebase_model,
            "file_editor": self.file_editor_model,
            "testing": self.testing_model,
            "documentation": self.documentation_model,
            "refactoring": self.refactoring_model,
        }
        return model_map.get(agent_type) or self.default_model
    
    def get_agent_temperature(self, agent_type: str) -> float:
        """Get temperature for specific agent type, falling back to default."""
        temp_map = {
            "coordinator": self.coordinator_temperature,
            "codebase": self.codebase_temperature,
            "file_editor": self.file_editor_temperature,
            "testing": self.testing_temperature,
            "documentation": self.documentation_temperature,
            "refactoring": self.refactoring_temperature,
        }
        temp = temp_map.get(agent_type)
        return temp if temp is not None else self.default_temperature
    
    def get_model_instance(self, agent_type: str) -> str:
        """Get model identifier for specific agent type.
        
        For Ollama models (those with 'ollama:' prefix), returns the model string
        with the OLLAMA_BASE_URL environment variable properly configured.
        For other providers, returns the string identifier for PydanticAI's auto-detection.
        
        Args:
            agent_type: Type of agent (e.g., 'file_editor', 'coordinator')
            
        Returns:
            Model string identifier
        """
        from ..utils.logger import get_logger
        logger = get_logger(__name__)
        
        model_str = self.get_agent_model(agent_type)
        
        # Check if this is an Ollama model and log accordingly
        if model_str.startswith("ollama:"):
            # Extract model name (e.g., "ollama:llama3.1" -> "llama3.1")
            model_name = model_str.split(":", 1)[1]
            
            logger.info(
                f"✓ Using Ollama model for {agent_type}: {model_name} "
                f"(via {self.ollama_base_url})"
            )
        else:
            # For non-Ollama providers
            logger.debug(f"Using {model_str} for {agent_type}")
        
        return model_str
    
    def get_agent_config(self, name: str) -> Optional[AgentConfigSpec]:
        """Get configuration for a specific agent."""
        return self.agents.get(name)
    
    def model_post_init(self, __context: any) -> None:
        """Initialize after model creation."""
        # Set environment variables for PydanticAI providers
        os.environ.setdefault("OLLAMA_BASE_URL", self.ollama_base_url)
        if self.openai_api_key:
            os.environ.setdefault("OPENAI_API_KEY", self.openai_api_key)
        
        # Add default agent if none configured
        if not self.agents:
            self.agents["default"] = AgentConfigSpec(
                model=self.default_model,
                temperature=self.default_temperature,
                system_prompt="You are a helpful AI assistant.",
            )


# Global config instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create the global configuration instance.
    
    This should be called early in the application lifecycle to ensure
    OLLAMA_BASE_URL and other environment variables are set before
    any agents are instantiated.
    
    Returns:
        The global Config instance
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


def init_config() -> Config:
    """Initialize the configuration system.
    
    Call this at application startup to ensure all environment
    variables are properly set.
    
    Returns:
        The initialized Config instance
    """
    return get_config()
