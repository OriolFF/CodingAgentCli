"""Model-specific configuration for Ollama models.

This module contains context window sizes, temperature settings, and other
model-specific parameters that affect code generation quality.
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    num_ctx: int          # Context window size (tokens)
    num_predict: int      # Max output tokens (-1 = unlimited)
    temperature: float    # Sampling temperature (0.0 = deterministic, 1.0 = creative)
    description: str      # Model description/notes


# Model-specific configurations
# Context sizes based on model capabilities and testing
MODEL_CONFIGS: Dict[str, ModelConfig] = {
    # gpt-oss:20b - Excellent for complex code generation
    # Supports 128K context, using 32K for optimal performance
    "gpt-oss:20b": ModelConfig(
        num_ctx=32768,
        num_predict=-1,
        temperature=0.7,
        description="Large context for complex applications, complete code generation"
    ),
    
    # qwen2.5-coder:14b - Best general-purpose code generator
    # Supports large context, good for multi-file projects
    "qwen2.5-coder:14b": ModelConfig(
        num_ctx=32768,
        num_predict=-1,
        temperature=0.7,
        description="Excellent for complete code generation, large projects"
    ),
    
    # codestral - Optimized for code completion (not full generation)
    # Uses smaller context as it's designed for snippets
    "codestral": ModelConfig(
        num_ctx=8192,
        num_predict=-1,
        temperature=0.5,
        description="Code completion specialist, use for small snippets only"
    ),
    
    # llama3.1:8b - Good general model
    # Standard context size for most tasks
    "llama3.1:8b-instruct-q8_0": ModelConfig(
        num_ctx=16384,
        num_predict=-1,
        temperature=0.7,
        description="Good general-purpose model for standard tasks"
    ),
    
    # cogito:14b - Code-focused model
    # Testing showed 8K works better than larger for this model
    "cogito:14b": ModelConfig(
        num_ctx=8192,
        num_predict=-1,
        temperature=0.7,
        description="Code-focused, works best with conservative context"
    ),
    
    # mistral:latest - Coordinator model
    # Smaller context OK for coordination tasks
    "mistral": ModelConfig(
        num_ctx=8192,
        num_predict=-1,
        temperature=0.7,
        description="Good for coordination and routing tasks"
    ),
    
    # granite3.3 - IBM model
    "granite3.3": ModelConfig(
        num_ctx=8192,
        num_predict=-1,
        temperature=0.7,
        description="IBM's code model"
    ),
    
    # codellama:13b - Meta's code model
    "codellama:13b": ModelConfig(
        num_ctx=16384,
        num_predict=-1,
        temperature=0.7,
        description="Meta's CodeLlama model"
    ),
}

# Default configuration for unknown models
DEFAULT_CONFIG = ModelConfig(
    num_ctx=16384,        # Safe middle ground
    num_predict=-1,       # Unlimited output
    temperature=0.7,      # Balanced creativity
    description="Default configuration for unspecified models"
)


def get_model_config(model_name: str) -> ModelConfig:
    """Get configuration for a specific model.
    
    Args:
        model_name: Name of the model (e.g., "gpt-oss:20b", "qwen2.5-coder:14b")
        
    Returns:
        ModelConfig with appropriate settings for the model
        
    Examples:
        >>> config = get_model_config("gpt-oss:20b")
        >>> print(config.num_ctx)
        32768
        
        >>> config = get_model_config("unknown-model")
        >>> print(config.num_ctx)
        16384
    """
    # Try exact match first
    if model_name in MODEL_CONFIGS:
        return MODEL_CONFIGS[model_name]
    
    # Try partial match (e.g., "qwen2.5-coder:14b" matches "qwen2.5-coder")
    for key in MODEL_CONFIGS:
        if key in model_name or model_name.startswith(key):
            return MODEL_CONFIGS[key]
    
    # Return default for unknown models
    return DEFAULT_CONFIG


def get_context_size(model_name: str) -> int:
    """Quick accessor for context window size.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Context window size in tokens
    """
    return get_model_config(model_name).num_ctx


def get_temperature(model_name: str) -> float:
    """Quick accessor for temperature setting.
    
    Args:
        model_name: Name of the model
        
    Returns:
        Temperature value
    """
    return get_model_config(model_name).temperature


# Context size recommendations by use case
CONTEXT_SIZE_GUIDE = {
    "simple_snippet": 4096,       # Small functions, single-file utilities
    "standard_file": 8192,         # Complete single files
    "multi_file": 16384,           # Small projects with 2-5 files
    "complex_app": 32768,          # Large applications, many features
    "very_large": 65536,           # Huge codebases, extensive context needed
    "maximum": 131072,             # 128K - for models that support it
}


def print_model_configs():
    """Print all configured models and their settings (for debugging)."""
    print("=" * 80)
    print("MODEL CONFIGURATIONS")
    print("=" * 80)
    for model_name, config in MODEL_CONFIGS.items():
        print(f"\n{model_name}:")
        print(f"  Context: {config.num_ctx:,} tokens")
        print(f"  Output: {'unlimited' if config.num_predict == -1 else config.num_predict}")
        print(f"  Temperature: {config.temperature}")
        print(f"  Notes: {config.description}")
    print(f"\nDefault (unknown models): {DEFAULT_CONFIG.num_ctx:,} tokens")
    print("=" * 80)


if __name__ == "__main__":
    # Test the configuration
    print_model_configs()
    
    # Test lookups
    print("\n" + "=" * 80)
    print("TESTING MODEL LOOKUPS")
    print("=" * 80)
    
    test_models = [
        "gpt-oss:20b",
        "qwen2.5-coder:14b", 
        "codestral",
        "unknown-model:latest"
    ]
    
    for model in test_models:
        config = get_model_config(model)
        print(f"\n{model}:")
        print(f"  → num_ctx: {config.num_ctx:,}")
        print(f"  → temperature: {config.temperature}")
