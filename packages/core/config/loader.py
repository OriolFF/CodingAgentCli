"""YAML configuration file loader."""

from pathlib import Path
from typing import Any
import yaml
from .config import Config, AgentConfig


def load_config_from_yaml(path: str | Path) -> Config:
    """Load configuration from YAML file.

    Args:
        path: Path to YAML configuration file

    Returns:
        Config object with loaded settings

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    # Convert agent configs
    if "agents" in data:
        agents_dict = {}
        for name, agent_data in data["agents"].items():
            agents_dict[name] = AgentConfig(**agent_data)
        data["agents"] = agents_dict

    return Config(**data)


def save_config_to_yaml(config: Config, path: str | Path) -> None:
    """Save configuration to YAML file.

    Args:
        config: Config object to save
        path: Path where to save the YAML file
    """
    path = Path(path)

    # Convert to dict
    data: dict[str, Any] = {
        "debug": config.debug,
        "log_level": config.log_level,
        "default_model": config.default_model,
        "agents": {},
    }

    # Convert agent configs
    for name, agent_config in config.agents.items():
        data["agents"][name] = agent_config.model_dump(exclude_defaults=True)

    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write YAML
    with open(path, "w") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
