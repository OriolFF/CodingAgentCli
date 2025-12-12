"""Configuration package initialization.

Call init_config() at application startup to ensure environment
variables are set before creating agents.
"""

from .config import Config, get_config, init_config, AgentConfigSpec

__all__ = [
    "Config",
    "get_config",
    "init_config",
    "AgentConfigSpec",
]
