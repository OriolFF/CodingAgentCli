"""Configuration package initialization.

This ensures configuration is loaded early and environment variables
are set before any agents are created.
"""

from .config import Config, get_config, init_config, AgentConfigSpec, ProviderConfig

# Initialize config at import time to set environment variables
init_config()

__all__ = [
    "Config",
    "get_config",
    "init_config",
    "AgentConfigSpec",
    "ProviderConfig",
]
