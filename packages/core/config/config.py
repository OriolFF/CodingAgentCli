"""Configuration system using Pydantic Settings."""

import os
from typing import Optional
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
    max_tokens: int = Field(
        default=4096,
        gt=0,
        description="Maximum tokens for response"
    )
    system_prompt: str = Field(
        default="",
        description="System prompt for the agent"
    )
    timeout: int = Field(
        default=300,
        gt=0,
        description="Timeout in seconds"
    )
    retries: int = Field(
        default=2,
        ge=0,
        description="Number of retries on failure"
    )


class Config(BaseSettings):
    """Main application configuration with environment variable support.
    
    Loads from:
    1. Environment variables (highest priority)
    2. .env file
    3. Default values (lowest priority)
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application settings
    app_name: str = Field(default="pydantic-agent", description="Application name")
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Provider settings (loaded from env vars)
    ollama_base_url: str = Field(
        default="http://localhost:11434/v1",
        description="Base URL for Ollama provider"
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    
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
    
    # Agent configurations
    agents: dict[str, AgentConfigSpec] = Field(
        default_factory=dict,
        description="Agent configurations by name"
    )
    
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
