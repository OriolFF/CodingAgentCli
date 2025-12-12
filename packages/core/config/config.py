"""Main configuration classes using Pydantic."""

from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentConfig(BaseModel):
    """Configuration for a single agent."""

    model: str = Field(
        description="Model identifier (e.g., 'ollama:mistral', 'gemini-1.5-pro')"
    )
    fallback_models: list[str] = Field(
        default_factory=list, description="Fallback models if primary fails"
    )
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Model temperature")
    max_tokens: int = Field(default=4096, gt=0, description="Maximum tokens for response")
    system_prompt: str = Field(default="", description="System prompt for the agent")
    timeout: int = Field(default=300, gt=0, description="Timeout in seconds")
    retries: int = Field(default=2, ge=0, description="Number of retries on failure")


class Config(BaseSettings):
    """Main application configuration with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="GEMINI_AGENT_",
        case_sensitive=False,
        extra="ignore",
    )

    # Global settings
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    default_model: str = Field(default="ollama:mistral", description="Default model to use")

    # Agent configurations
    agents: dict[str, AgentConfig] = Field(
        default_factory=dict, description="Agent configurations by name"
    )

    def get_agent_config(self, name: str) -> Optional[AgentConfig]:
        """Get configuration for a specific agent."""
        return self.agents.get(name)

    def model_post_init(self, __context: any) -> None:
        """Validate configuration after initialization."""
        if not self.agents:
            # Add default agent if none configured
            self.agents["default"] = AgentConfig(
                model=self.default_model,
                system_prompt="You are a helpful AI assistant.",
            )
