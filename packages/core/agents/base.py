"""Base agent implementation using PydanticAI.

This module demonstrates the basic usage of PydanticAI with Ollama.
"""

import os
from pydantic_ai import Agent


# Set Ollama base URL via environment variable (if not already set)
if "OLLAMA_BASE_URL" not in os.environ:
    os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434/v1"

# Create first PydanticAI agent with Ollama
# Requires DEFAULT_MODEL to be set in .env - no fallback
default_model = os.getenv("DEFAULT_MODEL")
if not default_model:
    raise ValueError(
        "\n❌ DEFAULT_MODEL environment variable is required but not set!\n\n"
        "Solution:\n"
        "1. Add DEFAULT_MODEL to your .env file:\n"
        "   DEFAULT_MODEL=ollama:llama3.1:8b-instruct-q8_0\n\n"
        "2. Or export it:\n"
        "   export DEFAULT_MODEL=ollama:llama3.1:8b-instruct-q8_0\n"
    )

simple_agent = Agent(
    default_model,
    system_prompt="You are a helpful assistant. Provide concise, accurate answers.",
    retries=2,
)


async def test_agent_async(question: str) -> str:
    """Test agent with async call.

    Args:
        question: Question to ask the agent

    Returns:
        String answer from the agent

    Raises:
        RuntimeError: If Ollama is not running or model not available
    """
    try:
        result = await simple_agent.run(question)
        return result.output
    except Exception as e:
        raise RuntimeError(
            f"Failed to run agent. Is Ollama running? Error: {e}"
        ) from e


def test_agent_sync(question: str) -> str:
    """Test agent with synchronous call.

    Args:
        question: Question to ask the agent

    Returns:
        String answer from the agent

    Raises:
        RuntimeError: If Ollama is not running or model not available
    """
    try:
        result = simple_agent.run_sync(question)
        return result.output
    except Exception as e:
        raise RuntimeError(
            f"Failed to run agent. Is Ollama running? Error: {e}"
        ) from e

